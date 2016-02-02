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

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json, datetime
import sys



if __name__ == "__main__":
    sc = SparkContext(appName="PythonStreamingKafka")
    # ssc = StreamingContext(sc, 2)   # every 2 seconds
    ssc = StreamingContext(sc, 1)


    # topics = {'chicago': 1, 'nyc': 1}
    topics = {city: 1 for city in envir_vars.cities_lat_and_long.keys()}


    # zkQuorum = '52.89.106.226:2181,52.89.118.67:2181,52.34.130.78:2181,52.89.11.71:2181'
    kafka_machines = ['52.89.106.226', '52.89.118.67', '52.34.130.78', '52.89.11.71']
    zkQuorum = ','.join([m + ':2181' for m in kafka_machines])

    kafkaStream = KafkaUtils.createStream(ssc, zkQuorum, "GroupNameDoesntMatter", topics)
    # lines = kafkaStream.map(lambda x: json.loads(x[1]))
    lines = kafkaStream.map(lambda x: x[1])
    # lines.pprint()

    def get_useful_info(alerts):
        d = {}  # {(lat, lng): [type, subType]
        for alert in alerts:
            d.update({(alert['latitude'], alert['longitude']): [alert['type'], alert['subType'], alert['numOfThumbsUp']]})
        return d

    try:
        # alertofinterest = 'POLICE'
        # output = lines.map(lambda l: [alert for alert in json.loads(l)["alerts"] if alert['type'] == alertofinterest])
        # output = lines.map(lambda l: json.loads(l)["city"])
        # output.pprint()
        alerts_now = {}
        output = lines.map(lambda l: json.loads(l)["alerts"])   # a list of dicts
        alerts_now = output.map(get_useful_info)
        alerts_now.pprint()
    except Exception as e:
        # TODO log these to file, but don't let some corrupted json response crash it all
        print "ERROR: something bad happened", e

    ssc.start()
    ssc.awaitTermination()

    # counts = lines.flatMap(lambda line: line.split(" ")) \
        # .map(lambda word: (word, 1)) \
        # .reduceByKey(lambda a, b: a+b)
