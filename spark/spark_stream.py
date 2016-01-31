#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-30-2016
# Purpose:
#----------------------------------------------------------------

"""Run with:
$SPARK_HOME/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.0 spark_stream_test.py
"""

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json, datetime
import sys



if __name__ == "__main__":
    sc = SparkContext(appName="PythonStreamingKafka")
    ssc = StreamingContext(sc, 2)   # every 2 seconds


    # topic = 'chicago'
    kafka_machines = ['52.89.106.226', '52.89.118.67', '52.34.130.78', '52.89.11.71']
    zkQuorum = ','.join([m + ':2181' for m in kafka_machines])
    # zkQuorum = '52.89.106.226:2181,52.89.118.67:2181,52.34.130.78:2181,52.89.11.71:2181'
    topics = {'chicago': 1}
    kafkaStream = KafkaUtils.createStream(ssc, zkQuorum, "GroupNameDoesntMatter", topics) #{topic: 1})
    # lines = kafkaStream.map(lambda x: json.loads(x[1]))
    lines = kafkaStream.map(lambda x: x[1].strip())
    # lines.pprint()

    alertofinterest = 'POLICE'
    output = lines.map(lambda l: json.loads(l)["alerts"])
    output.pprint()
    print

    ssc.start()
    ssc.awaitTermination()




    '''
    zkQuorum, topic = '52.89.106.226', 'nyc'
    kvs = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic: 1})
    lines = kvs.map(lambda x: x[1])
    # counts = lines.flatMap(lambda line: line.split(" ")) \
        # .map(lambda word: (word, 1)) \
        # .reduceByKey(lambda a, b: a+b)
    alerts = lines.map(lambda line: line.alerts)
    alerts.pprint()

    ssc.start()
    ssc.awaitTermination()
    '''
