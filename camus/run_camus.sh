#!/bin/sh
# this script is set to run in cron job every hour
cd /usr/local/hadoop/etc/hadoop/
hadoop jar camus-example-0.1.0-SNAPSHOT-shaded.jar com.linkedin.camus.etl.kafka.CamusJob -P /usr/local/camus/camus-example/src/main/resources/camus.properties
cd -
