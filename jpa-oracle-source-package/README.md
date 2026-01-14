# jpa-oracle-source-package

## Prepare
- Root folder is `/Users/emilzegers/GitHub/taatuut/sopdemo/`.
- Created workfolder `./jpa-oracle-source-package` with macOS Shell script `create-jpa-oracle-source-package.sh` then `chmod +x create-jpa-oracle-source-package.sh`.
- Tagged relevant section(s) in `docker-compose.yml` with `BO <tag>` and `EO <tag>`.

The script does the following:
- Copies tagged section(s) from`../sample.env` to `sample.env` in workfolder using tags `ORACLE`, `SOLACE`, `DATADOG` and `WORKFLOW`.
 -Copies `../jpa-oracle-config/application.yml` to `application.yml` in workfolder.
- Copies tagged section(s) from `../docker-compose.yml` to `docker-compose.yml`  in workfolder using tags `services` and `jpa-oracle-source`.
- Zips folder contents of workfolder to `jpa-oracle-source-package.zip` and stores zip in folder `./jpa-oracle-source-package` overwriting when exists.

Tag blocks must be delimited with:

```sh
BO <tag>   (or commented variants: # BO <tag>, #BO <tag>)
...
EO <tag>   (or commented variants: # EO <tag>, #EO <tag>)
```

In folder `jpa-oracle-source-package` run script `./create-jpa-oracle-source-package.sh` to create `jpa-oracle-source-package.zip`.

## Configure

Rename `sample.env` to `.env`

Change relevant variables in `.env`.

## Check

Verify package can be used standalone with Docker Desktop (or similar).

Commands:

```sh
<TODO, see ../README.md>
```

## Kubernetes

Convert to Kubernetes and deploy.