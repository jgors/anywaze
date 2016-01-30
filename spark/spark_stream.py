#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-28-2016
# Purpose:
#----------------------------------------------------------------


import sys
import json
from pyspark import SparkContext, SparkConf
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SQLContext, Row
from pyspark.sql.types import *
# from cassandra.cluster import Cluster
# from cassandra import ConsistencyLevel



def process(rdd):
    # rdd.foreachPartition(lambda record: write_into_cassandra(record))
    print rdd

topic = "nyc"
# topic = 'san-fran-small-wo-newline'

# spark_cluster_master = 'spark://ec2-54-69-163-111.us-west-2.compute.amazonaws.com:7077'
appname_for_spark_ui = 'waze_data'
# sc = SparkContext(spark_cluster_master, app_name_for_spark_ui)
sc = SparkContext(appName=appname_for_spark_ui)

ssc = StreamingContext(sc, 2)

kafka_machines = ['52.89.106.226', '52.89.118.67', '52.34.130.78', '52.89.11.71']
# spark_machines = ['54.69.163.111', '54.69.140.82', '54.69.108.204', '54.69.162.20']
zkQuorum = ','.join([m + ':2181' for m in kafka_machines])
kvs = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic: 1})
lines = kvs.map(lambda x: x[1])



# sc_sql = SQLContext(sc)
# json_data = sc_sql.read.json(lines)

# def get_alerts(row):
    # locations = []
    # for alert in row.alerts:
        # locations.append({alert.latitude, alert.longitude})
    # # return (row.time_stamp, len(locations), str(locations))
    # return locations

# result = json_data.map(get_alerts)
alertofinterest = 'POLICE'
output = lines.map(lambda l: json.loads(l)["alerts"])#\
# output = lines.filter(lambda l: alertofinterest in json.loads(l)["alerts"]['type'])#\
    # .filter(lambda l: len(json.loads(l)["place"]["name"]) > 0 )\
    # .filter(lambda l: len(json.loads(l)["place"]["country_code"]) > 0)\
    # .map(lambda l: ( (json.loads(l)["place"]["name"], json.loads(l)["place"]["country_code"] ), 1))\
    # .reduceByKey(lambda a,b: a+b)

output.pprint()

# output.foreachRDD(citycount_to_cassandra)




ssc.start()
ssc.awaitTermination()
