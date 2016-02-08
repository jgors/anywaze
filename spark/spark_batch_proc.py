#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 02-02-2016
# Purpose:  Does the actual processing of the data to be put into
#           cassandra
#----------------------------------------------------------------


import sys, os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
from envir_vars import hdfs_data_path, storage_cluster_ips, cassandra_keyspace

from pyspark import SparkConf, SparkContext, SQLContext
from cassandra.cluster import Cluster


# NOTE spark_master_hostname  ==  ip-172-31-1-85
# this way                                  {spark_master_hostname}
# $SPARK_HOME/bin/spark-submit --master spark://ip-172-31-1-85:7077 --packages TargetHolding/pyspark-cassandra:0.2.7 --executor-memory 14000M --driver-memory 14000M spark_batch_proc.py

''' from sesha
spark-submit
--master masterip
--packages org.apache.spark:spark-streaming-kafka_2.10:1.5.2,TargetHolding:pyspark-cassandra:0.2.4
'''


# NOTE this would be for running spark stand-alone (not spark interactive)
conf = (SparkConf()
         # .setMaster("local")
         # .set("spark.executor.memory", "1g")
         .setAppName("mysparkprocingjob")
       )
sc = SparkContext(conf=conf)
sc.addPyFile('../envir_vars.py')
sc_sql = SQLContext(sc)

data_path_in_hdfs = 'waze_data/topics/*/*'
hdfs_in_path =  hdfs_data_path.format(data_path_in_hdfs)
df = sc_sql.read.load(hdfs_in_path)

# What each cleaned up row looks like:
# [Row(city=u'atlanta', datetime=u'2016-01-25 08:35', lat=33.764181, lng=-84.371954,
#      numOfThumbsUp=1, subtype=u'POLICE_VISIBLE', time_stamp=1453710945, type=u'POLICE',
#      weekday=u'Monday')]

# p = df[df.type == 'POLICE']
# # another way
# p = df.filter(df.type == 'POLICE')


# do time based stuff the "spark way"
# from pyspark.sql import functions as sql_funcs
# hours = df.select(sql_funcs.hour(df.datetime))


def make_data_for_cassandra(row):
    year_month_day, hour_minute = row.datetime.split(' ')
    hour = int(hour_minute.split(':')[0])

    if not row.subtype:     # b/c some of the subtypes are just empty strings
        # row.subtype = row.type    # apparently can't do this b/c row is read only
        subtype = row.type
    else:
        subtype = row.subtype

    new_row = {'city': row.city,
               'type': row.type,
               'subtype':  subtype,
               'weekday': row.weekday,
               'year_month_day': year_month_day,
               'hour': hour
              }
    return new_row


rdd_data = df.map(make_data_for_cassandra)
new_df = rdd_data.toDF()

###  -->                             key is a tuple          and initially 1 for each thing      then add(/reduce) up all things that have similar keys
map_reduced_date_and_event = new_df.map(lambda r: ((r.year_month_day, r.city, r.type), 1)).reduceByKey(lambda a,b: a+b)
result_date_and_type = sorted(map_reduced_date_and_event.collect())
# result_date_and_type[0]  ==  ((u'2016-01-25', u'atlanta', u'ACCIDENT'), 97)


# map_reduced_date_and_city = new_df.map(lambda r: ((r.city, r.type, r.year_month_day, r.hour), 1)).reduceByKey(lambda a,b: a+b)
# result_date_and_city = sorted(map_reduced_date_and_city.collect())
# result_date_and_city[0]  ==  ((u'atlanta', u'ACCIDENT', u'2016-01-25', 10), 1)


map_reduced_date_and_city = new_df.map(lambda r: ((r.year_month_day, r.city, r.type, r.subtype), 1)).reduceByKey(lambda a,b: a+b)
result_date_and_city = sorted(map_reduced_date_and_city.collect())
# result_date_and_city[1]  ==  (( u'2016-01-25', u'atlanta', u'ACCIDENT', u'ACCIDENT_MAJOR'), 16)


