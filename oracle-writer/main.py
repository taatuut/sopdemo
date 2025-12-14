import time
import oracledb

dsn = "oracle19c:1521/FREEPDB1"

def write():
    conn = oracledb.connect(user="SYSTEM", password="Oradoc_db1", dsn=dsn)
    cur = conn.cursor()
    cur.execute("INSERT INTO test_identification (id, name) VALUES (TEST_IDENT_SEQ.NEXTVAL, 'demo')")
    cur.execute("INSERT INTO test_metrics (metric_id, metric_value) VALUES (METRIC_SEQ.NEXTVAL, 42)")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    while True:
        write()
        time.sleep(30)
