# jpa-oracle-source-package

## Prepare

Root folder is `/Users/emilzegers/GitHub/taatuut/sopdemo/`.

Created folder `./jpa-oracle-source-package` (folder where this `README.md` is).

Created `.empty`.

Created `README.md` (this file).

Tagged relevant section(s) in `docker-compose.yml` with `BO <tag>` and `EO <tag>`.

Run script `create-jpa-oracle-source-package.sh` to create `jpa-oracle-source-package.zip`.

This script:

Copies `../sample.env` to `.env`.

Copies `../jpa-oracle-config/application.yml` to `application.yml`.

Copies relevant section(s) from `../docker-compose.yml` to `docker-compose.yml` using tags `services` and `jpa-oracle-source`.

Zips folder contents to `jpa-oracle-source-package.zip`

## Check

Verify package can be used standalone

Commands:

```sh
todo
```

## Run

Convert to Kubernetes and deploy.