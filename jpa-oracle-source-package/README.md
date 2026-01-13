# jpa-oracle-source-package

## Prepare
- Root folder is `/Users/emilzegers/GitHub/taatuut/sopdemo/`.
- Created workfolder `./jpa-oracle-source-package` with macOS Shell script `create-jpa-oracle-source-package.sh` then `chmod +x create-jpa-oracle-source-package.sh`.
- Tagged relevant section(s) in `docker-compose.yml` with `BO <tag>` and `EO <tag>`.

Script does the following:
- Copies `../sample.env` to `.env` in workfolder.
 -Copies `../jpa-oracle-config/application.yml` to `application.yml` in workfolder.
- Copies relevant section(s) from `../docker-compose.yml` to `docker-compose.yml`  in workfolder using tags `services` and `jpa-oracle-source`.
- Zips folder contents of workfolder to `jpa-oracle-source-package.zip` and stores zip in folder `./jpa-oracle-source-package` overwriting when exists.

Run script `create-jpa-oracle-source-package.sh` to create `jpa-oracle-source-package.zip`.

## Check

Verify package can be used standalone.

Commands:

```sh
todo
```

## Configure

Rename `sample.env` to `.env`

Change relevant variables in `.env`.

Test setup

TODO: add docker commands

## Run

Convert to Kubernetes and deploy.