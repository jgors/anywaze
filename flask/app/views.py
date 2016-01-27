#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-22-2016
# Purpose:
#----------------------------------------------------------------

from flask import jsonify   #jsonify creates a json representation of the response
from flask import render_template

from app import app
from cassandra.cluster import Cluster
# setting up connections to cassandra

# topic_for_keyspace = 'san-fran-old'
cluster = Cluster(['ec2-52-89-106-226.us-west-2.compute.amazonaws.com'])
# session = cluster.connect(topic_for_keyspace)


@app.route('/')
@app.route('/index')
def index():
   user = {'nickname': 'World'} # fake user
   # mylist = [1,2,3,4]
   mylist = []
   return render_template("index.html", title='Home', user=user, mylist=mylist)


# session = cluster.connect('playground')

# @app.route('/api/<email>/<date>')
# def get_email(email, date):
        # stmt = "SELECT * FROM email WHERE id=%s and date=%s"
        # response = session.execute(stmt, parameters=[email, date])
        # response_list = []
        # for val in response:
            # # print val   # is one of those Row(...) objects
            # response_list.append(val)
        # # print response_list     # list of Row(...) objects
        # jsonresponse = [{"first name": x.fname, "last name": x.lname,
                         # "id": x.id, "message": x.message, "time": x.time} for x in response_list]
        # # print jsonresponse  # list of dicts (one dict for each Row() object from before)
        # return jsonify(emails=jsonresponse)


session = cluster.connect('waze')
# FIXME
@app.route('/api/<cityevent>')
# @app.route('/api/<city>/<event>')
# @app.route('/api/sanfransisco/date/police')
# def get_police(city, date, police):
def get_police(cityevent):
        # stmt = "SELECT * FROM sanfranpolice WHERE time=%s"
        # stmt = "SELECT * FROM sanfranpolice WHERE *"
        stmt = "SELECT * FROM sanfranpolice "
        response = session.execute(stmt)#, parameters=[city, event])

        response_list = []
        for val in response:
             response_list.append(val)
        jsonresponse = [{"time": x.time,
                         "count": x.count
                         # "locations": eval(x.locations)
                         }
                                for x in response_list]
        return jsonify(event=jsonresponse)
