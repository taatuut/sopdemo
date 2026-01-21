import os
import time
import psycopg2
from datetime import datetime, timezone

conn = psycopg2.connect(
    host=os.environ.get("POSTGRES_HOST"),
    dbname=os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USERNAME"),
    password=os.environ.get("POSTGRES_PASSWORD")
)

def log_info(message: str, level: str = "INFO"):
    ts = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    print(f"{ts} {level.upper()} {message}", flush=True)

if __name__ == "__main__":
    while True:
        cur = conn.cursor()
        cur.execute("SELECT * FROM test_identification ORDER BY test_id DESC LIMIT 1")
        rows = cur.fetchall()
        log_info(f"Latest identification: {rows}")
        cur.execute("SELECT * FROM test_metrics ORDER BY metric_id DESC LIMIT 5")
        rows = cur.fetchall()
        log_info(f"Latest metrics: {rows}")
        time.sleep(10)
