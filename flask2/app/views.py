#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-22-2016
# Purpose:
#----------------------------------------------------------------

import json

from flask import render_template, jsonify, request
from app import app
from cassandra.cluster import Cluster
# from bokeh.charts import Dot, show, output_file

import sys, os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
from envir_vars import cities_lat_and_long, event_types, dates, weekdays


cities = sorted(cities_lat_and_long.keys())
filler = '--'

# setting up connections to cassandra
cluster = Cluster(['52.89.106.226', '52.89.118.67', '52.34.130.78', '52.89.11.71'])
session = cluster.connect('waze')



@app.route('/')
@app.route('/index')
def index():
   return render_template("index.html")


# @app.route("/{}".format(pg), methods=['POST'])
# def date_type_post():
    # type_id = request.form["type_id"]
    # date = request.form["date"]

    # # type entered is in type_id and date selected in dropdown is in date variable
    # stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
    # response = session.execute(stmt, parameters=[date, type_id])
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
    # type_id = request.form["type_id"]
    # date = request.form["date"]

    # date selected is in date drop down and type selected in the type dropdown
    # stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
    stmt = "SELECT * FROM date_and_type2 WHERE date=%s AND type=%s"
    response = session.execute(stmt, parameters=[date, type_id.upper()])

    type_id = str(type_id)
    date = str(date)

    # chartID = 'my_chart'
    kwargs = dict(
        # chart = {"renderTo": chartID, "type": 'column', "height": '600px'},
        credits = {"text": 'jason gors', "href": 'http://jgors.com'},
        title = {"text": '{} reports'.format(type_id), 'style': {"fontSize": "36px"}},
        subtitle = {"text": date, 'style': {"fontSize": "32px"}},
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
    # stmt = "select * from date_and_city where date=%s and city=%s"
    stmt = "select * from date_and_city2 where date=%s and city=%s"
    response = session.execute(stmt, parameters=[date, city])

    city = str(city)
    date = str(date)

    # chartID = 'my_chart'
    kwargs = dict(
        # chart = {"renderTo": chartID, "type": 'column', "height": '600px'},
        credits = {"text": 'jason gors', "href": 'http://jgors.com'},
        title = {"text": '{} - {}'.format(city, date), 'style': {"fontSize": "34px"}
                },
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



@app.route("/hotspots", methods=['GET'])
def hotspots():
    args = request.args

    city = getitem(args, 'city', filler)
    # date = getitem(args, 'date', dates[0])
    # weekday = getitem(args, 'weekday', weekdays[0])
    weekday = getitem(args, 'weekday', filler)
    type_id = getitem(args, 'type_id', filler)


    # "lat +- 90     -91 < lat < 91"
    # "lng +- 180    -181 < lng < 181"
    # stmt = "select * from heatmaps where date=%s and city=%s and type=%s"
    # response = session.execute(stmt, parameters=[date, city, type_id.upper()])

    # stmt = "select * from heatmaps2 where city=%s and type=%s and weekday=%s"
    stmt = "select * from hotspots2 where city=%s and type=%s and weekday=%s"
    response = session.execute(stmt, parameters=[city, type_id.upper(), weekday])

    # date = str(date)
    city = str(city)
    type_id = str(type_id)
    weekday = str(weekday)
    if city == filler:
        city = 'san_francisco'
    lat_centroid, lng_centroid = cities_lat_and_long[city]

    lat_and_lngs = []
    for r in response:
        lat_and_lngs.append((r.lat, r.lng))

    return render_template("hotspots.html",
                           city=city,
                           type_id=type_id,
                           weekdays=weekdays,
                           weekday=weekday,
                           # date=date,
                           # city='',
                           # type_id='',
                           lat_centroid=lat_centroid,
                           lng_centroid=lng_centroid,
                           lat_and_lngs=lat_and_lngs,
                           cities=cities,
                           event_types=event_types,
                           dates=dates,
                           )


@app.route('/api/<city>')
def realtime_api(city):
    stmt = "SELECT * FROM realtime WHERE city=%s"
    response = session.execute(stmt, parameters=[city])
    response_list = []
    for x in response:
        d = {"city": x.city, "type": x.type, "subtype": x.subtype,
             "numofthumbsup": x.numofthumbsup,
             "lat": x.lat, "lng": x.lng}
        response_list.append(d)
    return jsonify(alerts=response_list)


@app.route("/api_geojson/<city>", methods=['GET'])
def api_geojson(city):
    stmt = "SELECT * FROM realtime WHERE city=%s"
    response = session.execute(stmt, parameters=[city])
    response_list = []
    for x in response:
        d = {"city": x.city, "type": x.type, "subtype": x.subtype,
             "numofthumbsup": x.numofthumbsup,
             "lat": x.lat, "lng": x.lng}
        response_list.append(d)

    # do a request on this api from the realtime_events page and
    # deliver back geojson data -- so shape it nicely here:
    # eventfeed_callback(
    # {"type":"FeatureCollection",
        # "features":[
            # {"type":"Feature", "properties":{"numofthumbsup": 7}, "geometry": {"type":"Point", "coordinates": [-98.7088, 36.4726]}},
            # {"type":"Feature", "properties":{"numofthumbsup": 2}, "geometry": {"type":"Point", "coordinates": [-98.7151, 36.47273]}},
        # ]
    # }

    jsondict = {"type": "FeatureCollection", "features": []}
    for r in response_list:
        feature_dict = {"type": "Feature"}
        properties = {"numofthumbsup": r['numofthumbsup']+1, # don't let there be zeros
                      "type": r['type']}
        geometry = {"type": "Point", "coordinates": [r['lng'], r['lat']]}   # these are backwards
        feature_dict.update(dict(properties=properties, geometry=geometry))

        jsondict["features"].append(feature_dict)

    return jsonify(jsondict)



@app.route("/realtime_events/<city>", methods=['GET'])
def realtime_events(city):
    lat_centroid, lng_centroid = cities_lat_and_long[city]
    center = {"lat": lat_centroid, "lng": lng_centroid}
    return render_template("realtime_events.html", center=center, city=city)


# with the circles of different sizes depending on numofthumbsup (FIXME)
@app.route("/realtime_impact/<city>", methods=['GET'])
def realtime_impact(city):
    lat_centroid, lng_centroid = cities_lat_and_long[city]
    center = {"lat": lat_centroid, "lng": lng_centroid}
    return render_template("realtime_impact.html", center=center, city=city)



# the insight ajax example
@app.route('/realtime_ex')
def realtime_ex():
    return render_template("realtime_ex.html")



# these are for the realtime highcharts graphs
@app.route("/realtime_reports2", methods=['GET'])
def realtime_reports2():
    return render_template("realtime_reports2.html")

@app.route("/realtime_reports3", methods=['GET'])
def realtime_reports3():
    return render_template("realtime_reports3.html")


