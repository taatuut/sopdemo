# sopdemo
A Oracle 19c ⇄ Solace ⇄ PostgreSQL Demo

End-to-end demo showing how to stream data from an **Oracle 19c** source database into **PostgreSQL** via a **Solace PubSub+ Standard** event broker and the **Solace Databases (JPA) Micro‑Integration**, with Python services producing and consuming data.

## What You Get
This repo contains:

- `docker-compose.yml` – brings up:
  - Oracle 19c source DB (Enterprise Edition, official Oracle container image)
  - PostgreSQL target DB
  - Solace PubSub+ Standard broker
  - Solace Databases (JPA) micro‑integration instance for **Oracle → Solace**
  - Solace Databases (JPA) micro‑integration instance for **Solace → PostgreSQL**
  - A Python **Oracle writer** service (inserts new test data every 30 seconds)
  - A Python **PostgreSQL reporter** service (continuously prints new rows)

- Auto‑init database scripts:
  - `oracle-init/01_create_schema.sql`
  - `postgres-init/01_create_schema.sql`

- Python apps:
  - `oracle-writer/` – inserts rows into Oracle
  - `postgres-reporter/` – reads rows from PostgreSQL

- JPA Micro‑Integration configs:
  - `jpa-oracle-config/application.yml`
  - `jpa-postgres-config/application.yml`

> ⚠️ **Important**:  
> The Solace Databases (JPA) Micro‑Integration container image is **not** on Docker Hub.  
> You must download current version `pubsubplus-connector-database-2.0.1-image.tar` from https://solace.com/integration-hub/databases-jpa/ at the **Solace Integration Hub** and `docker load` it locally before using this demo, see documentation `pubsubplus-connector-database-2.0.1-User-Guide.pdf`.

## High‑Level Architecture
TODO: swap order JPA MI Oracle and Solace PubSub+ Standard, arrow from JPA MI Oracle to Oracle 19c DB
```text
+-------------------+        +----------------------------+        +---------------------+
|  Oracle 19c DB    |        |  Solace PubSub+ Standard   |        |  PostgreSQL DB      |
|  (source)         |        |  (event broker)            |        |  (target)           |
+---------+---------+        +---------------+------------+        +----------+----------+
          ^                                  ^                                ^
          |                                  |                                |
          |                                  |                                |
          |                         +--------+--------+                       |
          |                         |  JPA MI:        |                       |
          |                         |  Oracle → Solace|                       |
          |                         +--------+--------+                       |
          |                                  |                                |
          |                        Topics:   |                                |
          |                        db/oracle/test_identification              |
          |                        db/oracle/test_metrics                     |
          |                                  v                                |
+---------+---------+        +---------------+------------+        +----------+----------+
| Python Writer    |         |  Queues on Solace          |  --->  |  JPA MI:           |
| (oracle-writer)  |         |  Q.ORACLE.TEST_IDENT...    |       |  Solace → Postgres |
+------------------+         |  Q.ORACLE.TEST_METRICS     |        +----------+---------+
                             +----------------------------+                   |
                                                                              v
                                                                     +--------+--------+
                                                                     | Python Reporter |
                                                                     | postgres-repor. |
                                                                     +-----------------+
```

## Prerequisites
This repo provides a `docker-compose.yml` file to run demo as a standalone setup. You can use existing (Cloud) components like Oracle, PostgreSQL database and Solace broker by changing environment parameters. Docker Desktop can convert your Compose file into Kubernetes manifests and deploy them to the Kubernetes cluster.

You’ll need:

1. **Docker Desktop** or similar alternatives (`podman`, `colima` with **docker-compose** installed, might hit some caveats).
2. Ability to log in to **Oracle Container Registry** and accept the Oracle Database 19c image license.
3. Access to the **Solace Databases (JPA) Micro‑Integration** container image:
   - Download from Solace Integration Hub (Databases JPA connector).
   - You should end up with a `.tar` image file which you then load into Docker.
4. Internet access for pulling the Postgres and Solace broker images (once).

## Repository structure

After unpacking/cloning:

```text
sopdemo
├── documents
├── images
├── jpa-oracle-config
├── jpa-oracle-source-package
├── jpa-postgres-config
│   └── lib
├── oracle-init
├── oracle-writer
├── postgres-init
├── postgres-reporter
└── samples
```
(source: `tree ../sopdemo -d > tree.txt`)

## One‑Time Preparation

