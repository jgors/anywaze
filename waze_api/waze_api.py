#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-14-2016
# Purpose: to get waze data from lots of cities;
#          script takes a single city as an arg and starts a subprocess
#          submitting a curl request through the webserver, which hits
#          the waze/google servers and returns back a json dict of the
#          events for that given city.
#----------------------------------------------------------------

from subprocess import Popen, PIPE
import json
import time
import os
import smtplib
import sys
import socket
from datetime import datetime
from math import cos, pi

parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
from envir_vars import cities_lat_and_long, me

area = sys.argv[1]


def compute_sides(lat1, lon1, miles=10):
    '''Alg from: http://gis.stackexchange.com/a/2980'''
    d = {}

    # Earth's radius, sphere -- # R = 6378137 in meters
    R = 6378.137 # km

    # to go NORTH -- dn on, de to 0
    # to go EAST -- dn to 0, de on
    # to go WEST -- dn to 0, de on with negative
    # to go SOUTH -- dn on with negative, de to 0
    km = miles * 1.609344       # turn miles arg into km
    for direction in ['N', 'S', 'E', 'W']:
        if direction == "N":
            dn, de = km, 0
        elif direction == "E":
            dn, de = 0, km
        elif direction == "W":
            dn, de = 0, -(km)
        elif direction == "S":
            dn, de = -(km), 0

        # Coordinate offsets in radians
        dLat = dn / R
        dLon = de / (R*cos(pi * lat1/180.))

        # OffsetPosition, decimal degrees
        lat2 = lat1 + dLat * 180./pi
        lon2 = lon1 + dLon * 180./pi

        if direction == "N":
            d['lat_top'] = lat2
        elif direction == "E":
            d['long_right'] = lon2
        elif direction == "W":
            d['long_left'] = lon2
        elif direction == "S":
            d['lat_bot'] = lat2
    return d


def email_me_on_failure(msg, issue, area=area):
    FROM = "{}@gmail.com".format(me)
    TO = ["{}.work@gmail.com".format(me)]
    SUBJECT = "{} for {} data".format(issue, area)
    MESSAGE = """From: mylogger <{}>
To: otherme <{}>
Subject: {}
{}""".format(FROM, TO, SUBJECT, msg)

    try:
        server = smtplib.SMTP("localhost")
        server.sendmail(FROM, TO, MESSAGE)
        server.quit()
    except Exception as e:
        email_logfile = '{}/email_fail_log.txt'.format(logs_dir)
        writetype = 'a' if os.path.exists(email_logfile) else 'w'
        with open(email_logfile, writetype) as email_log:
            msg = "ERROR: Exception {}: unable to send email to report {}".format(e, msg)
            email_log.write(msg+'\n')


def make_dir_if_not_exists(d):
    if not os.path.exists(d):
        os.mkdir(d)



cities = cities_lat_and_long.keys()
if area not in cities:
    print "ERROR: need to pass in single argument to choose a city from:\n {}".format(cities)
    raise SystemExit

lat, lon = cities_lat_and_long[area]
lats_and_longs = compute_sides(lat, lon)
# print lats_and_longs
# raise SystemExit

# for c in cities:
    # lat, lon = cities_lat_and_long[c]
    # print c, compute_sides(lat, lon)



hostname = socket.gethostname()
vis_break = '*'*40
cmd = 'curl -v "http://localhost:8080/waze/traffic-notifications?latBottom={lat_bot}&latTop={lat_top}&lonLeft={long_left}&lonRight={long_right}"'.format(**lats_and_longs)
cmd += ' -H "Accept: application/json"'

data_dir = './waze_data'
make_dir_if_not_exists(data_dir)
output_file = '{}/{}.txt'.format(data_dir, area)
writetype = 'a' if os.path.exists(output_file) else 'w'
# writetype = lambda f: 'a' if os.path.exists(f) else 'w'

logs_dir = './logs'
make_dir_if_not_exists(logs_dir)
logfile = open('{}/{}_log.txt'.format(logs_dir, area), 'w')

with open(output_file, writetype) as outfile:
    tries = 0
    while tries <= 20:
        print vis_break
        current_ts = time.time()
        now_time = datetime.now()

        sproc = Popen(cmd, stdout=PIPE, shell=True)
        out, err = sproc.communicate()
        if err:
            msg = "{}; {}; {}; curl ERROR {}\n".format(hostname, now_time, area, err)
            logfile.write(msg)
            if tries == 15:
                # don't email me right away...give it a some tries before doing so
                email_me_on_failure(msg, 'err')
            tries += 1
            time.sleep(1)   # let the webservers chill for a bit if were err'ing out
            continue

        try:
            json_data = json.loads(out)
            # police_alerts = [alert for alert in json_data['alerts'] if alert['type'] == 'POLICE']
            json_data.update({'time_stamp': current_ts})


            print '{0}\n{0}'.format(vis_break)
            # just so i can inspect what's happening in each city in realtime
            print len(json_data['alerts']), len(json_data['jams'])
            print '{0}\n{0}'.format(vis_break)


            outfile.write(json.dumps(json_data))
            outfile.write('\n')
            tries = 0
        except Exception as e:
            msg = "{}; {}; {}; Exception {}".format(hostname, now_time, area, e)
            try:
                msg = '{}: {}'.format(msg, out)     # 'out' might be problematic (unicode?)
                logfile.write(msg)
                logfile.write('\n')
            except:
                logfile.write(msg)
                logfile.write('\n')
            finally:
                if tries == 15:
                    email_me_on_failure(msg, 'exception')
                time.sleep(1)
            tries += 1


    email_me_on_failure("Exited the infinite loop because number of tries exceeded {}".format(tries), 'process_shutdown')


### this just makes the json prettier to read for visual inspections
# json_data = open(output_file).read()
# data = json.loads(json_data)
# with open('output_formated.json', 'w') as f:
    # f.write(json.dumps(data, sort_keys=True, indent=4))
raise SystemExit

import json
# with open('./Los_Angeles.txt', 'r') as f:
# with open('./NYC.txt', 'r') as f:
with open('./San_Francisco.txt', 'r') as f:
    for ln in f:
        try:
            json_data = json.loads(ln)
            a, j = len(json_data['alerts']), len(json_data['jams'])
            if (a != 200) or (j != 100):
                print a, j
        except Exception as e:
            print e
            raw_input()

        # if len(ln) > 60000:
            # print len(ln)
        # print len(ln)


