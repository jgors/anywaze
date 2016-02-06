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

@app.route('/realtime')
def realtime():
    return render_template("realtime.html")


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


# pg = 'date_type'
# @app.route('/{}'.format(pg))
# def date_type():
    # # return render_template("dots.html")
    # return render_template("{}.html".format(pg))

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

# @app.route("/{}".format(pg), methods=['POST'])
# def date_type_post():
    # type_id = request.form["type_id"]
    # date = request.form["date"]

    # # type entered is in type_id and date selected in dropdown is in date variable
    # stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
    # response = session.execute(stmt, parameters=[date, type_id.upper()])

    # '''
    # data = {
        # 'sample': ['1st', '2nd', '1st', '2nd', '1st', '2nd'],
        # 'interpreter': ['python', 'python', 'pypy', 'pypy', 'jython', 'jython'],
        # 'timing': [-2, 5, 12, 40, 22, 30],
    # }
    # # x-axis labels pulled from the interpreter column, stacking labels from sample column
    # dots = Dot(data, values='timing', label='interpreter',
            # group='sample', agg='mean',
            # title="Python Interpreter Sampling",
            # legend='top_right', width=600)
    # output_file("app/templates/dots.html", title="dots.py example")
    # '''

    # response_list = []
    # for val in response:
        # response_list.append(val)
    # jsonresponse = [{"date": x.date,
                     # "type": x.type,
                     # "city": x.city,
                     # "count": x.count,
                    # } for x in response_list]
    # print jsonresponse
    # return render_template("{}_op.html".format(pg), output=jsonresponse)

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

pg = 'date_type'
@app.route("/{}".format(pg), methods=['GET'])
def date_type():
    ''' type_id: eg. 'accident', 'police', etc
        date: eg. '2016-1-27'
    '''

    args = request.args

    type_id = getitem(args, 'type_id', 'accident')
    date = getitem(args, 'date', '2016-1-27')

    # type_id = request.form["type_id"]
    # date = request.form["date"]

    # type entered is in type_id and date selected in dropdown is in date variable
    stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
    response = session.execute(stmt, parameters=[date, type_id.upper()])

    type_id = str(type_id)
    date = str(date)

    chartID = 'my_chart'
    kwargs = dict(
        chart = {"renderTo": chartID, "type": 'column', "height": '600px'},

        credits = {"text": 'jason gors', "href": 'http://jgors.com'},
        title = {"text": '{} reports'.format(type_id)},
        subtitle = {"text": date},
        yAxis = {"min": 0, "title": {"text": 'Number Reported'}},
        tooltip = {"pointFormat": '%s on %s: <b>{point.y:.0f}</b>' % (type_id, date)},
    )

    series_name = type_id
    series_data = []
    for r in response:
        series_data.append([str(r.city), r.count])
    series_data = sorted(series_data, reverse=True, key=lambda cities_data: cities_data[1])

    kwargs.update(series_name=series_name, series_data=series_data, chartID=chartID)

    # NOTE for some reason this stuff breaks it:
    # {% extends "base.html" %}
    # {% block date_type %}
    # if that stuff is removed, then the graph works

    # return render_template('graph.html', **kwargs)
    return render_template("{}.html".format(pg), **kwargs)





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