### Download Oracle 19c Database Image

1. Go to Oracle Container Registry https://container-registry.oracle.com/ (you must have an Oracle account).
2. Accept the license for **Oracle Database Enterprise Edition** 19c.
3. Log in and pull the image:

```sh
docker login container-registry.oracle.com
docker pull container-registry.oracle.com/database/enterprise:19.3.0.0
```

This is the image used by `oracle19c` in `docker-compose.yml`.

NOTE: Docker Desktop (or similar) must be running the docker daemon. If not you might error message like:
```sh
failed to connect to the docker API at unix:///Users/emilzegers/.docker/run/docker.sock; check if the path is correct and if the daemon is running: dial unix /Users/emilzegers/.docker/run/docker.sock: connect: no such file or directory
```

### Download the Solace Databases (JPA) Micro‑Integration Image

1. Go to the Solace Integration Hub → **Databases (JPA)**.
2. Download the **container image** for the JPA micro‑integration.
3. Load it into Docker and tag it as `solace/mi-databases-jpa:2.0.1` (or adjust the tag and the compose file):

```sh
docker load -i ./pubsubplus-connector-database-2.0.1-image.tar
docker images
docker tag <IMAGE_ID> solace/mi-databases-jpa:2.0.1
```

Replace `<IMAGE_ID>` with the ID from `docker images`, for example:

```sh
docker images
                                                         i Info →   U  In Use
IMAGE                        ID             DISK USAGE   CONTENT SIZE   EXTRA
container-registry.oracle.com/database/enterprise:19.3.0.0
                             291fd8c7958b       8.32GB             0B        
solace/solace-pubsub-connector-database:2.0.1
                             ef614b5c4b57        291MB             0B        
emilzegers@ezSolace sopdemo % docker tag ef614b5c4b57 solace/mi-databases-jpa:2.0.1
```

If you use a different tag, update `docker-compose.yml` accordingly.

## Bring Up the Core Stack

Ensure you are in the root of the project:

```sh
cd <path/to/sopdemo>
```

### Build the Python Services

NOTE: depending on OS and Docker version you might need to use either `docker compose` or `docker-compose`

```sh
docker-compose build oracle-writer postgres-reporter
```

If necessary check for running containers (starting with `docker ps -a `) to avoid any port conflicts.

### Start Databases and Broker

```sh
docker-compose up -d oracle19c postgres solace-broker
```

The Oracle container will automatically run `oracle-init/01_create_schema.sql` during its first startup.

**Wait a few minutes** for Oracle to initialize. You can check logs and/or stats:

```sh
docker logs -f oracle19c
docker stats oracle19c
```

Once Oracle writes that the database is open and ready, you can continue. See Appendix Oracle Log for more details. 

```sh
#########################
DATABASE IS READY TO USE!
#########################
```

