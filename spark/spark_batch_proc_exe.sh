#!/bin/bash

$SPARK_HOME/bin/spark-submit --master spark://ip-172-31-1-85:7077 --packages TargetHolding/pyspark-cassandra:0.2.7 --executor-memory 14000M --driver-memory 14000M spark_batch_proc.py $1
