import time
import psycopg2

conn = psycopg2.connect(host="postgres", dbname="testdb", user="postgres", password="postgres")

while True:
    cur = conn.cursor()
    cur.execute("SELECT * FROM test_metrics ORDER BY metric_id DESC LIMIT 5")
    rows = cur.fetchall()
    print("Latest metrics:", rows)
    time.sleep(10)
