# EU Data Job Market Tracker

A data pipeline that pulls live data analyst / data engineer / data scientist
job postings across the Netherlands, Germany, Spain, and the UK, and surfaces
which tools and skills are actually in demand right now.

**Why I built this:** I'm transitioning from an MBA background into data
analytics (bootcamp graduate, self-taught SQL/Python), and I wanted to base
my job search on real market data instead of guessing which skills to
highlight. This project doubles as market research for my own applications
and as a demonstration of the modern data stack: API ingestion → cloud
warehouse → dbt transformations → BI dashboard.

## Architecture

```
Adzuna API  →  Python (ingestion)  →  BigQuery (raw)  →  dbt (transform)  →  Looker Studio (dashboard)
```

See `docs/architecture.png` for a visual diagram.

## What it answers

- Which tools/technologies (SQL, Python, dbt, Airflow, Snowflake, etc.) show
  up most often in data job postings across these countries?
- How does skill demand differ by country — should I emphasize different
  tools when applying to NL vs. DE vs. ES vs. UK roles?
- What share of postings are tagged remote-friendly?
- Which role type (analyst/engineer/scientist) has the most postings?

## Tech stack

- **Ingestion:** Python (`requests`, `pandas`)
- **Warehouse:** Google BigQuery (free tier)
- **Transformation:** dbt-core
- **Visualization:** Looker Studio
- **Version control:** Git/GitHub

## Repo structure

```
├── ingestion/          # API pull script
├── dbt/                 # dbt project — staging + mart models, tests
├── dashboards/          # dashboard screenshots
├── docs/                # architecture diagram, notes
└── requirements.txt
```

## Setup

1. Clone the repo and install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Get free API credentials at https://developer.adzuna.com/
3. Create a `.env` file in the project root:
   ```
   ADZUNA_APP_ID=your_id_here
   ADZUNA_APP_KEY=your_key_here
   ```
4. Run the ingestion script:
   ```
   python ingestion/pull_jobs.py
   ```

## Key findings

Based on 1,182 postings for Data Analyst/Engineer/Scientist roles across
NL, DE, ES, and the UK (pulled July 2026):

- **Top skills overall:** Python (38 mentions), Azure (34), SQL (29), AWS (28),
  and Power BI (26) lead the tracked skill list. Cloud platforms (Azure, AWS,
  GCP combined) appear more often than any single BI tool.
- **UK postings are notably more skill-dense** than NL/DE/ES — despite all
  four countries having near-identical average description length (~498-499
  characters, all near Adzuna's truncation limit), UK postings mention
  roughly double the skills per posting of the other markets. This likely
  reflects how UK job ads are written (more keyword-forward, tool lists
  early in the text) rather than roles requiring more skills — the data
  can't fully distinguish the two explanations.
- **Postings are split almost evenly across the four countries** (~25%
  each), suggesting Adzuna's coverage is reasonably balanced, not skewed
  toward one market.
- **95.9% of postings are not tagged remote-friendly.** Traditional job
  board coverage skews heavily toward onsite/hybrid roles — a strong
  argument for the planned v1.1 RemoteOK addition, which should surface
  a very different, more remote-skewed picture.
- **"Data engineer" was the most-retrieved search term** (100 postings vs.
  ~65 each for analyst/scientist) — worth noting this reflects the query
  design (results-per-page cap) more than true market demand, and isn't a
  claim about which role has more real openings.

## Data sources & known limitations

- **Coverage:** Adzuna covers NL, DE, ES, GB. Ireland is not a supported
  Adzuna country — a planned v1.1 adds RemoteOK's API as a second source,
  partly to fill this gap and partly because it also surfaces remote-specific
  postings relevant to my own job search.
- **Description length:** Adzuna's free tier returns truncated (~500 char)
  job descriptions, not full text. Skill-extraction from descriptions is
  therefore directional, not exhaustive — skills mentioned later in a full
  posting will be undercounted. A paid tier or a scraping fallback would
  resolve this in a future version.
- **Single-letter skill names are unreliable to regex-match:** an early
  version tracked "R" (the language) and found it "mentioned" in 143
  postings — far more than Python or SQL. Inspecting the matches showed
  the regex was catching "R&D" (Research & Development), unrelated
  boilerplate text, not the language. R was removed from tracked skills
  as a result. General lesson: validate extraction results against raw
  text before trusting them, especially for short/ambiguous patterns.

## Status / roadmap

- [x] API ingestion script (NL, DE, ES, GB)
- [x] Load to BigQuery
- [x] dbt staging + mart models with tests
- [x] Looker Studio dashboard
- [ ] v1.1: add RemoteOK as a second source (Ireland + remote coverage)
- [ ] v2: automate weekly runs (currently run manually)

## Author

Transitioning from MBA/business
background into Data Analytics/Engineering.
