#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-21-2016
# Purpose:
#----------------------------------------------------------------

import sys, os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import envir_vars

from time import tzset, strftime, gmtime, timezone
from os import environ
from pyspark import SparkConf, SparkContext, SQLContext

# NOTE submit jobs to spark like so:
# this way
# $SPARK_HOME/bin/spark-submit --executor-memory 12000M --driver-memory 12000M spark_batch.py
# not this
# spark-submit --master spark://ip-172-31-1-87:7077 --packages TargetHolding/pyspark-cassandra:0.1.5 ~/wazted/spark/spark_batch.py

# to start the ipython spark repl
# IPYTHON=1 $SPARK_HOME/bin/pyspark --master spark://ip-172-31-1-70:7077
# doesn't work...not sure why:
# IPYTHON=1 $SPARK_HOME/bin/pyspark --master spark://ip-172-31-1-70:7077 --executor-memory 12000M --driver-memory 12000M


# NOTE this would be for running spark stand-alone (not spark interactive)
# sc = SparkContext("local", "App Name", pyFiles=['MyFile.py', 'lib.zip', 'app.egg'])
conf = (SparkConf()
         # .setMaster("local")
         .setAppName("mysparkjob")
         # .set("spark.executor.memory", "1g")
         )
sc = SparkContext(conf=conf)
sc.addPyFile('../envir_vars.py')
sc_sql = SQLContext(sc)

pub_dns = 'ec2-52-89-106-226.us-west-2.compute.amazonaws.com'   # this is the master node (where kafka is waiting)

cities = envir_vars.cities_lat_and_long.keys()
# cities = ['atlanta']
# cities = ['san-fran-small-wo-newline']
# topic = cities[0]
for city in cities:
    topic = city

    # For example:  camus/topics/san_fransisco/hourly/2016/01/21/10
    data_path_in_hdfs = 'camus/topics/{}/*/*/*/*/*'.format(topic)
    # data_path_in_hdfs = 'testing/{}'.format(topic)
    # data_path_in_hdfs = 'testing/{}/part-r-00184-f5234aaf-93dc-412a-8cea-ca6354e1f72f.gz.parquet'.format(topic)


    hdfs_data_path = "hdfs://{}:9000/{}"
    hdfs_inpath =  hdfs_data_path.format(pub_dns, data_path_in_hdfs)

    json_data = sc_sql.read.json(hdfs_inpath)
    # json_data.printSchema()

    # works
    # def get_alerts(row):
        # locations = []
        # for alert in row.alerts:
            # if alert.type == 'POLICE':
                # locations.append((alert.latitude, alert.longitude))
        # return (row.time_stamp, len(locations), locations)
    # result = json_data.map(get_alerts)


    def get_alerts(row):
        alerts = []
        for alert in row.alerts:
            # save back to hdfs below and then read those hdfs files back in later;

            # convert to proper date time for cassandra
            # https://docs.datastax.com/en/cql/3.0/cql/cql_reference/timestamp_type_r.html
            # yyyy-mm-dd HH:mm:ssZ
            # https://pymotw.com/2/time/#working-with-time-zones
            data_timezone = envir_vars.time_zones[city]
            if data_timezone == 'eastern':
                environ['TZ'] = 'US/Eastern'
                # dt += ':-0500'
            elif data_timezone == 'central':
                environ['TZ'] = 'US/Central'
                # dt += ':-0600'
            elif data_timezone == 'mountain':
                environ['TZ'] = 'US/Mountain'
                # dt += ':-0700'
            elif data_timezone == 'pacific':
                environ['TZ'] = 'US/Pacific'
                # dt += ':-0800'
            tzset()
            row_ts = row.time_stamp - timezone
            dt = strftime("%Y-%m-%d %H:%M", gmtime(row_ts))
            wkday = strftime("%A", gmtime(row_ts))

            row_reformatted = {'time_stamp': int(row_ts),
                               'datetime': dt,
                               'weekday': wkday,
                               'lat': float(alert.latitude), 'lng': float(alert.longitude),
                               'type': alert.type, 'subtype': alert.subType,
                               'city': row.city, # uncomment this for the real data
                               'numOfThumbsUp': alert.numOfThumbsUp}
            alerts.append(row_reformatted)
        return alerts


    alerts = json_data.map(get_alerts)
    afm = alerts.flatMap(lambda row: [alert for alert in row])
    # print afm.count()

    # afm.saveAsTextFile(hdfs_outpath)
    afm_df = afm.toDF()
    afm_df.cache()
    # afm_df.count()

    afm_df_deduped = afm_df.dropDuplicates(['lat', 'lng', 'type'])
    afm_df_deduped_sorted = afm_df_deduped.sort('time_stamp')#.collect()
    # print afm_df_deduped_sorted.count()


    # For saving
    # data_path_out_hdfs = 'testing/{}/'.format(topic)
    data_path_out_hdfs = 'waze_data/topics/{}/'.format(topic)
    hdfs_outpath = hdfs_data_path.format(pub_dns, data_path_out_hdfs)
    #
    # For df's:
    afm_df_deduped_sorted.write.save(hdfs_outpath)
    # NOTE and then read back in w/
    # data_path_in_hdfs = 'waze_data/topics/{}/*'.format(city)
    # hdfs_data_path = "hdfs://{}:9000/{}"
    # hdfs_inpath =  hdfs_data_path.format(pub_dns, data_path_in_hdfs)
    # df = sqlContext.read.load(hdfs_inpath)
    #
    # For rdd's:
    # afm_df_deduped_sorted.rdd.saveAsTextFile(hdfs_outpath)
    # afm_df_deduped_sorted.rdd.saveAsHadoopFile(hdfs_outpath)

