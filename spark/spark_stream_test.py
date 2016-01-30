#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-30-2016
# Purpose:
#----------------------------------------------------------------


 # kafkaStream = KafkaUtils.createStream(streamingContext,
         # [ZK quorum],
         # [consumer group id],
         # [per-topic number of Kafka partitions to consume])


from __future__ import print_function

import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


if __name__ == "__main__":

    sc = SparkContext(appName="PythonStreamingKafka")
    ssc = StreamingContext(sc, 1)

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
