#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-26-2016
# Purpose: since this isn't a python pkg (yet) pull this info in to
# script in this project like so:
#
# import sys, os
# parent_dir = os.path.dirname(os.getcwd())
# sys.path.append(parent_dir)
# import envir_vars
#----------------------------------------------------------------


me = 'jason.gors'

# Metro areas in order of bigger to smaller
# cities = ['NYC', 'Los_Angeles',  'Chicago', 'Dallas', 'Houston', 'Philadelphia', 'DC',
          # 'Miami', 'Atlanta', 'Boston', 'San_Francisco', 'Phoenix', 'Detroit', 'Seattle',
          # 'Minneapolis', 'San_Diego', 'Tampa', 'St_Louis', 'Baltimore', 'Denver' 'Pittsburgh',
          # 'Portland', 'Orlando', 'Cincinnati', 'Kansas_City', 'Las_Vegas', 'Cleveland',
          # 'Columbus', 'Indianapolis', 'San_Jose', 'Austin', 'Nashville', 'Milwaukee',
          # 'Oklahoma_City', 'New_Orleans', 'Salt_Lake_City']

# cities = dict(
    # machine_1 = ['nyc', 'boston', 'minneapolis', 'mountain_view'], # 'san_jose', # 'cupertino',
    # machine_2 = ['los_angeles', 'atlanta', 'kansas_city', 'seattle'],
    # machine_3 = ['chicago', 'miami', 'portland', 'detroit'],
    # machine_4 = ['dallas', 'dc', 'denver', 'phoenix'],
    # machine_5 = ['houston', 'philly', 'baltimore', 'san_francisco'],
    # machine_6 = ['austin', 'cincinnati', 'st_louis', 'tampa', 'san_diego'],
# )

cities_lat_and_long = {
    # got city center lat and long from:    http://www.latlong.net (google maps api)

    # machine 1
    'nyc': (40.712784, -74.005941),
    'boston': (42.360082, -71.05888),
    'minneapolis': (44.977753, -93.265011),
    'mountain_view': (37.386052, -122.083851),
    # 'san_jose': (37.338208, -121.886329),
    # 'cupertino': (37.322998, -122.032182),

    # machine 2
    'los_angeles': (34.052234, -118.243685),
    'atlanta': (33.748995, -84.387982),
    'kansas_city': (39.099727, -94.578567),
    'seattle': (47.606209, -122.332071),

    # machine 3
    'chicago': (41.878114, -87.629798),
    'miami': (25.761680, -80.19179),
    'portland': (45.523062, -122.676482),
    'detroit': (42.331427, -83.045754),

    # machine 4
    'dallas': (32.776664, -96.796988),
    'dc': (38.907192, -77.036871),
    'denver': (39.739236, -104.990251),
    'phoenix': (33.448377, -112.074037),

    # machine 5
    'houston': (29.760427, -95.369803),
    'philly': (39.952584, -75.165222),
    'baltimore': (39.290385, -76.612189),
    'san_francisco': (37.774929, -122.419416),

    # machine 6     # added this machine in a day later
    'austin': (30.267153, -97.743061),
    'cincinnati': (39.103118, -84.51202),
    'st_louis': (38.627003, -90.199404),
    'tampa': (27.950575, -82.457178),
    'san_diego': (32.715738, -117.161084),
}
