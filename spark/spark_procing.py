#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-21-2016
# Purpose:
#----------------------------------------------------------------

from pyspark import SparkConf, SparkContext, SQLContext
import pyspark

# NOTE submit jobs to spark like so (this would be for a scala script):
# $ spark-submit --class price_data --master spark://master_hostname:7077 target/scala-2.10/price_data_2.10-1.0.jar
# or
# $ cd $SPARK_HOME
# $ ./bin/pyspark SimpleApp.py

# to start the ipython spark repl
# IPYTHON=1 $SPARK_HOME/bin/pyspark --master spark://ip-172-31-1-70:7077
# doesn't work...not sure why:
# IPYTHON=1 $SPARK_HOME/bin/pyspark --master spark://ip-172-31-1-70:7077 --executor-memory 6000M --driver-memory 6000M

# NOTE this would be for running spark stand-alone (not spark interactive)
# sc = SparkContext("local", "App Name", pyFiles=['MyFile.py', 'lib.zip', 'app.egg'])
conf = (SparkConf()
         # .setMaster("local")
         .setAppName("jg_sparkjob_1")
         # .set("spark.executor.memory", "1g")
         )
sc = SparkContext(conf=conf)
sc = SQLContext(sc)





import json
from pyspark import SQLContext
# from pyspark.sql import SQLContext    # same thing

pub_dns = 'ec2-52-89-106-226.us-west-2.compute.amazonaws.com'   # this is the master node (where kafka is waiting)
topic = 'san-fran-small-wo-newline'

# For example:  /camus/topics/san-fransisco/hourly/2016/01/21/10
# data_path_on_hdfs = '/camus/topics/*/*/*/*/*/*'
# data_path_on_hdfs = '/camus/topics/san-fransisco/*/*/*/*/*'
data_path_on_hdfs = '/camus/topics/{}/*/*/*/*/*'.format(topic)

data_path = "hdfs://{}:9000/{}".format(pub_dns, data_path_on_hdfs)


#################################
# NOTE not using this
# f = sc.textFile("hdfs://<public_dns>:9000/user/test.txt")
rdd = sc.textFile(data_path)#.cache()
# rdd_dicts = rdd.map(json.loads)
rdd_dicts = rdd.map(lambda ln: json.loads(ln))
# jd = json_dict.take(1)
# police = [alert for alert in jd[0]['alerts'] if alert['type']=='POLICE']

alerts = rdd_dicts.map(lambda x: x['alerts'])
print alerts.take(1)

alerts = rdd_dicts.map(lambda x: x['alerts']).filter(lambda x: x=='POLICE')
# police = alerts.filter(lambda x: x['type']=='POLICE')
# print police.take(1)
print alerts.take(1)
#################################



##############################
# NOTE coded this w/ Austin -- NOTE works!!!!
sc_sql = SQLContext(sc)
# json_data = sc_sql.jsonFile(data_path)
json_data = sc_sql.read.json(data_path)

# j_first = json_data.take(1)
# type(j_first[0])  # each entry is a pyspark.sql.types.Row object

# row = json_data.first()
# print row.time_stamp
# for alert in row.alerts:
    # if alert.type == 'POLICE':
        # # return i.latitude
        # print alert

def get_alerts(row):
    locations = []
    for alert in row.alerts:
        if alert.type == 'POLICE':
            locations.append((alert.latitude, alert.longitude))
    return (row.time_stamp, len(locations), str(locations))     # FIXME don't do this hacky locations str conversion -- figure out how to pass collections into cassandra

result = json_data.map(get_alerts)

# r1 = result.take(1)
# type(r1) is list
##############################



#########################
# sql_sc = SQLContext(sc)
# json_data = sql_sc.jsonFile(data_path)
# jd_1 = json_data.take(1)[0]
# alerts = jd_1.__getattr__('alerts')
# alerts_rdd = sc.parallelize(alerts)
# police_alerts = alerts_rdd.filter(lambda x: x.type=='POLICE')
# police_alerts.count()


# def my_func(jd):
    # time_stamp = jd.__getattr__('time_stamp')
    # alerts = jd.__getattr__('alerts')
    # return time_stamp, alerts

    # alerts_rdd = sc.parallelize(alerts)
    # police_alerts = alerts_rdd.filter(lambda x: x.type=='POLICE').map(lambda a: (time_stamp, a))
    # # police_alerts_cnt = police_alerts.count()
    # return police_alerts


# sql_sc = SQLContext(sc)
# json_data = sql_sc.jsonFile(data_path)
# police_alerts = json_data.map(my_func)
# police_alerts.take(1)#.count()

# alerts = [i for i in json_data.take(1)[0].__getattr__('alerts') if i['type']=='POLICE'] #[0]#.__getattr__('type')
# x = [i for i in json_data.take(1)[0].__getattr__('alerts')[i]]#.__getattr__('type')
# x = json_data.take(1)[0].__getattr__('alerts')
#########################


# from the tutorial example
# counts = file.flatMap(lambda line: line.split(" "))\
       # .map(lambda word: (word, 1))\
       # .reduceByKey(lambda a, b: a + b)

# res = counts.collect()
# for val in res:
    # print val






##############################################
# NOTE to save to casandra
# NOTE make the table outside of this script somewhere (using cassandra on cli like in cassandra tmux pane) like:
# in cassandra shell
# $ cqlsh
# CREATE KEYSPACE waze WITH replication = {'class': 'SimpleStrategy', 'replication_factor':3};
# cqlsh> USE waze ;
# cqlsh:waze> CREATE TABLE sanfranpolice (time timestamp, count int, PRIMARY KEY (time, count));    # worked
# want something like this though
# cqlsh:waze> CREATE TABLE sanfranpolice (time timestamp, locations list, count int, PRIMARY KEY (time, count));

# do this from inside python:
# https://sites.google.com/a/insightdatascience.com/dataengineering/devsetups

def agg_to_cassandra_part(agg):
    from cassandra.cluster import Cluster
    if agg:
        cluster = Cluster(['52.89.106.226', '52.89.118.67', '52.34.130.78', '52.89.11.71'])
        # session = cluster.connect(topic)
        # session = cluster.connect('san_fran_small_wo_newline_police')
        # session = cluster.connect('sanfranpolice')
        session = cluster.connect('waze')
        for agg_item in agg:
            session.execute(
                    # 'INSERT INTO sliding_window_batch (monitor, ts_start, time_total) VALUES (%s, %s, %s)', (agg_item[0], 0, agg_item[1]))
                    # 'INSERT INTO police (time_stamp, num_police, locations) VALUES (%s, %s, %s)', (agg_item[0], agg_item[1], agg_item[2]))
                    # 'INSERT INTO sanfranpolice (time, count) VALUES (%s, %s)', (agg_item[0], agg_item[1]))    # NOTE works
                    'INSERT INTO sanfranpolice (time, count, locations) VALUES (%s, %s, %s)', (agg_item[0], agg_item[1], agg_item[2]))
                    # 'INSERT INTO police (time_stamp, num_police, locations) VALUES (%s, %s, %s)'.format(agg_item[0], agg_item[1], agg_item[2]))
        session.shutdown()
        cluster.shutdown()
result.foreachPartition(agg_to_cassandra_part)

'''
from cassandra.cluster import Cluster
cluster = Cluster(['52.89.106.226', '52.89.118.67', '52.34.130.78', '52.89.11.71'])
session = cluster.connect(topic)
session.execute(
        'INSERT INTO sanfranpolice (time_stamp, num_police, locations) VALUES (%s, %s, %s)', (agg_item[0], agg_item[1], agg_item[2]))
'''

