#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-28-2016
# Purpose:
#----------------------------------------------------------------

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

spark_cluster_master = 'spark://ec2-54-69-163-111.us-west-2.compute.amazonaws.com:7077'
app_name_for_spark_ui = 'waze_data'
sc = SparkContext(spark_cluster_master, app_name_for_spark_ui)
ssc = StreamingContext(sc, 1)

# Create a DStream that will connect to hostname:port, like localhost:9999
lines = ssc.socketTextStream("localhost", 9999)
