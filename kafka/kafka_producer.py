#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-20-2016
# Purpose:
#----------------------------------------------------------------

import argv
import json
import kafka

city, topic = argv[1]

# city = 'philly.txt'
# topic = 'philly-test'
# datafile = 'San_Francisco_old.txt'
# topic = 'san-fran-small-wo-newline'
# datafile = 'San_Francisco.txt'
# topic = 'san-francisco'

# connect to Kafka Cluster
# cluster = kafka.KafkaClient("localhost:9092")     # for running the kafka producer on the same node as the master node
# cluster = kafka.KafkaClient("ec2-52-89-106-226.us-west-2.compute.amazonaws.com:9092")
kafka_nodes = ['{}:9092'.format(node) for node in ["52.89.106.226", '52.89.11.71', '52.34.130.78', '52.89.118.67']]
cluster = kafka.KafkaClient(kafka_nodes)    # to send from somewhere remote into the aws kafka cluster

prod = kafka.SimpleProducer(cluster, async=False)


# produce msgs
datafile = '../../waze_test_data/waze_data/philly.txt'
# datafile = '/home/ubuntu/data_raw/{}'.format(city)

for msg in open(datafile, 'r'):
    msg = msg.strip()   # b/c of a newline char i put at the end
    # d = json.loads(msg)
    # prod.send_messages(topic, json.dumps(d))

    prod.send_messages(topic, msg)  # just send the string instead of dict


