#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-21-2016
# Purpose:
#----------------------------------------------------------------

# import json
# import pyspark
from pyspark import SparkConf, SparkContext, SQLContext

# NOTE submit jobs to spark like so:
# spark-submit --master spark://ip-172-31-1-87:7077 --packages TargetHolding/pyspark-cassandra:0.1.5 ~/wazted/spark/spark_batch.py
# or
# $ cd $SPARK_HOME
# $ ./bin/pyspark SimpleApp.py

# NOTE this works to run it

# to start the ipython spark repl
# IPYTHON=1 $SPARK_HOME/bin/pyspark --master spark://ip-172-31-1-70:7077
# doesn't work...not sure why:
# IPYTHON=1 $SPARK_HOME/bin/pyspark --master spark://ip-172-31-1-70:7077 --executor-memory 12000M --driver-memory 12000M


# NOTE this would be for running spark stand-alone (not spark interactive)
# sc = SparkContext("local", "App Name", pyFiles=['MyFile.py', 'lib.zip', 'app.egg'])
conf = (SparkConf()
         # .setMaster("local")
         .setAppName("sparkjob_1")
         # .set("spark.executor.memory", "1g")
         )
sc = SparkContext(conf=conf)
# sc_sql = SQLContext(sc)





# NOTE START FROM HERE
# from pyspark.sql import SQLContext    # same thing
# from pyspark import SQLContext

topic = 'san-fran-small-wo-newline'
pub_dns = 'ec2-52-89-106-226.us-west-2.compute.amazonaws.com'   # this is the master node (where kafka is waiting)

# For example:  /camus/topics/san-fransisco/hourly/2016/01/21/10
# data_path_on_hdfs = '/camus/topics/*/*/*/*/*/*'     # everything
# data_path_on_hdfs = '/camus/topics/san-fransisco/*/*/*/*/*'
# data_path_on_hdfs = '/camus/topics/chicago/hourly/2016/01/28/06/*'
data_path_on_hdfs = '/camus/topics/{}/*/*/*/*/*'.format(topic)

data_path = "hdfs://{}:9000/{}".format(pub_dns, data_path_on_hdfs)



#################################
# NOTE not using this
'''
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
'''
#################################



##############################
# works
sc_sql = SQLContext(sc)
json_data = sc_sql.read.json(data_path)
# json_data = sc_sql.jsonFile(data_path)

# json_data.printSchema()

# j_first = json_data.take(1)
# type(j_first[0])  # each entry is a pyspark.sql.types.Row object

# row = json_data.first()
# print row.time_stamp
# for alert in row.alerts:
    # if alert.type == 'POLICE':
        # # return i.latitude
        # print alert

# def func(a):
    # pass
# something = json_data.map(lambda a: (a.latitude, a.longitude, a.type), x.time_stamp)


# works
# def get_alerts(row):
    # locations = []
    # for alert in row.alerts:
        # if alert.type == 'POLICE':
            # locations.append((alert.latitude, alert.longitude))
    # return (row.time_stamp, len(locations), locations)

# result = json_data.map(get_alerts)









# data_path_on_hdfs = '/camus/topics/chicago/hourly/2016/01/28/06/*'
# data_path_on_hdfs = '/waze_data/topics/{}/'.format(topic)
data_path_out_hdfs = '/testing/{}/'.format(topic)
hdfs_outpath = "hdfs://{}:9000/{}".format(pub_dns, data_path_out_hdfs)

def get_alerts(row):
    alerts = []
    for alert in row.alerts:
        # if alert.type == 'POLICE':
        # TODO save back to hdfs here and then read those hdfs files back in further down
        # in this script.  so each line would look like:
        # {'time_stamp': 1234345, 'lat': 2342, 'lon': 1234, 'type': 'police', 'subtype': 'hidden_police'}
        # row_reformatted = [('time_stamp', row.time_stamp),
                            # ('lat', alert.latitude), ('lon', alert.longitude),
                            # ('type', alert.type), ('subtype', alert.subType)]
        row_reformatted = {'time_stamp': float(row.time_stamp),     # NOTE should make this a float here or later?
                           'lat': float(alert.latitude), 'lon': float(alert.longitude),
                           # 'lat_and_lon': (alert.latitude, alert.longitude),
                           'type': alert.type, 'subtype': alert.subType,
                           # 'city': row.city, # TODO uncomment this for the real data
                           'numOfThumbsUp': alert.numOfThumbsUp}
        alerts.append(row_reformatted)
        # df = sc_sql.createDataFrame(row_reformatted)
        # df.saveAsTextFile(hdfs_outpath)
        # locations.update({(alert.latitude, alert.longitude): row.time_stamp})
        # print row_reformatted
    return alerts


result = json_data.map(get_alerts)
rfm = result.flatMap(lambda row: [alert for alert in row])
# rfm.saveAsTextFile(hdfs_outpath)  # this would be what i'd want NOTE it works

# output = sc_sql.createDataFrame(rfm)
# result.saveAsTextFile(hdfs_outpath)

rfm_df = rfm.toDF()
rfm_df.cache()
# rfm_df.checkpoint()

# rfm_df.count()
# rfm_df_dedup_1 = rfm_df.dropDuplicates(['lat_and_lon'])
rfm_df_deduped = rfm_df.dropDuplicates(['lat', 'lon', 'type'])
print rfm_df_deduped.sort('time_stamp').collect()


# maybe something like this?
# result = json_data.select(json_data.alerts)
# result_new = result.flatMap(lambda r: r)


# def func(row):
    # d_merged = {}
    # for d in row:
        # d_merged.update(d)

# result = json_data.map(get_alerts).map(func)




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




raise SystemExit

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
