"""
EU Data Job Market Tracker — Data ingestion
----------------------------------------------------
Pulls job postings from the Adzuna API for data-related roles
across a few target countries, saves them as a local CSV, and
loads them into BigQuery (raw layer) for dbt to pick up.

Beginner notes are left in as comments on purpose — delete them
once you're comfortable with what each part does.
"""

import requests   # lets Python make web/API calls
import pandas as pd
import time
import os
from datetime import datetime, timezone
from dotenv import load_dotenv  # reads variables from a local .env file
from google.cloud import bigquery  # loads data into BigQuery

# ---------------------------------------------------------
# 1. CONFIG — credentials are read from a .env file, never hardcoded
#    Create a file called ".env" (same folder as this script) containing:
#       ADZUNA_APP_ID=your_id_here
#       ADZUNA_APP_KEY=your_key_here
#    This file is gitignored — it will never be pushed to GitHub.
#
#    BigQuery auth uses your local Application Default Credentials
#    (gcloud auth application-default login) — no key file needed.
# ---------------------------------------------------------
load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not APP_ID or not APP_KEY:
    raise ValueError(
        "Missing API credentials. Create a .env file with "
        "ADZUNA_APP_ID and ADZUNA_APP_KEY set."
    )

BQ_PROJECT = "eu-data-jobtracker"
BQ_DATASET = "job_market_raw"
BQ_TABLE = "raw_jobs"

# Countries Adzuna supports with their country codes.
# gb = UK, used partly as a proxy for "remote-friendly" postings.
# Note: 'ie' (Ireland) is NOT a supported Adzuna country code — confirmed
# via API error response. Using 'de' (Germany) instead, which also fits
# since you have intermediate German skills.
COUNTRIES = {
    "nl": "Netherlands",
    "de": "Germany",
    "es": "Spain",
    "gb": "United Kingdom",
}

# Search terms — we'll run each of these per country.
SEARCH_TERMS = [
    "data analyst",
    "data engineer",
    "data scientist",
]

RESULTS_PER_PAGE = 50   # max Adzuna allows per page
PAGES_PER_SEARCH = 2    # 2 pages x 50 = up to 100 postings per term/country

# ---------------------------------------------------------
# 2. FUNCTION — pull one page of results from Adzuna
# ---------------------------------------------------------


def fetch_jobs(country_code, search_term, page=1):
    """
    Calls the Adzuna API for a given country/search term/page.
    Returns a list of job dictionaries (raw JSON 'results').
    """
    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": search_term,
        "content-type": "application/json",
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"  ⚠️  Failed: {country_code} / {search_term} / page {page} "
              f"(status {response.status_code})")
        # show Adzuna's actual error message
        print(f"      → {response.text[:300]}")
        return []

    data = response.json()
    return data.get("results", [])


# ---------------------------------------------------------
# 3. FUNCTION — load a DataFrame into BigQuery
# ---------------------------------------------------------


def load_to_bigquery(df, project_id=BQ_PROJECT, dataset=BQ_DATASET, table=BQ_TABLE):
    """
    Appends the DataFrame into the BigQuery raw table.
    Uses Application Default Credentials picked up automatically from
    `gcloud auth application-default login` — nothing to configure here.
    """
    client = bigquery.Client(project=project_id)
    table_id = f"{project_id}.{dataset}.{table}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",  # keep accumulating each run
        autodetect=True,
    )

    print(f"\nLoading {len(df)} rows into {table_id}...")
    load_job = client.load_table_from_dataframe(
        df, table_id, job_config=job_config)
    load_job.result()  # blocks until the load finishes

    table_ref = client.get_table(table_id)
    print(f"✅ Loaded. Table now has {table_ref.num_rows} total rows.")


# ---------------------------------------------------------
# 4. MAIN LOOP — pull everything and collect into one list
# ---------------------------------------------------------
def main():
    all_jobs = []

    for country_code, country_name in COUNTRIES.items():
        for term in SEARCH_TERMS:
            print(f"Fetching '{term}' jobs in {country_name}...")

            for page in range(1, PAGES_PER_SEARCH + 1):
                results = fetch_jobs(country_code, term, page)

                if not results:
                    break  # no more results, stop paging for this term

                for job in results:
                    all_jobs.append({
                        "search_term": term,
                        "country_code": country_code,
                        "country_name": country_name,
                        "title": job.get("title"),
                        "company": job.get("company", {}).get("display_name"),
                        "location": job.get("location", {}).get("display_name"),
                        "salary_min": job.get("salary_min"),
                        "salary_max": job.get("salary_max"),
                        "contract_type": job.get("contract_type"),
                        "created": job.get("created"),
                        "description": job.get("description"),
                        "redirect_url": job.get("redirect_url"),
                        "pulled_at": datetime.now(timezone.utc).isoformat(),
                    })

                time.sleep(0.5)  # be polite to the API, avoid rate limits

    # ---------------------------------------------------------
    # 5. SAVE RESULTS — local CSV (audit trail) + BigQuery (raw layer)
    # ---------------------------------------------------------
    df = pd.DataFrame(all_jobs)

    # Drop exact duplicate postings (same title/company/location/description)
    before = len(df)
    df = df.drop_duplicates(
        subset=["title", "company", "location", "description"])
    after = len(df)
    print(f"\nRemoved {before - after} duplicate postings.")

    os.makedirs("raw", exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = f"raw/jobs_{today}.csv"
    df.to_csv(output_path, index=False)
    print(f"\n✅ Saved {len(df)} job postings to {output_path}")

    load_to_bigquery(df)


if __name__ == "__main__":
    main()
