-- postgres-init/01_create_schema.sql
-- This script runs automatically when the Postgres database is initialized.

CREATE TABLE IF NOT EXISTS test_identification (
  test_id     INTEGER PRIMARY KEY,
  test_name   VARCHAR(100) NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS test_metrics (
  metric_id    SERIAL PRIMARY KEY,
  test_id      INTEGER NOT NULL REFERENCES test_identification(test_id),
  metric_name  VARCHAR(100) NOT NULL,
  metric_value NUMERIC(10,2) NOT NULL,
  recorded_at  TIMESTAMPTZ DEFAULT NOW()
);

