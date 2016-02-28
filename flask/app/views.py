#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-22-2016
# Purpose:  all(/most) the things for rendering the html pages
#----------------------------------------------------------------

from flask import render_template, jsonify, request
from app import app
from cassandra.cluster import Cluster
# from bokeh.charts import Dot, show, output_file

import sys, os
parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)
from envir_vars import cities_lat_and_long, event_types, dates, weekdays, storage_cluster_ips, times_of_day, hours_dict

cities = sorted(cities_lat_and_long.keys())

cluster = Cluster(storage_cluster_ips)
session = cluster.connect('waze')



@app.route('/')
@app.route('/index')
def index():
   return render_template("index.html")


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

    req_args = request.args
    type_id = getitem(req_args, 'type_id', event_types[0])
    date = getitem(req_args, 'date', dates[0])

    # date selected is in date drop down and type selected is in the type dropdown
    stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
    response = session.execute(stmt, parameters=[date, type_id.upper()])

    type_id = str(type_id)
    date = str(date)

    kwargs = dict(
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

    kwargs.update(series_name=type_id, series_data=series_data)
    return render_template("date_and_type.html",
                            type_id_choosen=type_id,
                            date_choosen=date,
                            event_types=event_types,
                            dates=dates,
                            **kwargs)


@app.route("/date_and_city", methods=['GET'])
def date_and_city():
    ''' date: eg. '2016-1-27'
        city: eg. 'los_angeles'
    '''

    req_args = request.args
    date = getitem(req_args, 'date', dates[0])
    city = getitem(req_args, 'city', 'san_francisco')

    # date selected is in date drop down and city selected in the city dropdown
    stmt = "select * from date_and_city where date=%s and city=%s"
    response = session.execute(stmt, parameters=[date, city])

    city = str(city)
    date = str(date)

    kwargs = dict(
        credits = {"text": 'jason gors', "href": 'http://jgors.com'},
        title = {"text": '{} - {}'.format(city, date), 'style': {"fontSize": "34px"}},
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

    kwargs.update(series_data=series_data, drilldown_series=drilldown_series)
    return render_template("date_and_city.html",
                            city_choosen=city,
                            date_choosen=date,
                            cities=cities,
                            dates=dates,
                            **kwargs)


@app.route("/hotspots", methods=['GET'])
def hotspots():
    ''' weekday: eg. 'Monday'
        city: eg. 'los_angeles'
        type_id: eg. 'accident', 'police', etc
        time_of_day: many options, morning, night, hourly, etc
    '''

    req_args = request.args
    city = getitem(req_args, 'city', 'san_francisco')#cities[0]))
    weekday = getitem(req_args, 'weekday', weekdays[0])
    type_id = getitem(req_args, 'type_id', event_types[0])
    time_of_day = getitem(req_args, 'time_of_day', times_of_day[0])

    stmt = "select * from hotspots where city=%s and type=%s and weekday=%s"
    response = session.execute(stmt, parameters=[city, type_id.upper(), weekday])

    city = str(city)
    type_id = str(type_id)
    weekday = str(weekday)
    lat_centroid, lng_centroid = cities_lat_and_long[city]

    lat_and_lngs = []
    for r in response:
        if time_of_day == 'all day':
            lat_and_lngs.append((r.lat, r.lng))
        elif time_of_day == 'night (12am-6am)':
            if 0 <= r.hour <= 5:
                lat_and_lngs.append((r.lat, r.lng))
        elif time_of_day == 'morning (6am-12pm)':
            if 6 <= r.hour <= 11:
                lat_and_lngs.append((r.lat, r.lng))
        elif time_of_day == 'afternoon (12pm-6pm)':
            if 12 <= r.hour <= 17:
                lat_and_lngs.append((r.lat, r.lng))
        elif time_of_day == 'evening (6pm-12am)':
            if 18 <= r.hour <= 23:
                lat_and_lngs.append((r.lat, r.lng))
        else:     # for just a single hour specified
            hour_of_day = hours_dict[time_of_day]
            if hour_of_day == r.hour:
                lat_and_lngs.append((r.lat, r.lng))

    return render_template("hotspots.html",
                           city_choosen=city,
                           weekday_choosen=weekday,
                           time_of_day_choosen=time_of_day,
                           type_id_choosen=type_id,
                           lat_centroid=lat_centroid,
                           lng_centroid=lng_centroid,
                           lat_and_lngs=lat_and_lngs,
                           cities=cities,
                           dates=dates,
                           weekdays=weekdays,
                           times_of_day=times_of_day,
                           event_types=event_types)


@app.route('/api/<city>')
def realtime_api(city):
    '''exposes a public facing api for each city returning a json object'''

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
    '''exposes a public facing api for each city returning a geojson object'''

    stmt = "SELECT * FROM realtime WHERE city=%s"
    response = session.execute(stmt, parameters=[city])

    # do a request on this api from the realtime_events page and
    # deliver back geojson data -- so shape it nicely here:
    # {"type":"FeatureCollection",
        # "features":[
            # {"type":"Feature", "properties":{"numofthumbsup": 7, "type": 'xxx', "subtype": 'xxx'}, "geometry": {"type":"Point", "coordinates": [-98.7088, 36.4726]}},
            # {"type":"Feature", "properties":{"numofthumbsup": 2, "type": 'xxx', "subtype": 'xxx'}, "geometry": {"type":"Point", "coordinates": [-98.7151, 36.47273]}},
        # ]
    # }

    geojson = {"type": "FeatureCollection", "features": []}
    for r in response:
        feature_dict = {"type": "Feature"}
        properties = {"numofthumbsup": r.numofthumbsup,
                      "type": r.type, "subtype": r.subtype}
        geometry = {"type": "Point", "coordinates": [r.lng, r.lat]}   # NOTE these are backwards
        feature_dict.update(dict(properties=properties, geometry=geometry))
        geojson["features"].append(feature_dict)

    return jsonify(geojson)



@app.route("/realtime_events/<city>", methods=['GET'])
def realtime_events(city):
    '''renders a realtime map for a specified city using the api_geojson data'''
    lat_centroid, lng_centroid = cities_lat_and_long[city]
    center = {"lat": lat_centroid, "lng": lng_centroid}
    return render_template("realtime_events.html", center=center, city=city)


@app.route("/realtime_video")
def realtime_video():
    '''jump to the realtime demo part of the screen cast'''
    return render_template("realtime_video.html")



# with the circles of different sizes depending on numofthumbsup for each reported type
@app.route("/realtime_impact/<city>", methods=['GET'])
def realtime_impact(city):
    '''display the impact each reported event currently has as measured
       by the numofthumbsup each event has received.
    '''
    lat_centroid, lng_centroid = cities_lat_and_long[city]
    center = {"lat": lat_centroid, "lng": lng_centroid}
    return render_template("realtime_impact.html", center=center, city=city)
