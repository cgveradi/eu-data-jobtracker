# EU Data Job Market Tracker

A data pipeline that pulls live data analyst / data engineer / data scientist
job postings across the Netherlands, Ireland, Spain, and the UK, and surfaces
which tools, skills, and salary ranges are actually in demand right now.

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
- How do salary ranges compare between NL, IE, ES, and the UK?
- What share of postings are remote-friendly?
- How is demand trending week over week?

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

## Status / roadmap

- [x] API ingestion script (NL, DE, ES, GB)
- [ ] Load to BigQuery
- [ ] dbt staging + mart models with tests
- [ ] Looker Studio dashboard
- [ ] v1.1: add RemoteOK as a second source (Ireland + remote coverage)
- [ ] v2: automate weekly runs (currently run manually)