##############################################
# NOTE to save to casandra, eg:
# $ cqlsh
# cqlsh> CREATE KEYSPACE waze WITH replication = {'class': 'SimpleStrategy', 'replication_factor':3};
# cqlsh> USE waze ;
# cqlsh:waze> CREATE TABLE ... (var1 timestamp, var2 list, var3 int, PRIMARY KEY (var1, var3));
'''
want daily aggregate for each type (POLICE) for each city (LA) for each date (1-11-16)
CREATE TABLE date_aggregation (
    date timestamp,
    event_type text
    city text,
    lat int,
    lon int
    PRIMARY KEY ((date, event_type))
);
SELECT * FROM date_aggregation WHERE date = '1-11-16'
                           AND event_type = 'POLICE'

within a date partition, rows will be ordered by event_type,
all event_types for a given date will be on the same node
'''

'''
def hand_off_to_cassandra(agg):
    from cassandra.cluster import Cluster
    if agg:
        cluster = Cluster(storage_cluster_ips)
        session = cluster.connect(cassandra_keyspace)
        for a in agg:
            cmd = 'INSERT INTO {tablename} (time, count, locations) VALUES (%s, %s, %s)'.format()
            session.execute(
                    # 'INSERT INTO sliding_window_batch (monitor, ts_start, time_total) VALUES (%s, %s, %s)', (agg_item[0], 0, agg_item[1]))
                    # 'INSERT INTO police (time_stamp, num_police, locations) VALUES (%s, %s, %s)', (agg_item[0], agg_item[1], agg_item[2]))
                    # 'INSERT INTO sanfranpolice (time, count) VALUES (%s, %s)', (agg_item[0], agg_item[1]))    # NOTE works
                    'INSERT INTO sanfranpolice (time, count, locations) VALUES (%s, %s, %s)', (a[0], a[1], a[2]))
                    # 'INSERT INTO police (time_stamp, num_police, locations) VALUES (%s, %s, %s)'.format(agg_item[0], agg_item[1], agg_item[2]))
        session.shutdown()
        cluster.shutdown()


# result.foreachPartition(hand_off_to_cassandra)
# hand_off_to_cassandra(result)
'''

cluster = Cluster(storage_cluster_ips)
session = cluster.connect(cassandra_keyspace)

# create keyspace (just do this once)
# session.execute("""CREATE KEYSPACE waze WITH replication = {'class':'SimpleStrategy', 'replication_factor':3};""")

# create table
# date and type displayed for all cities -- #1 on sheet
tablename = 'date_and_type'
cmd = """CREATE TABLE {tablename} (
    date text,
    type text,
    city text,
    count int,
    PRIMARY KEY ((type, date), city)
);""".format(tablename=tablename)

try:
    session.execute(cmd)
except Exception as e:
    print e

# https://datastax.github.io/python-driver/api/cassandra/cluster.html#cassandra.cluster.Session.prepare
query = 'INSERT INTO {} (date, type, city, count) VALUES (?, ?, ?, ?)'.format(tablename)
prepared = session.prepare(query)
for r in result_date_and_type:
    date, city, _type, count = r[0][0], r[0][1], r[0][2], r[1]
    session.execute(prepared, (date, _type, city, count))




# do the chart below instead of this one here
# create table
# date and city displayed for all types for all hours -- #2 on sheet
'''
tablename = 'date_and_city'
cmd = """CREATE TABLE {tablename} (
    date text,
    type text,
    city text,
    hour int
    count int,
    PRIMARY KEY ((type, date, hour), city)
);""".format(tablename=tablename)

try:
    session.execute(cmd)
except Exception as e:
    print e

query = 'INSERT INTO {} (date, type, city, count) VALUES (?, ?, ?, ?)'.format(tablename)
prepared = session.prepare(query)
for r in result_date_and_type:
    city, _type, date, count = r[0][0], r[0][1], r[0][2], r[1]
    session.execute(prepared, (date, _type, city, count))
'''




tablename = 'date_and_city'
cmd = """CREATE TABLE {tablename} (
    date text,
    city text,
    type text,
    subtype text,
    count int,
    PRIMARY KEY ((date, city), type, subtype)
);""".format(tablename=tablename)

try:
    session.execute(cmd)
except Exception as e:
    print e

query = 'INSERT INTO {} (date, city, type, subtype, count) VALUES (?, ?, ?, ?, ?)'.format(tablename)
prepared = session.prepare(query)
for r in result_date_and_city:
    date, city, _type, subtype, count = r[0][0], r[0][1], r[0][2], r[0][3], r[1]
    session.execute(prepared, (date, city, _type, subtype, count))






session.shutdown()
cluster.shutdown()