import os
import time
import oracledb

USER = "testuser"
PASSWORD = "Oradoc_db1"
DSN = "oracle19c:1521/ORCLPDB1"

def write_once():
    with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("select user from dual")
            print("DB user:", cur.fetchone()[0])

            cur.execute("select sys_context('USERENV','CON_NAME') from dual")
            print("CON_NAME:", cur.fetchone()[0])

            cur.execute("""
                select owner, table_name
                from all_tables
                where table_name in ('TEST_IDENTIFICATION','TEST_METRICS')
                order by owner, table_name
            """)
            print("Tables visible:", cur.fetchall())
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
            print(f"Inserted test_id={test_id}")


if __name__ == "__main__":
    while True:
        write_once()
        time.sleep(30)
