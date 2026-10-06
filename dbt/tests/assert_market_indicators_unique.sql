select
    series_id,
    observation_date,
    count(*) as row_count
from {{ ref('market_indicators') }}
group by
    series_id,
    observation_date
having count(*) > 1