
with source as (

    select * from {{ source('job_market_raw', 'raw_jobs') }}

),

cleaned as (

    select
        -- identifiers / categorical fields
        trim(search_term)      as search_term,
        trim(country_code)     as country_code,
        trim(country_name)     as country_name,

        -- job details
        trim(title)             as job_title,
        trim(company)           as company_name_raw,
        coalesce(trim(company), 'Not disclosed') as company_name,
        trim(location)          as job_location,
        trim(contract_type)     as contract_type,

        -- salary — cast to numeric, keep nulls as nulls (don't fill with 0,
        -- that would distort averages later)
        cast(salary_min as numeric) as salary_min,
        cast(salary_max as numeric) as salary_max,

        -- full text field, used later for skill extraction
        description,

        -- dates
        cast(created as timestamp)   as posted_at,
        cast(pulled_at as timestamp) as pulled_at,

        redirect_url

    from source
    where description is not null   -- drop postings with no text, nothing to analyze

)

select * from cleaned
