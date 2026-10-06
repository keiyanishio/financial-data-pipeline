select
    series.series_id,
    catalog.series_name,
    catalog.unit,
    catalog.frequency,
    series.observation_date,
    series.value,
    catalog.source,
    catalog.source_url
from {{ ref('stg_bcb_series') }} as series
inner join {{ ref('stg_bcb_series_catalog') }} as catalog
    on series.series_id = catalog.series_id
where catalog.is_active = true