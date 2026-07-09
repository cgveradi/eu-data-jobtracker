-- Mart model: flags which skills/tools are mentioned in each job posting's
-- description. One row per job posting, one boolean column per skill.
--
-- Note: descriptions are truncated to ~500 characters by Adzuna's free tier,
-- so this undercounts skills mentioned later in the full posting. Directional
-- signal, not exhaustive — documented in the README as a known limitation.
--
-- Note: "R" (the language) is deliberately excluded from this list.
-- Single-letter names are unreliable to regex-match against free text —
-- \bR\b was found matching "R&D" (Research & Development), a common,
-- unrelated phrase in job postings, producing false-positive counts far
-- higher than genuine mentions. Also documented as a known limitation.

with staged as (

    select * from {{ ref('stg_jobs') }}

),

flagged as (

    select
        *,

        -- REGEXP_CONTAINS is case-sensitive by default, so we lower() the
        -- description once and match lowercase patterns against it.
        -- (?i) isn't needed in BigQuery's re2 syntax when we lower() first.

        regexp_contains(lower(description), r'\bsql\b')            as mentions_sql,
        regexp_contains(lower(description), r'\bpython\b')         as mentions_python,
        regexp_contains(lower(description), r'\bdbt\b')            as mentions_dbt,
        regexp_contains(lower(description), r'\bairflow\b')        as mentions_airflow,
        regexp_contains(lower(description), r'\bsnowflake\b')      as mentions_snowflake,
        regexp_contains(lower(description), r'\bbigquery\b')       as mentions_bigquery,
        regexp_contains(lower(description), r'\bexcel\b')          as mentions_excel,
        regexp_contains(lower(description), r'\btableau\b')        as mentions_tableau,
        regexp_contains(lower(description), r'\bpower ?bi\b')       as mentions_power_bi,
        regexp_contains(lower(description), r'\blooker\b')          as mentions_looker,
        regexp_contains(lower(description), r'\bspark\b')           as mentions_spark,
        regexp_contains(lower(description), r'\baws\b')             as mentions_aws,
        regexp_contains(lower(description), r'\bazure\b')           as mentions_azure,
        regexp_contains(lower(description), r'\bgcp\b')             as mentions_gcp,
        regexp_contains(lower(description), r'\bdocker\b')          as mentions_docker,
        regexp_contains(lower(description), r'\bkubernetes\b')      as mentions_kubernetes,
        regexp_contains(lower(description), r'\bkafka\b')           as mentions_kafka,

        -- whether the posting appears remote-friendly, based on location text
        regexp_contains(lower(job_location), r'\bremote\b')
            or regexp_contains(lower(description), r'\bremote\b')
            as is_remote_friendly

    from staged

)

select * from flagged
