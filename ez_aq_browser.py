# Run Python script to browse AQ messages
# (prerequisite: Oracle Database up & running with Advanced Queuing set up by the 02_create_AQ_queue_plus_test.sql script):
# Go to the sopdemo directory and set up a virtual environment:
# cd sopdemo
"""
python3 -m venv .venv
source .venv/bin/activate
which python
pip install --upgrade pip
pip install -r requirements.txt
python3 ez_aq_browser.py
"""
# NOTE: credetials and host values hardcoded.

import oracledb
print("oracledb version:", oracledb.__version__)

USER = "aqdemo"
PWD = "AQdemo#123"
DSN = "localhost:1521/ORCLPDB1"   # EZConnect format

def main():
    with oracledb.connect(user=USER, password=PWD, dsn=DSN) as conn:
        with conn.cursor() as cur:
            # Show last 20 messages currently in the queue table (does NOT consume them)
            cur.execute("""
                SELECT
                    msgid,
                    enq_time,
                    state,
                    UTL_RAW.CAST_TO_VARCHAR2(user_data) AS payload
                FROM aqdemo_qtab
                ORDER BY enq_time DESC
                FETCH FIRST 20 ROWS ONLY
            """)

            rows = cur.fetchall()
            if not rows:
                print("Queue table AQDEMO_QTAB is empty.")
                return

            for msgid, enq_time, state, payload in rows:
                print(f"- enq_time={enq_time} state={state} msgid={msgid.hex()} payload={payload}")

if __name__ == "__main__":
    main()
