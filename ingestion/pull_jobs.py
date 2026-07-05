"""
EU Data Job Market Tracker — Day 1: Data ingestion
----------------------------------------------------
Pulls job postings from the Adzuna API for data-related roles
across a few target countries, and saves them as a single CSV.

Beginner notes are left in as comments on purpose — delete them
once you're comfortable with what each part does.
"""

import requests   # lets Python make web/API calls
import pandas as pd
import time
import os
from datetime import datetime
from dotenv import load_dotenv  # reads variables from a local .env file

# ---------------------------------------------------------
# 1. CONFIG — credentials are read from a .env file, never hardcoded
#    Create a file called ".env" (same folder as this script) containing:
#       ADZUNA_APP_ID=your_id_here
#       ADZUNA_APP_KEY=your_key_here
#    This file is gitignored — it will never be pushed to GitHub.
# ---------------------------------------------------------
load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not APP_ID or not APP_KEY:
    raise ValueError(
        "Missing API credentials. Create a .env file with "
        "ADZUNA_APP_ID and ADZUNA_APP_KEY set."
    )

# Countries Adzuna supports with their country codes.
# gb = UK, used partly as a proxy for "remote-friendly" postings.
COUNTRIES = {
    "nl": "Netherlands",
    "ie": "Ireland",
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
        return []

    data = response.json()
    return data.get("results", [])


# ---------------------------------------------------------
# 3. MAIN LOOP — pull everything and collect into one list
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
                        "pulled_at": datetime.utcnow().isoformat(),
                    })

                time.sleep(0.5)  # be polite to the API, avoid rate limits

    # ---------------------------------------------------------
    # 4. SAVE RESULTS
    # ---------------------------------------------------------
    df = pd.DataFrame(all_jobs)

    # Drop exact duplicate postings (same title/company/location/description)
    before = len(df)
    df = df.drop_duplicates(subset=["title", "company", "location", "description"])
    after = len(df)
    print(f"\nRemoved {before - after} duplicate postings.")

    os.makedirs("raw", exist_ok=True)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = f"raw/jobs_{today}.csv"
    df.to_csv(output_path, index=False)

    print(f"\n✅ Saved {len(df)} job postings to {output_path}")


if __name__ == "__main__":
    main()
