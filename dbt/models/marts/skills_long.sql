-- Reshapes the wide skills_extracted table (one boolean column per skill)
-- into a long/tidy format: one row per (posting, skill) pair, only where
-- that skill was actually mentioned. This is what makes a clean "top
-- skills" bar chart possible in Looker Studio — charting tools want one
-- column to group by, not 18 separate boolean columns.

with base as (

    select
        redirect_url,
        country_name,
        search_term,
        posted_at,
        is_remote_friendly,
        mentions_sql,
        mentions_python,
        mentions_dbt,
        mentions_airflow,
        mentions_snowflake,
        mentions_bigquery,
        mentions_excel,
        mentions_tableau,
        mentions_power_bi,
        mentions_looker,
        mentions_spark,
        mentions_aws,
        mentions_azure,
        mentions_gcp,
        mentions_docker,
        mentions_kubernetes,
        mentions_kafka
    from {{ ref('skills_extracted') }}

),

unpivoted as (

    select
        redirect_url,
        country_name,
        search_term,
        posted_at,
        is_remote_friendly,
        skill,
        mentioned
    from base
    unpivot(mentioned for skill in (
        mentions_sql        as 'SQL',
        mentions_python      as 'Python',
        mentions_dbt         as 'dbt',
        mentions_airflow     as 'Airflow',
        mentions_snowflake   as 'Snowflake',
        mentions_bigquery    as 'BigQuery',
        mentions_excel       as 'Excel',
        mentions_tableau     as 'Tableau',
        mentions_power_bi    as 'Power BI',
        mentions_looker      as 'Looker',
        mentions_spark       as 'Spark',
        mentions_aws         as 'AWS',
        mentions_azure       as 'Azure',
        mentions_gcp         as 'GCP',
        mentions_docker      as 'Docker',
        mentions_kubernetes  as 'Kubernetes',
        mentions_kafka       as 'Kafka'
    ))

)

-- only keep rows where the skill was actually mentioned — Looker Studio
-- just needs to count rows per skill, no need to carry the FALSE rows
select
    redirect_url,
    country_name,
    search_term,
    posted_at,
    is_remote_friendly,
    skill
from unpivoted
where mentioned = true
