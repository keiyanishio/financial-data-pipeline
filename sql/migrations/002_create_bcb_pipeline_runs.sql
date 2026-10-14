CREATE SCHEMA IF NOT EXISTS audit;

COMMENT ON SCHEMA audit IS
    'Pipeline execution history and operational metadata.';
    
CREATE TABLE IF NOT EXISTS audit.bcb_pipeline_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY,
    series_id INTEGER NOT NULL,
    airflow_run_id TEXT,
    requested_start_date DATE NOT NULL,
    requested_end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    rows_loaded INTEGER,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMPTZ,

    CONSTRAINT pk_bcb_pipeline_runs
        PRIMARY KEY (run_id),

    CONSTRAINT fk_bcb_pipeline_runs_series
        FOREIGN KEY (series_id)
        REFERENCES raw.bcb_series_catalog (series_id),

    CONSTRAINT ck_bcb_pipeline_runs_status
        CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),

    CONSTRAINT ck_bcb_pipeline_runs_period
        CHECK (requested_start_date <= requested_end_date),

    CONSTRAINT ck_bcb_pipeline_runs_rows
        CHECK (rows_loaded IS NULL OR rows_loaded >= 0)
);

CREATE INDEX IF NOT EXISTS ix_bcb_pipeline_runs_series_started_at
    ON audit.bcb_pipeline_runs (series_id, started_at DESC);