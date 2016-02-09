#!/bin/bash

$SPARK_HOME/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.0,TargetHolding:pyspark-cassandra:0.2.7 --conf spark.cassandra.connection.host=52.89.106.226 --master spark://ip-172-31-1-85:7077 --executor-memory 14000M --driver-memory 14000M spark_stream.py
