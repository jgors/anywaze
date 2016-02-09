#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-21-2016
# Purpose:  this script just does preprocing of the data; the
#           interesting processing and handing-off of the data
#           to Cassandra is in different files.
#----------------------------------------------------------------

import sys, os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import envir_vars
from envir_vars import hdfs_data_path, time_zones

from time import tzset, strftime, gmtime, timezone
from os import environ
from pyspark import SparkConf, SparkContext, SQLContext

# NOTE submit jobs to spark like so:
# NOTE spark_master_hostname  == ip-172-31-1-85
# this way:
# $SPARK_HOME/bin/spark-submit --master spark://{spark_master_hostname}:7077 --executor-memory 14000M --driver-memory 14000M spark_batch_preproc.py
# or with specify libs:
# spark-submit --master spark://{spark_master_hostname}:7077 --packages TargetHolding/pyspark-cassandra:0.1.5 ~/wazted/spark/spark_batch_preproc.py

# to start the ipython spark repl
# IPYTHON=1 $SPARK_HOME/bin/pyspark --master spark://{spark_master_hostname}:7077
# doesn't work...not sure why:
# IPYTHON=1 $SPARK_HOME/bin/pyspark --master spark://{spark_master_hostname}:7077 --executor-memory 14000M --driver-memory 14000M


# NOTE this would be for running spark stand-alone (not spark interactive)
# sc = SparkContext("local", "App Name", pyFiles=['MyFile.py', 'lib.zip', 'app.egg'])
conf = (SparkConf()
         # .setMaster("local")
         # .set("spark.executor.memory", "1g")
         .setAppName("mysparkpreprocingjob")
       )
sc = SparkContext(conf=conf)
sc.addPyFile('../envir_vars.py')
sc_sql = SQLContext(sc)


cities = envir_vars.cities_lat_and_long.keys()
# cities = ['san-fran-small-wo-newline']
# topic = cities[0]
cities = ['cincinnati']
for city in cities:
    topic = city

    # Fpr example:  camus/topics/san_fransisco/hourly/2016/01/21/10
    data_path_in_hdfs = 'camus/topics/{}/*/*/*/*/*'.format(topic)
    # data_path_in_hdfs = 'testing/{}'.format(topic)
    # data_path_in_hdfs = 'testing/{}/part-r-00184-f5234aaf-93dc-412a-8cea-ca6354e1f72f.gz.parquet'.format(topic)

    hdfs_in_path =  hdfs_data_path.format(data_path_in_hdfs)

    json_data = sc_sql.read.json(hdfs_in_path)
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
            # save back to hdfs below and then read those hdfs files back in later after preprocing;

            # convert to proper date time for cassandra
            # https://docs.datastax.com/en/cql/3.0/cql/cql_reference/timestamp_type_r.html
            # yyyy-mm-dd HH:mm:ssZ
            # https://pymotw.com/2/time/#working-with-time-zones
            data_timezone = time_zones[city]
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

    # afm.saveAsTextFile(hdfs_out_path)
    afm_df = afm.toDF()
    afm_df.cache()
    # afm_df.count()

    afm_df_deduped = afm_df.dropDuplicates(['lat', 'lng', 'type'])
    afm_df_deduped_sorted = afm_df_deduped.sort('time_stamp')#.collect()
    # print afm_df_deduped_sorted.count()


    # For saving
    # data_path_out_hdfs = 'testing/{}/'.format(topic)
    # data_path_out_hdfs = 'waze_data/topics/{}/'.format(topic)     # old data
    data_path_out_hdfs = 'waze/topics/{}/'.format(topic)       # new data
    hdfs_out_path = hdfs_data_path.format(data_path_out_hdfs)
    #
    # For df's:
    afm_df_deduped_sorted.write.save(hdfs_out_path)
    # NOTE and then read back in w/
    # data_path_in_hdfs = 'waze_data/topics/{}/*'.format(city)
    # hdfs_in_path =  hdfs_data_path.format(data_path_in_hdfs)
    # df = sc_sql.read.load(hdfs_in_path)
    #
    # For rdd's:
    # afm_df_deduped_sorted.rdd.saveAsTextFile(hdfs_out_path)
    # afm_df_deduped_sorted.rdd.saveAsHadoopFile(hdfs_out_path)


