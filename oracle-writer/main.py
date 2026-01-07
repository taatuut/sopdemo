import os
import time
import oracledb


def dsn_from_env() -> str:
    """
    Prefer ORACLE_JDBC_URL from .env (jdbc:oracle:thin:@//host:port/service)
    and convert to python-oracledb EZConnect format (host:port/service).
    """
    jdbc = os.getenv("ORACLE_JDBC_URL", "").strip()
    if jdbc.startswith("jdbc:oracle:thin:@//"):
        return jdbc.replace("jdbc:oracle:thin:@//", "", 1)

    # fallback env var if you ever add it
    dsn = os.getenv("ORACLE_DSN", "").strip()
    if dsn:
        return dsn

    # final fallback
    return "oracle19c:1521/ORCLPDB1"


USER = os.getenv("ORACLE_USERNAME", "testuser")
PASSWORD = os.getenv("ORACLE_PASSWORD", "Oradoc_db1")
DSN = dsn_from_env()


def write_once():
    with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
        with conn.cursor() as cur:
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

            test_id = int(new_id.getvalue())

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
            print(f"Inserted test_id={test_id}")


if __name__ == "__main__":
    while True:
        write_once()
        time.sleep(30)
