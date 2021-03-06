#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-26-2016
# Purpose: create the kafka topics
#----------------------------------------------------------------

import subprocess
import sys, os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import envir_vars

# Kafka is started already (via peagus),
# now need to create the topics to be used (just do this on hdfs master):
# NOTE this will create 1 topic per city, with one partition per topic
replication_factor = 3
partitions = 1
cmd =  '/usr/local/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181'
cmd += ' --replication-factor {} --partitions {}'.format(replication_factor, partitions)

for city in envir_vars.cities_lat_and_long:
    city_specific_cmd = '{} --topic {}'.format(cmd, city)
    print city_specific_cmd
    sproc = subprocess.Popen(city_specific_cmd, stdout=subprocess.PIPE, shell=True)
    out, err = sproc.communicate()
    if err:
        print "ERROR:  something didn't work trying to create topic\n{}".format(city_specific_cmd)
