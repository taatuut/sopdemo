java -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:7878  -cp ./pubsubplus-connector-database-2.0.2-SNAPSHOT.jar -D"loader.path=./Emil_PoC/Source_JPA_ora_TEST_METRICS/dependencies,./Emil_PoC/Source_JPA_ora_TEST_METRICS/Config"  org.springframework.boot.loader.launch.PropertiesLauncher --spring.config.additional-location="./Emil_PoC/Source_JPA_ora_TEST_METRICS/Config/application-operator.yml"


database: oracle   comments
