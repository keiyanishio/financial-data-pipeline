CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

COMMENT ON SCHEMA raw IS
    'Data ingested from source systems with minimal transformation.';

COMMENT ON SCHEMA staging IS
    'Cleaned, typed and standardized data used as an intermediate layer.';

COMMENT ON SCHEMA analytics IS
    'Business-ready analytical models and data marts.';


CREATE TABLE IF NOT EXISTS raw.bcb_series (
    series_id INTEGER NOT NULL,
    observation_date DATE NOT NULL,
    value NUMERIC(18, 6) NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'BCB_SGS',
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_raw_bcb_series
        PRIMARY KEY (series_id, observation_date)
);

COMMENT ON TABLE raw.bcb_series IS
    'Series temporais públicas extraídas do SGS do Banco Central.';

COMMENT ON COLUMN raw.bcb_series.series_id IS
    'Código da série no SGS do Banco Central.';

COMMENT ON COLUMN raw.bcb_series.observation_date IS
    'Data de referência da observação.';

COMMENT ON COLUMN raw.bcb_series.value IS
    'Valor informado pelo Banco Central.';

COMMENT ON COLUMN raw.bcb_series.ingested_at IS
    'Data e hora em que o registro foi carregado.';


CREATE TABLE IF NOT EXISTS raw.bcb_series_catalog (
    series_id INTEGER PRIMARY KEY,
    series_name VARCHAR(200) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    frequency VARCHAR(30) NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'BCB_SGS',
    source_url TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


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
        11,
        'Taxa de juros - Selic',
        'Percentual ao dia',
        'Diária',
        'BCB_SGS',
        'https://dadosabertos.bcb.gov.br/dataset/11-taxa-de-juros---selic',
        TRUE
    ),
    (
        432,
        'Taxa de juros - Meta Selic definida pelo Copom',
        'Percentual ao ano',
        'Diária',
        'BCB_SGS',
        'https://dadosabertos.bcb.gov.br/dataset/432-taxa-de-juros---meta-selic-definida-pelo-copom',
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



DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_bcb_series_catalog'
    ) THEN
        ALTER TABLE raw.bcb_series
        ADD CONSTRAINT fk_bcb_series_catalog
        FOREIGN KEY (series_id)
        REFERENCES raw.bcb_series_catalog (series_id);
    END IF;
END
$$;