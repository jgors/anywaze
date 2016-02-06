#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-22-2016
# Purpose:
#----------------------------------------------------------------

from flask import render_template, jsonify, request
from app import app
from cassandra.cluster import Cluster
# from bokeh.charts import Dot, show, output_file

import sys, os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
from envir_vars import cities_lat_and_long


# setting up connections to cassandra
# cluster = Cluster(['ec2-52-89-106-226.us-west-2.compute.amazonaws.com'])
cluster = Cluster(['52.89.106.226', '52.89.118.67', '52.34.130.78', '52.89.11.71'])
session = cluster.connect('waze')


# FIXME these should really be populated from the db and not hardcoded here
event_types = ['accident', 'police', 'road_closed', 'hazard', 'jam']
dates = ['2016-01-25', '2016-01-26', '2016-01-27', '2016-01-28', '2016-01-29', '2016-01-30',
         '2016-01-31', '2016-02-01', '2016-02-02']
cities = sorted(cities_lat_and_long.keys())


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


@app.route("/date_and_type", methods=['GET'])
def date_and_type():
    ''' type_id: eg. 'accident', 'police', etc
        date: eg. '2016-1-27'
    '''

    args = request.args
    type_id = getitem(args, 'type_id', event_types[0])
    date = getitem(args, 'date', dates[0])
    # type_id = getitem(args, 'type_id', 'accident')
    # date = getitem(args, 'date', '2016-1-27')

    # type_id = request.form["type_id"]
    # date = request.form["date"]

    # date selected is in date drop down and date selected in date dropdown
    stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
    response = session.execute(stmt, parameters=[date, type_id.upper()])

    type_id = str(type_id)
    date = str(date)

    # chartID = 'my_chart'
    kwargs = dict(
        # chart = {"renderTo": chartID, "type": 'column', "height": '600px'},
        credits = {"text": 'jason gors', "href": 'http://jgors.com'},
        title = {"text": '{} reports'.format(type_id)},
        subtitle = {"text": date},
        yAxis = {"min": 0, "title": {"text": 'Number Reported'}},
        tooltip = {"pointFormat": '%s on %s: <b>{point.y:.0f}</b>' % (type_id, date)},
    )

    series_data = []
    for r in response:
        series_data.append([str(r.city), r.count])
    series_data = sorted(series_data, reverse=True, key=lambda cities_data: cities_data[1])

    kwargs.update(series_name=type_id, series_data=series_data)#, chartID=chartID)
    # print kwargs

    return render_template("date_and_type.html",
                            event_types=event_types,
                            dates=dates,
                            **kwargs)


@app.route("/date_and_city", methods=['GET'])
def date_and_city():
    ''' date: eg. '2016-1-27'
        city: eg. 'los_angeles'
    '''

    args = request.args
    date = getitem(args, 'date', dates[0])
    city = getitem(args, 'city', cities[0])

    # date selected is in date drop down and city selected in city dropdown
    stmt = "select * from date_and_city where date=%s and city=%s"
    response = session.execute(stmt, parameters=[date, city])

    city = str(city)
    date = str(date)

    # chartID = 'my_chart'
    kwargs = dict(
        # chart = {"renderTo": chartID, "type": 'column', "height": '600px'},
        credits = {"text": 'jason gors', "href": 'http://jgors.com'},
        title = {"text": '{} for {}'.format(city, date)},
    )


    d = {}
    for r in response:
        _type = str(r.type)
        subtype = str(r.subtype)
        count = r.count
        if r.type not in d:
            d[_type] = [[subtype, count]]
        else:
            d[_type].append([subtype, count])

    series_data = []
    drilldown_series = []
    for _type, subtype_and_cnts in d.items():
        type_cnt = sum([subtype_and_cnt[1] for subtype_and_cnt in subtype_and_cnts])
        series_data.append({'name': _type, 'drilldown': _type, 'y': type_cnt})
        drilldown_series.append({'name': _type, 'id': _type, 'data': subtype_and_cnts})

    kwargs.update(series_data=series_data, drilldown_series=drilldown_series)#, chartID=chartID)

    return render_template("date_and_city.html",
                            cities=cities,
                            dates=dates,
                            **kwargs)


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
