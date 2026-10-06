select
    series_id,
    observation_date,
    count(*) as row_count
from {{ ref('stg_bcb_series') }}
group by
    series_id,
    observation_date
having count(*) > 1