#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-30-2016
# Purpose:
#----------------------------------------------------------------


from kafka import KafkaConsumer
import json

consumer = KafkaConsumer('chicago',
                         group_id='my_group',
                         bootstrap_servers=['ec2-52-89-106-226.us-west-2.compute.amazonaws.com:9092'])
                         #ec2-52-89-106-226.us-west-2.compute.amazonaws.com


for message in consumer:
    # message value is raw byte string -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
    #print("{}:{}:{}: key={} value={}".format(message.topic, message.partition,
                                             #message.offset, message.key,
                                             #message.value))

    alerts = json.loads(message.value)['alerts']


########################
from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer
from kafka.producer import SimpleProducer
client = KafkaClient('ec2-52-89-106-226.compute-1.amazonaws.com:9092')

consumer = SimpleConsumer(client, "test-group", "gps")

for message in consumer:
    print(message)
