ALTER SESSION SET CONTAINER = FREEPDB1;
ALTER SESSION SET CURRENT_SCHEMA = testuser;

CREATE TABLE test_identification (
  id         NUMBER PRIMARY KEY,
  test_name  VARCHAR2(100) NOT NULL,
  created_at TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE TABLE test_metrics (
  metric_id    NUMBER PRIMARY KEY,
  test_id      NUMBER NOT NULL,
  metric_name  VARCHAR2(100) NOT NULL,
  metric_value NUMBER(10,2) NOT NULL,
  recorded_at  TIMESTAMP DEFAULT SYSTIMESTAMP,
  CONSTRAINT fk_test_metrics_ident
    FOREIGN KEY (test_id)
    REFERENCES test_identification(id)
);

CREATE SEQUENCE test_ident_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE metric_seq START WITH 1 INCREMENT BY 1;