raise SystemExit



##############################################
# NOTE to save to casandra
# NOTE make the table outside of this script somewhere (using cassandra on cmdline like in
# the cassandra tmux pane) like (in cassandra shell):
# $ cqlsh
# CREATE KEYSPACE waze WITH replication = {'class': 'SimpleStrategy', 'replication_factor':3};
#
# cqlsh> USE waze ;
# cqlsh:waze> CREATE TABLE sanfranpolice (time timestamp, count int, PRIMARY KEY (time, count));    # worked
# want something like this though
# cqlsh:waze> CREATE TABLE sanfranpolice (time timestamp, locations list, count int, PRIMARY KEY (time, count));

# do this from inside python:
# https://sites.google.com/a/insightdatascience.com/dataengineering/devsetups

'''
# his example
CREATE TABLE daily_location_aggregate (
    event_time timestamp,
    spot_name text,
    availability int,
    lat int,
    lon int
    PRIMARY KEY ( (event_time, spot_name) )
);


# mine
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
                           AND WHERE event_type = 'POLICE'

within a date partition, rows will be ordered by event_type
all event_types for a given date will be on the same node
'''

def create_schema(session):
    # session.execute("""CREATE KEYSPACE waze WITH replication = {'class':'SimpleStrategy', 'replication_factor':3};""")
    # want daily aggregate for each type (POLICE) for each city (LA) for each date (1-11-16)
    session.execute("""
        CREATE TABLE date_aggregation (
            date timestamp,
            event_type text
            city text,
            lat int,
            lon int
            PRIMARY KEY ((date, event_type))
        );
    """)


def hand_off_to_cassandra(agg):
    from cassandra.cluster import Cluster
    if agg:
        cluster = Cluster(['52.89.106.226', '52.89.118.67', '52.34.130.78', '52.89.11.71'])
        # session = cluster.connect(topic)
        # session = cluster.connect('san_fran_small_wo_newline_police')
        # session = cluster.connect('sanfranpolice')
        session = cluster.connect('waze')
        for a in agg:
            session.execute(
                    # 'INSERT INTO sliding_window_batch (monitor, ts_start, time_total) VALUES (%s, %s, %s)', (agg_item[0], 0, agg_item[1]))
                    # 'INSERT INTO police (time_stamp, num_police, locations) VALUES (%s, %s, %s)', (agg_item[0], agg_item[1], agg_item[2]))
                    # 'INSERT INTO sanfranpolice (time, count) VALUES (%s, %s)', (agg_item[0], agg_item[1]))    # NOTE works
                    'INSERT INTO sanfranpolice (time, count, locations) VALUES (%s, %s, %s)', (a[0], a[1], a[2]))
                    # 'INSERT INTO police (time_stamp, num_police, locations) VALUES (%s, %s, %s)'.format(agg_item[0], agg_item[1], agg_item[2]))
        session.shutdown()
        cluster.shutdown()

result.foreachPartition(hand_off_to_cassandra)


'''
from cassandra.cluster import Cluster
cluster = Cluster(['52.89.106.226', '52.89.118.67', '52.34.130.78', '52.89.11.71'])
session = cluster.connect(topic)
session.execute(
        'INSERT INTO sanfranpolice (time_stamp, num_police, locations) VALUES (%s, %s, %s)', (agg_item[0], agg_item[1], agg_item[2]))
'''

'''
create a group for each city
'''
