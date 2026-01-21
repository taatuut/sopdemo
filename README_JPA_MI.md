# Databases (JPA) Solace Micro-Integration for Databases

## Context
This README describes setup and configuration of the JPA Micro-Integration for Oracle 19c deployed in Kubernetes.

## Prerequisites
- Docker Desktop
- Maven
- Code editor of choice, e.g. Visual Studio Code
- Kubernetes

## Preparation

### Docker image
Load `pubsubplus-connector-databaseV2.0.2.tar` as docker image, results in image with name `pubsubplus-connector-database` and tag `v2.0.2`.

```sh
docker load -i ./pubsubplus-connector-databaseV2.0.2.tar
# Optional: list images with ID, Disk Usage, ...
docker images
# Optional: tag image with custom tag using image ID
docker tag <IMAGE_ID> solace/mi-databases-jpa:2.0.2
```
### Configuration
The example configuration assumes following Oracle parameters for connectivity and schema:
```sh
```
#### yaml files
The configuration files use `host.docker.internal` to connect to conatiner host. Default Solace broker port is `55555`, set to `55554` on macOS because of reserved port.

Adjust following files:

`config and entity/Emil_PoC/Source_JPA_ora_TEST_IDENTIFICATION/Config/application-operator.yml`
TODO
`config and entity/Emil_PoC/SINK_JPA_pos_test_identification/Config/application-operator.yml`
TODO
#### Entity
Need Maven to (re)build package when making any changes for `table_entity-0.0.1.jar`. Install with `brew install maven` on macOS/Linux or simnilar on Windows.

Adjust following files:
`config and entity/pubsubplus-connector-database-entity-v2/src/main/java/com/solace/connectors/database/source/entity/TestIdentification.java`
TODO
`config and entity/pubsubplus-connector-database-entity-v2/src/main/java/com/solace/connectors/database/source/entity/TestMetrics.java`
TODO

Then in folder `config and entity/pubsubplus-connector-database-entity-v2` where `pom.xml`resides run command:

```sh
mvn clean package
```

This (re)builds jar file at `config and entity/pubsubplus-connector-database-entity-v2/target/table_entity-0.0.1.jar`

Copy `table_entity-0.0.1.jar` from folder `entity/pubsubplus-connector-database-entity-v2/target` to folder `config and entity/Emil_PoC/Source_JPA_ora_TEST_IDENTIFICATION/dependencies`.
#### Solace broker
Create queue `Q.ORACLE.TEST_IDENTIFICATION` with topic subscription `db/oracle/test_identification ` either in GUI, through API or using Event Portal.

NOTE: topic name can be adapted to your preference but must match with configuration in file `TODO.yml`. 

Create queue 
checked queues and subscriptions
created lvq

## Execution
Run docker specifying name (e.g. `solace-jpa-source`) and relevant configuration folder mapped to `/config` using the `pubsubplus-connector-database:v2.0.2` image.
```sh
docker run --name solace-jpa-source -v "/Users/emilzegers/GitHub/taatuut/sopdemo/config and entity/Emil_PoC/Source_JPA_ora_TEST_IDENTIFICATION:/config" pubsubplus-connector-database:v2.0.2
# Optional: to restart container
docker restart solace-jpa-source
# Optional: to view container logs
docker logs solace-jpa-source
```

# Tools
SolaceQueueMessageViewer see https://github.com/solacecommunity/solace-queue-browser-extension and images `images/SolaceQueueMessageViewer*.png` for example configuration.

# Links

https://solace.com/integration-hub/databases-jpa/