select
    series_id::integer as series_id,
    observation_date::date as observation_date,
    value::numeric(18, 6) as value
from {{ source('raw', 'bcb_series') }}