TIP: DBeaver to easily check Oracle and PostgreSQL database connectivity and schema creation (https://dbeaver.io/download/ or `brew install --cask dbeaver-community`).

### Start JPA Micro‑Integration Instances

After Oracle, Postgres, and the Solace broker are running:

```sh
docker-compose up -d jpa-oracle-source jpa-postgres-target
```

These will read their configuration from:

- `jpa-oracle-config/application.yml` (Oracle → Solace)
- `jpa-postgres-config/application.yml` (Solace → Postgres)

### Verify Solace Broker

Open PubSub+ Manager in your browser:

- URL: `http://localhost:8080`
- Default credentials from `docker-compose.yml`: `admin / admin`

Check that the queues:

- `Q.ORACLE.TEST_IDENTIFICATION`
- `Q.ORACLE.TEST_METRICS`

exist and have the correct topic subscriptions configured (also defined in the JPA MI config).

If not present, you can quickly create them in the UI (or via CLI/SEMP) and add subscriptions:

- `Q.ORACLE.TEST_IDENTIFICATION` → `db/oracle/test_identification`
- `Q.ORACLE.TEST_METRICS` → `db/oracle/test_metrics`

## Start the Demo Data Flow

### Start the Oracle Writer

```sh
docker-compose up -d oracle-writer
```

This service:

- Every 30 seconds:
  - Inserts one row into `TEST_IDENTIFICATION`.
  - Inserts three metrics rows into `TEST_METRICS`.
- Commits the transaction.

These new rows are picked up by the **JPA Oracle source** instance and published as messages to Solace topics.

### 7.2. Start the Postgres Reporter

```sh
docker-compose up -d postgres-reporter
```

Now, the full flow is:

1. Oracle writer inserts rows into Oracle 19c.
2. JPA Oracle source polls Oracle and publishes changes to:
   - `db/oracle/test_identification`
   - `db/oracle/test_metrics`
3. On the broker, those topics are attracted to:
   - `Q.ORACLE.TEST_IDENTIFICATION`
   - `Q.ORACLE.TEST_METRICS`
4. JPA Postgres target consumes from those queues and writes to:
   - `test_identification`
   - `test_metrics`
5. Postgres reporter polls for new rows and prints them.

View the reporter logs:

```sh
docker logs -f sopdemo-postgres-reporter
```

You should see lines similar to:

```text
[2025-01-01 12:00:05+00:00] test_id=1 (LoadTest-2025-01-01T12:00:05.123456), latency_ms=42.17
[2025-01-01 12:00:05+00:00] test_id=1 (LoadTest-2025-01-01T12:00:05.123456), throughput_msgps=87.33
[2025-01-01 12:00:05+00:00] test_id=1 (LoadTest-2025-01-01T12:00:05.123456), error_rate=0.89
```

## 8. Inspecting the Databases Manually

### 8.1. Oracle

Connect into the container:

```sh
docker exec -it oracle19c bash
```

Inside the container:

```sh
sqlplus testuser/testuser@ORCLPDB1

SELECT * FROM TEST_IDENTIFICATION ORDER BY TEST_ID DESC;
SELECT * FROM TEST_METRICS ORDER BY METRIC_ID DESC;
```

### 8.2. PostgreSQL

From your host:

```sh
docker exec -it postgres psql -U demo -d demo

SELECT * FROM test_identification ORDER BY test_id DESC;
SELECT * FROM test_metrics ORDER BY metric_id DESC;
```

You should see rows corresponding to the ones in Oracle.

## 9. Stopping and Cleaning Up

To stop everything:

```sh
docker-compose down
```

To remove volumes (Oracle/Postgres data will be wiped):

```sh
docker-compose down -v
```

## 10. Notes & Troubleshooting

- **Oracle startup takes time**: The initial creation of the CDB/PDB can easily take a few minutes. Don’t start the JPA or writer too early.
- **JPA configs**: The provided `application.yml` files are sane defaults that assume:
  - Single Solace broker.
  - Default Message VPN (`default`).
  - Simple direct mapping of table columns to JSON payload fields.
  - You may need to tweak workflow and entity configuration according to your exact JPA MI version. Use the official user guide as reference.
- **Connector workflows**:
  - `jpa-oracle-source` defines two workflows:
    - `TEST_IDENTIFICATION` table → `db/oracle/test_identification`
    - `TEST_METRICS` table → `db/oracle/test_metrics`
  - `jpa-postgres-target` defines two workflows:
    - `Q.ORACLE.TEST_IDENTIFICATION` → `test_identification`
    - `Q.ORACLE.TEST_METRICS` → `test_metrics`

If you get stuck with the JPA micro‑integration configuration, enable DEBUG logs in the MI container and compare with the examples in the official docs.

Happy testing! 🚀

# Appendices

## Appendix tips

To remove extended attributes from a downloaded file:

```sh
xattr -c pubsubplus-connector-database-2.0.2-SNAPSHOT.jar
```

Save listed jar contents to file:

```sh
unzip -l pubsubplus-connector-database-2.0.2-SNAPSHOT.jar > pubsubplus-connector-database-2.0.2-SNAPSHOT.txt
```

## Appendix docker compose

### build

```sh
docker-compose build oracle-writer postgres-reporter
[+] Building 19.7s (22/22) FINISHED                                                                                                                                                                
 => [internal] load local bake definitions                                                                                                                                                    0.0s
 => => reading from stdin 1.11kB                                                                                                                                                              0.0s
 => [oracle-writer internal] load build definition from Dockerfile                                                                                                                            0.0s
 => => transferring dockerfile: 195B                                                                                                                                                          0.0s
 => [postgres-reporter internal] load build definition from Dockerfile                                                                                                                        0.0s
 => => transferring dockerfile: 282B                                                                                                                                                          0.0s
 => [oracle-writer internal] load metadata for docker.io/library/python:3.12-slim                                                                                                             1.7s
 => [postgres-reporter internal] load .dockerignore                                                                                                                                           0.0s
 => => transferring context: 2B                                                                                                                                                               0.0s
 => [oracle-writer internal] load .dockerignore                                                                                                                                               0.0s
 => => transferring context: 2B                                                                                                                                                               0.0s
 => [oracle-writer 1/5] FROM docker.io/library/python:3.12-slim@sha256:fa48eefe2146644c2308b909d6bb7651a768178f84fc9550dcd495e4d6d84d01                                                       2.1s
 => => resolve docker.io/library/python:3.12-slim@sha256:fa48eefe2146644c2308b909d6bb7651a768178f84fc9550dcd495e4d6d84d01                                                                     0.0s
 => => sha256:be2247ce67e89642d0ab8de566a63a5dead183ebe55e6c08c14c573aa486a7c2 249B / 249B                                                                                                    0.3s
 => => sha256:a9f68c0a3aadb70a0b446f162248647f1909e76228a6c95bb38c0a7478bc0352 12.04MB / 12.04MB                                                                                              0.8s
 => => sha256:e4f53be5987bcccb341c9ba8661a266f8f4a6416b21b4bb1de6af395f2f9e3f4 1.27MB / 1.27MB                                                                                                0.6s
 => => sha256:f626fba1463b32b20f78d29b52dcf15be927dbb5372a9ba6a5f97aad47ae220b 30.14MB / 30.14MB                                                                                              1.4s
 => => extracting sha256:f626fba1463b32b20f78d29b52dcf15be927dbb5372a9ba6a5f97aad47ae220b                                                                                                     0.4s
 => => extracting sha256:e4f53be5987bcccb341c9ba8661a266f8f4a6416b21b4bb1de6af395f2f9e3f4                                                                                                     0.0s
 => => extracting sha256:a9f68c0a3aadb70a0b446f162248647f1909e76228a6c95bb38c0a7478bc0352                                                                                                     0.2s
 => => extracting sha256:be2247ce67e89642d0ab8de566a63a5dead183ebe55e6c08c14c573aa486a7c2                                                                                                     0.0s
 => [oracle-writer internal] load build context                                                                                                                                               0.0s
 => => transferring context: 2.13kB                                                                                                                                                           0.0s
 => [postgres-reporter internal] load build context                                                                                                                                           0.0s
 => => transferring context: 2.05kB                                                                                                                                                           0.0s
 => [oracle-writer 2/5] WORKDIR /app                                                                                                                                                          0.2s
 => [postgres-reporter 2/6] RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*                                                                             8.6s
 => [oracle-writer 3/5] COPY requirements.txt .                                                                                                                                               0.0s
 => [oracle-writer 4/5] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                    2.4s
 => [oracle-writer 5/5] COPY main.py .                                                                                                                                                        0.0s
 => [oracle-writer] exporting to image                                                                                                                                                        1.1s
 => => exporting layers                                                                                                                                                                       0.9s
 => => exporting manifest sha256:31f7523d8fef374cede40920c55383d78adee16aa8f381c5836aeb7e0e9c0c4e                                                                                             0.0s
 => => exporting config sha256:e94320473825036e25b5edef0916c499b0d01d50390e5a50ad408cb922eaee95                                                                                               0.0s
 => => exporting attestation manifest sha256:40bf87a0b7dcc359591be5b8062f71ded459fdc1624a6dd683b8bf0431fe6c6f                                                                                 0.0s
 => => exporting manifest list sha256:ea0107eae2459b80bf23fcddaf6a8e9846338f570f37f75b4c20266525f08ac1                                                                                        0.0s
 => => naming to docker.io/library/sopdemo-oracle-writer:latest                                                                                                                               0.0s
 => => unpacking to docker.io/library/sopdemo-oracle-writer:latest                                                                                                                            0.2s
 => [oracle-writer] resolving provenance for metadata file                                                                                                                                    0.0s
 => [postgres-reporter 3/6] WORKDIR /app                                                                                                                                                      0.0s 
 => [postgres-reporter 4/6] COPY requirements.txt .                                                                                                                                           0.0s 
 => [postgres-reporter 5/6] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                1.4s 
 => [postgres-reporter 6/6] COPY main.py .                                                                                                                                                    0.0s 
 => [postgres-reporter] exporting to image                                                                                                                                                    5.5s 
 => => exporting layers                                                                                                                                                                       4.6s 
 => => exporting manifest sha256:0b23be98940a921e44a06abdcbc69ef38d4a97d05fd726a9ce434cc8569b9ab3                                                                                             0.0s 
 => => exporting config sha256:71011b9022646571c04d4062f595aa17094e076d84a88cb8419ff457354f3a05                                                                                               0.0s 
 => => exporting attestation manifest sha256:1cb959962f42d2e3c01059b6ce631b30a9acb01322c1d6a3c07d149352f8e94d                                                                                 0.0s 
 => => exporting manifest list sha256:60cb47f4a1f3f1c6a17da4c0a4bbaf9ab07aab34e2da3288da33cee97abccb90                                                                                        0.0s
 => => naming to docker.io/library/sopdemo-postgres-reporter:latest                                                                                                                           0.0s
 => => unpacking to docker.io/library/sopdemo-postgres-reporter:latest                                                                                                                        0.9s
 => [postgres-reporter] resolving provenance for metadata file                                                                                                                                0.0s
[+] Building 2/2
 ✔ sopdemo-postgres-reporter  Built                                                                                                                                                           0.0s 
 ✔ sopdemo-oracle-writer      Built 
```

### up

```sh
docker-compose up -d oracle19c postgres solace-broker
[+] Running 30/30
 ✔ solace-broker Pulled                                                                                                                                                                      43.8s 
   ✔ 37ec27b0cc89 Pull complete                                                                                                                                                              42.0s 
   ✔ eb0c5f005c94 Pull complete                                                                                                                                                              38.3s 
   ✔ bb4d4e0bb46a Pull complete                                                                                                                                                              40.7s 
   ✔ 4f4fb700ef54 Pull complete                                                                                                                                                               0.7s 
   ✔ 040d3098cb9f Pull complete                                                                                                                                                              40.6s 
   ✔ 3d31ff0be4b8 Pull complete                                                                                                                                                              16.0s 
   ✔ 4878ebb9364a Pull complete                                                                                                                                                              39.0s 
   ✔ eb1c72a6f5f4 Pull complete                                                                                                                                                              39.2s 
 ✔ postgres Pulled                                                                                                                                                                           16.9s 
   ✔ 68ddf11a3b09 Pull complete                                                                                                                                                               2.2s 
   ✔ 095c943337a4 Pull complete                                                                                                                                                               2.1s 
   ✔ 70eefe1d4030 Pull complete                                                                                                                                                              12.9s 
   ✔ 30510bb727c6 Pull complete                                                                                                                                                              12.8s 
   ✔ 9489ff614da7 Pull complete                                                                                                                                                               2.2s 
   ✔ 5c0519ff8ffa Pull complete                                                                                                                                                               2.1s 
   ✔ 6dd96c6166b0 Pull complete                                                                                                                                                               5.6s 
   ✔ 1790448b2ffa Pull complete                                                                                                                                                               5.7s 
   ✔ 87e4529caf5b Pull complete                                                                                                                                                               2.2s 
   ✔ dd41c2432499 Pull complete                                                                                                                                                               2.1s 
   ✔ 1ec970c8249c Pull complete                                                                                                                                                               3.5s 
   ✔ 7f7bda153710 Pull complete                                                                                                                                                               5.5s 
   ✔ c460c571d627 Pull complete                                                                                                                                                               2.1s 
 ✔ oracle19c Pulled                                                                                                                                                                          42.4s 
   ✔ 581cd9b60709 Pull complete                                                                                                                                                              40.4s 
   ✔ e910ada64373 Pull complete                                                                                                                                                              39.0s 
   ✔ 1a21ffc61e30 Pull complete                                                                                                                                                              14.1s 
   ✔ 6892bd8688ca Pull complete                                                                                                                                                              39.9s 
   ✔ a0e6f73c8374 Pull complete                                                                                                                                                              14.9s 
   ✔ e4752e3cd1af Pull complete                                                                                                                                                              38.0s 
[+] Running 5/5
 ✔ Network sopdemo_default          Created                                                                                                                                                   0.0s 
 ✔ Volume sopdemo_oracle-free-data  Created                                                                                                                                                   0.0s 
 ✔ Container oracle19c              Started                                                                                                                                                   0.8s 
 ✔ Container solace-broker          Started                                                                                                                                                   0.8s 
 ✔ Container postgres               Started                                                                                                                                                   0.8s 
```

### ps

```sh
docker ps -a
CONTAINER ID   IMAGE                                  COMMAND                  CREATED         STATUS         PORTS                                                                                                                                                                                        NAMES
473df24add2f   postgres:16                            "docker-entrypoint.s…"   7 seconds ago   Up 7 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp                                                                                                                                                  postgres
25bb2b256061   gvenzl/oracle-free:23-slim             "container-entrypoin…"   7 seconds ago   Up 7 seconds   0.0.0.0:1521->1521/tcp, [::]:1521->1521/tcp, 0.0.0.0:5500->5500/tcp, [::]:5500->5500/tcp                                                                                                     oracle19c
2c92c2e4a2e5   solace/solace-pubsub-standard:latest   "/usr/sbin/boot.sh"      7 seconds ago   Up 7 seconds   0.0.0.0:8008->8008/tcp, [::]:8008->8008/tcp, 0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp, 0.0.0.0:55443->55443/tcp, [::]:55443->55443/tcp, 0.0.0.0:55554->55555/tcp, [::]:55554->55555/tcp   solace-broker
```

### logs

```sh
docker logs -f oracle19c

CONTAINER: starting up...
CONTAINER: first database startup, initializing...
CONTAINER: uncompressing database data files, please wait...
CONTAINER: done uncompressing database data files, duration: 4 seconds.
CONTAINER: starting up Oracle Database...

LSNRCTL for Linux: Version 23.26.0.0.0 - Production on 14-DEC-2025 00:18:51

Copyright (c) 1991, 2025, Oracle.  All rights reserved.

Starting /opt/oracle/product/26ai/dbhomeFree/bin/tnslsnr: please wait...

TNSLSNR for Linux: Version 23.26.0.0.0 - Production
System parameter file is /opt/oracle/product/26ai/dbhomeFree/network/admin/listener.ora
Log messages written to /opt/oracle/diag/tnslsnr/3427e91abf2f/listener/alert/log.xml
Listening on: (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=EXTPROC_FOR_FREE)))
Listening on: (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=0.0.0.0)(PORT=1521)))

Connecting to (DESCRIPTION=(ADDRESS=(PROTOCOL=IPC)(KEY=EXTPROC_FOR_FREE)))
STATUS of the LISTENER
------------------------
Alias                     LISTENER
Version                   TNSLSNR for Linux: Version 23.26.0.0.0 - Production
Start Date                14-DEC-2025 00:18:51
Uptime                    0 days 0 hr. 0 min. 0 sec
Trace Level               off
Security                  ON: Local OS Authentication
SNMP                      OFF
Default Service           FREE
Listener Parameter File   /opt/oracle/product/26ai/dbhomeFree/network/admin/listener.ora
Listener Log File         /opt/oracle/diag/tnslsnr/3427e91abf2f/listener/alert/log.xml
Listening Endpoints Summary...
  (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=EXTPROC_FOR_FREE)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=0.0.0.0)(PORT=1521)))
The listener supports no services
The command completed successfully
ORACLE instance started.

Total System Global Area 1603373280 bytes
Fixed Size                  5007584 bytes
Variable Size             654311424 bytes
Database Buffers          939524096 bytes
Redo Buffers                4530176 bytes
Database mounted.
Database opened.

CONTAINER: Resetting SYS and SYSTEM passwords.

User altered.


User altered.

CONTAINER: Creating app user for default pluggable database.

Session altered.


User created.


Grant succeeded.

CONTAINER: DONE: Creating app user for default pluggable database.

CONTAINER: Executing user-defined scripts...

CONTAINER: running /container-entrypoint-startdb.d/01_create_schema.sql ...

Session altered.

CREATE USER testuser IDENTIFIED BY testuser
            *
ERROR at line 1:
ORA-01920: user name 'TESTUSER' conflicts with another user or role name
Help: https://docs.oracle.com/error-help/db/ora-01920/



Grant succeeded.


Table created.


Table created.


Sequence created.


Sequence created.

CONTAINER: DONE: running /container-entrypoint-startdb.d/01_create_schema.sql

CONTAINER: DONE: Executing user-defined scripts.


#########################
DATABASE IS READY TO USE!
#########################

####################################################################
CONTAINER: The following output is now from the alert_FREE.log file:
####################################################################
Completed: ALTER DATABASE OPEN
2025-12-14T00:18:54.058656+00:00
Thread 1 advanced to log sequence 13 (LGWR switch),  current SCN: 2276767
  Current log# 1 seq# 13 mem# 0: /opt/oracle/oradata/FREE/redo01.log
Thread 1 cannot allocate new log, sequence 14
Checkpoint not complete
  Current log# 1 seq# 13 mem# 0: /opt/oracle/oradata/FREE/redo01.log
2025-12-14T00:18:54.713203+00:00
Thread 1 advanced to log sequence 14 (LGWR switch),  current SCN: 2276898
  Current log# 2 seq# 14 mem# 0: /opt/oracle/oradata/FREE/redo02.log
2025-12-14T00:18:54.765649+00:00
Resize operation completed for file# 18, fname /opt/oracle/oradata/FREE/undotbs01.dbf, old size 11264K, new size 21504K
2025-12-14T00:18:55.163910+00:00
Thread 1 advanced to log sequence 15 (LGWR switch),  current SCN: 2277625
  Current log# 1 seq# 15 mem# 0: /opt/oracle/oradata/FREE/redo01.log
Thread 1 cannot allocate new log, sequence 16
Checkpoint not complete
  Current log# 1 seq# 15 mem# 0: /opt/oracle/oradata/FREE/redo01.log
2025-12-14T00:18:55.367356+00:00
Thread 1 advanced to log sequence 16 (LGWR switch),  current SCN: 2277673
  Current log# 2 seq# 16 mem# 0: /opt/oracle/oradata/FREE/redo02.log
FREEPDB1(3):Resize operation completed for file# 23, fname /opt/oracle/oradata/FREE/FREEPDB1/undotbs01.dbf, old size 11264K, new size 21504K
```

# Appendix Oracle Log

```sh
docker logs -f oracle19c
[2025:12:18 17:34:49]: Acquiring lock .ORCLCDB.create_lck with heartbeat 30 secs
[2025:12:18 17:34:49]: Lock acquired
[2025:12:18 17:34:49]: Starting heartbeat
[2025:12:18 17:34:49]: Lock held .ORCLCDB.create_lck
ORACLE EDITION: ENTERPRISE

LSNRCTL for Linux: Version 19.0.0.0.0 - Production on 18-DEC-2025 17:34:49

Copyright (c) 1991, 2019, Oracle.  All rights reserved.

Starting /opt/oracle/product/19c/dbhome_1/bin/tnslsnr: please wait...

TNSLSNR for Linux: Version 19.0.0.0.0 - Production
System parameter file is /opt/oracle/product/19c/dbhome_1/network/admin/listener.ora
Log messages written to /opt/oracle/diag/tnslsnr/544c5dcf5add/listener/alert/log.xml
Listening on: (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=EXTPROC1)))
Listening on: (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=0.0.0.0)(PORT=1521)))

Connecting to (DESCRIPTION=(ADDRESS=(PROTOCOL=IPC)(KEY=EXTPROC1)))
STATUS of the LISTENER
------------------------
Alias                     LISTENER
Version                   TNSLSNR for Linux: Version 19.0.0.0.0 - Production
Start Date                18-DEC-2025 17:34:49
Uptime                    0 days 0 hr. 0 min. 0 sec
Trace Level               off
Security                  ON: Local OS Authentication
SNMP                      OFF
Listener Parameter File   /opt/oracle/product/19c/dbhome_1/network/admin/listener.ora
Listener Log File         /opt/oracle/diag/tnslsnr/544c5dcf5add/listener/alert/log.xml
Listening Endpoints Summary...
  (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=EXTPROC1)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=0.0.0.0)(PORT=1521)))
The listener supports no services
The command completed successfully
Prepare for db operation
8% complete
Copying database files
31% complete
Creating and starting Oracle instance
32% complete
36% complete
40% complete
43% complete
46% complete
Completing Database Creation
51% complete
54% complete
Creating Pluggable Databases
58% complete
77% complete
Executing Post Configuration Actions
100% complete
Database creation complete. For details check the logfiles at:
 /opt/oracle/cfgtoollogs/dbca/ORCLCDB.
Database Information:
Global Database Name:ORCLCDB
System Identifier(SID):ORCLCDB
Look at the log file "/opt/oracle/cfgtoollogs/dbca/ORCLCDB/ORCLCDB.log" for further details.

SQL*Plus: Release 19.0.0.0.0 - Production on Thu Dec 18 17:49:24 2025
Version 19.3.0.0.0

Copyright (c) 1982, 2019, Oracle.  All rights reserved.


Connected to:
Oracle Database 19c Enterprise Edition Release 19.0.0.0.0 - Production
Version 19.3.0.0.0

SQL> 
System altered.

SQL> 
System altered.

SQL> 
Pluggable database altered.

SQL> 
PL/SQL procedure successfully completed.

SQL> SQL> 
Session altered.

SQL> 
User created.

SQL> 
Grant succeeded.

SQL> 
Grant succeeded.

SQL> 
Grant succeeded.

SQL> 
User altered.

SQL> SQL> Disconnected from Oracle Database 19c Enterprise Edition Release 19.0.0.0.0 - Production
Version 19.3.0.0.0
The Oracle base remains unchanged with value /opt/oracle

Executing user defined scripts
/opt/oracle/runUserScripts.sh: running /opt/oracle/scripts/extensions/setup/swapLocks.sh
[2025:12:18 17:49:29]: Releasing lock .ORCLCDB.create_lck
[2025:12:18 17:49:29]: Lock released .ORCLCDB.create_lck
[2025:12:18 17:49:29]: Acquiring lock .ORCLCDB.exist_lck with heartbeat 30 secs
[2025:12:18 17:49:29]: Lock acquired
[2025:12:18 17:49:29]: Starting heartbeat
[2025:12:18 17:49:29]: Lock held .ORCLCDB.exist_lck

DONE: Executing user defined scripts


Executing user defined scripts
/opt/oracle/runUserScripts.sh: running /opt/oracle/scripts/setup/01_create_schema.sql
ERROR:
ORA-65011: Pluggable database FREEPDB1 does not exist.


ERROR:
ORA-01435: user does not exist



Table created.


Table created.


Sequence created.


Sequence created.



DONE: Executing user defined scripts

The Oracle base remains unchanged with value /opt/oracle
#########################
DATABASE IS READY TO USE!
#########################
The following output is now a tail of the alert.log:
ORCLPDB1(3):
ORCLPDB1(3):XDB initialized.
2025-12-18T17:49:24.803493+00:00
ALTER SYSTEM SET control_files='/opt/oracle/oradata/ORCLCDB/control01.ctl' SCOPE=SPFILE;
2025-12-18T17:49:24.826214+00:00
ALTER SYSTEM SET local_listener='' SCOPE=BOTH;
   ALTER PLUGGABLE DATABASE ORCLPDB1 SAVE STATE
Completed:    ALTER PLUGGABLE DATABASE ORCLPDB1 SAVE STATE

XDB initialized.
```

## Appendix colima

### Colima

```sh
brew install colima lima-additional-guestagents docker qemu
```

~~Need to start colima with `--arch x86_64` for Oracle.~~

ARM Oracle support means no x86 emulation needed.

```sh
colima start --runtime docker --cpu 6 --memory 12 --disk 100 --network-address
```

If already started without run:

```sh
colima stop
colima delete
<colima start command>
limactl info | jq .guestAgents
docker context use colima
docker info | grep -i architecture
docker context ls
```

On Apple Silicon (M1/M2/M3), Oracle Database is not available natively. The official 19c Enterprise image is amd64-only, and running it under Docker Desktop’s built-in emulation (qemu/Rosetta) is known to cause these kinds of failures: PMON not starting, ORA-01034 during DBCA, etc.

📌 Final note: will never get Oracle 19c to run inside Colima on Apple Silicon — SIGILL during DBCA makes it impossible.

On macOS M use ARM-native “Oracle Free 23ai” image like `gvenzl/oracle-free`.

### Uninstall

```sh
colima stop --force
colima delete
limactl stop --all
limactl delete --all
pkill -f colima
pkill -f limactl
osascript -e 'quit app "Docker"'
osascript -e 'quit app "Podman Desktop"'  
rm -rf ~/.docker
rm -rf ~/.colima
rm -rf ~/.lima
sudo rm -rf /Library/Containers/com.docker.docker
sudo rm -rf /Library/Group\ Containers/group.com.docker
brew uninstall --cask docker-desktop podman-desktop
brew uninstall colima docker docker-completion docker-compose docker-credential-helper lima lima-additional-guestagents
brew list | grep -E 'docker|lima|colima'
brew list --cask | grep -E 'docker|podman'
ps aux | grep -E 'lima|colima|podman' | grep -v grep
ls ~/.lima ~/.colima 2>/dev/null
```
