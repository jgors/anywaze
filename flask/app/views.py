#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-22-2016
# Purpose:
#----------------------------------------------------------------

from flask import render_template, jsonify, request
from app import app
from cassandra.cluster import Cluster
from bokeh.charts import Dot, show, output_file

# setting up connections to cassandra
# cluster = Cluster(['ec2-52-89-106-226.us-west-2.compute.amazonaws.com'])
cluster = Cluster(['52.89.118.67'])
session = cluster.connect('waze')


@app.route('/')
@app.route('/index')
def index():
   # user = {'nickname': 'World'} # fake user
   # # mylist = [1,2,3,4]
   # mylist = []
   # return render_template("index.html", title='Home', user=user, mylist=mylist)
   return render_template("base.html")


@app.route('/slides')
def slides():
   return render_template("slides.html", title='Slides')

# works!
# @app.route('/api/date_type/<date>/<_type>')
# def get_date_type(date, _type):
        # stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
        # response = session.execute(stmt, parameters=[date, _type])
        # response_list = []
        # for val in response:
             # response_list.append(val)
        # jsonresponse = [{"date": x.date,
                         # "type": x.type,
                         # "city": x.city,
                         # "count": x.count,
                        # }
                        # for x in response_list]
        # return jsonify(events=jsonresponse)


pg = 'date_type'
@app.route('/{}'.format(pg))
def date_type():
    return render_template("{}.html".format(pg))
    # return render_template("dots.html")
'''
@app.route("/{}".format(pg), methods=['POST'])
def date_type_post():
    type_id = request.form["type_id"]
    date = request.form["date"]

    # type entered is in type_id and date selected in dropdown is in date variable
    stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
    response = session.execute(stmt, parameters=[date, type_id])
    response_list = []
    for val in response:
        response_list.append(val)
    jsonresponse = [{"date": x.date,
                     "type": x.type,
                     "city": x.city,
                     "count": x.count,
                    } for x in response_list]
    print jsonresponse
    return render_template("{}_op.html".format(pg), output=jsonresponse)
'''

@app.route("/{}".format(pg), methods=['POST'])
def date_type_post():
    type_id = request.form["type_id"]
    date = request.form["date"]

    # type entered is in type_id and date selected in dropdown is in date variable
    stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
    response = session.execute(stmt, parameters=[date, type_id])

    data = {
        'sample': ['1st', '2nd', '1st', '2nd', '1st', '2nd'],
        'interpreter': ['python', 'python', 'pypy', 'pypy', 'jython', 'jython'],
        'timing': [-2, 5, 12, 40, 22, 30],
    }
    # x-axis labels pulled from the interpreter column, stacking labels from sample column
    dots = Dot(data, values='timing', label='interpreter',
            group='sample', agg='mean',
            title="Python Interpreter Sampling",
            legend='top_right', width=600)
    output_file("app/templates/dots.html", title="dots.py example")

    response_list = []
    for val in response:
        response_list.append(val)
    jsonresponse = [{"date": x.date,
                     "type": x.type,
                     "city": x.city,
                     "count": x.count,
                    } for x in response_list]
    print jsonresponse
    return render_template("{}_op.html".format(pg), output=jsonresponse)


# For map drawing:
m = 'map4'
@app.route('/{}'.format(m))
def map():
   return render_template("{}.html".format(m), title=m)

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
