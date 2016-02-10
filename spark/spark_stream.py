#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-30-2016
# Purpose:
#----------------------------------------------------------------

"""Run with:
sh spark_stream_exe.sh
"""

import sys, os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import envir_vars

import json

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from cassandra.cluster import Cluster

import pyspark_cassandra
from pyspark_cassandra import streaming
# from pyspark import SparkContext, SparkConf
# from pyspark.streaming import StreamingContext
# from pyspark.streaming.kafka import KafkaUtils


# cluster = Cluster(envir_vars.storage_cluster_ips)
# session = cluster.connect(envir_vars.cassandra_keyspace)


if __name__ == "__main__":
    sc = SparkContext(appName="PythonStreamingKafka")
    ssc = StreamingContext(sc, 2)   # every 2 seconds

    # topics = {'chicago': 1, 'nyc': 1}
    topics = {city: 1 for city in envir_vars.cities_lat_and_long.keys()}

    kafka_machines = envir_vars.storage_cluster_ips
    zkQuorum = ','.join([m + ':2181' for m in kafka_machines])

    kafkaStream = KafkaUtils.createStream(ssc, zkQuorum, "GroupNameDoesntMatter", topics)
    # lines = kafkaStream.map(lambda x: json.loads(x[1]))
    lines = kafkaStream.map(lambda x: x[1])
    # lines.pprint()

    def get_useful_info(row):
        # d = {}  # {(lat, lng): [type, subType]
        # for alert in alerts:
            # d.update({(alert['latitude'], alert['longitude']): [alert['type'], alert['subType'], alert['numOfThumbsUp']]})
        # return d
        alerts_new = []
        for alert in row['alerts']:
            alerts_new.append({'city': row['city'], 'type': alert['type'], 'subtype': alert['subType'],
                               # made this lowercase b/c cassandra column names seem to only allow lowercase
                               'numofthumbsup': int(alert['numOfThumbsUp']),
                               'lat': alert['latitude'], 'lng': alert['longitude'],
                               })
        return alerts_new


    output = lines.map(lambda l: json.loads(l))   # a list of dicts
    # output.pprint()

    alerts_now = output.map(get_useful_info)
    # alerts_now.pprint()

    afm = alerts_now.flatMap(lambda row: [alert for alert in row])
    # afm.pprint()

    tablename = 'realtime'
    seconds = 900  # 15min    # 86400 # in one day

    # This would be for doing realtime hotspots:
    # CREATE TABLE realtime (city text, type text, subtype text, numOfThumbsUp int,
    #                        lat float, lng float,
    #                        PRIMARY KEY ((city, type), subtype, lat, lng));

    # This would be for a doing realtime map of everything -- like waze actually does:
    # CREATE TABLE realtime (city text, type text, subtype text, numOfThumbsUp int,
    #                        lat float, lng float,
    #                        PRIMARY KEY ((city), type, subtype, lat, lng));

    afm.foreachRDD(lambda rdd: rdd.saveToCassandra(
                            envir_vars.cassandra_keyspace, tablename, ttl=seconds))

    ssc.start()
    ssc.awaitTermination()
