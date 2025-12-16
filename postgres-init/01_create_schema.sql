-- postgres-init/01_create_schema.sql
-- Initializes Postgres schema (FK removed for demo simplicity)

CREATE TABLE IF NOT EXISTS test_identification (
  test_id     INTEGER PRIMARY KEY,
  test_name   VARCHAR(100) NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS test_metrics (
  metric_id    SERIAL PRIMARY KEY,
  test_id      INTEGER NOT NULL,
  metric_name  VARCHAR(100) NOT NULL,
  metric_value NUMERIC(10,2) NOT NULL,
  recorded_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Optional but recommended for demo/query performance
CREATE INDEX IF NOT EXISTS idx_test_metrics_test_id ON test_metrics(test_id);
