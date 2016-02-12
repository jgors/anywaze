#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-27-2016
# Purpose: to change how long kafka keeps stuff in each topic
# http://stackoverflow.com/questions/29129222/changing-kafka-rentention-period-during-runtime
# http://www.convertunits.com/from/month/to/millisecond
#----------------------------------------------------------------
import subprocess
import os, sys
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
import envir_vars

# ms_to_save = 2629746000     # ms_in_a_month
ms_to_save = 129599999  # ms_in_one_and_a_half_days



for city in envir_vars.cities_lat_and_long.keys():
    cmd = '$KAFKA_HOME/bin/kafka-topics.sh --zookeeper localhost:2181'
    cmd += ' --alter --topic {} --config retention.ms={}'.format(city, ms_to_save)
    sproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = sproc.communicate()
    print out
    if err:
        print "ERROR:  something didn't work trying to change retention with:\n{}".format(cmd)
