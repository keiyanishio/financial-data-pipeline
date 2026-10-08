INSERT INTO raw.bcb_series_catalog (
    series_id,
    series_name,
    unit,
    frequency,
    source,
    source_url,
    is_active
)
VALUES
    (
        1,
        'Taxa de câmbio - Livre - Dólar americano (venda)',
        'Taxa unidade monetária corrente/dólar americano',
        'Diária',
        'BCB_SGS',
        'https://dadosabertos.bcb.gov.br/dataset/1-taxa-de-cambio---livre---dolar-americano-venda---diario',
        TRUE
    ),
    (
        24363,
        'Índice de Atividade Econômica do Banco Central - IBC-Br',
        'Índice',
        'Mensal',
        'BCB_SGS',
        'https://dadosabertos.bcb.gov.br/dataset/24363-indice-de-atividade-economica-do-banco-central---ibc-br',
        TRUE
    ),
    (
        24364,
        'Índice de Atividade Econômica do Banco Central - IBC-Br com ajuste sazonal',
        'Índice',
        'Mensal',
        'BCB_SGS',
        'https://dadosabertos.bcb.gov.br/dataset/24364-indice-de-atividade-economica-do-banco-central-ibc-br---com-ajuste-sazonal',
        TRUE
    )
ON CONFLICT (series_id)
DO UPDATE SET
    series_name = EXCLUDED.series_name,
    unit = EXCLUDED.unit,
    frequency = EXCLUDED.frequency,
    source = EXCLUDED.source,
    source_url = EXCLUDED.source_url,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;