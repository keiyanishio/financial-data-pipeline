select
    series_id::integer as series_id,
    trim(series_name) as series_name,
    trim(unit) as unit,
    trim(frequency) as frequency,
    trim(source) as source,
    source_url::text as source_url,
    is_active::boolean as is_active,
    created_at::timestamptz as created_at,
    updated_at::timestamptz as updated_at
from {{ source('raw', 'bcb_series_catalog') }}