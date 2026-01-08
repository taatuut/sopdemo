import os
import time
import oracledb
from datetime import datetime, timezone

USER = os.environ.get("ORACLE_USERNAME")
PASS = os.environ.get("ORACLE_PWD")
JDBC = "jdbc:oracle:thin:@//"
DSN = os.environ.get("ORACLE_JDBC_URL").replace(JDBC, "")

def log_info(message: str, level: str = "INFO"):
    """
    Print log message with ISO 8601 / RFC 3339 timestamp and log level

    Examples:
    2026-01-10T14:32:05.123Z INFO DB user: TESTUSER
    2026-01-10T14:32:05.123Z ERROR Connection failed
    """
    ts = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    print(f"{ts} {level.upper()} {message}", flush=True)

def write_once():
    with oracledb.connect(user=USER, password=PASS, dsn=DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("select user from dual")
            log_info(f"DB user: {cur.fetchone()[0]}")

            cur.execute("select sys_context('USERENV','CON_NAME') from dual")
            log_info(f"CON_NAME: {cur.fetchone()[0]}")

            cur.execute("""
                select owner, table_name
                from all_tables
                where table_name in ('TEST_IDENTIFICATION','TEST_METRICS')
                order by owner, table_name
            """)
            log_info(f"Tables visible: {cur.fetchall()}")

            # Insert into test_identification and fetch generated id
            new_id = cur.var(oracledb.NUMBER)

            cur.execute(
                """
                INSERT INTO test_identification (id, test_name)
                VALUES (test_ident_seq.NEXTVAL, :test_name)
                RETURNING id INTO :new_id
                """,
                test_name="demo",
                new_id=new_id,
            )

            val = new_id.getvalue()
            test_id = int(val[0] if isinstance(val, list) else val)

            # Insert corresponding metric referencing the test_id
            cur.execute(
                """
                INSERT INTO test_metrics (metric_id, test_id, metric_name, metric_value)
                VALUES (metric_seq.NEXTVAL, :test_id, :metric_name, :metric_value)
                """,
                test_id=test_id,
                metric_name="example_metric",
                metric_value=42.0,
            )

            conn.commit()
            log_info(f"Inserted test_id={test_id}")


if __name__ == "__main__":
    while True:
        write_once()
        time.sleep(30)
