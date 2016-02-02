#!/bin/bash

$SPARK_HOME/bin/spark-submit --executor-memory 14000M --driver-memory 14000M --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.0 spark_stream.py
