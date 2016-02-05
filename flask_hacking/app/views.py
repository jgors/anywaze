#!/usr/bin/env python

#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-22-2016
# Purpose:
#----------------------------------------------------------------

from flask import render_template, jsonify, request, redirect
from app import app
from cassandra.cluster import Cluster
# from bokeh.charts import Dot, show, output_file

# setting up connections to cassandra
# cluster = Cluster(['ec2-52-89-106-226.us-west-2.compute.amazonaws.com'])
cluster = Cluster(['52.89.118.67'])
session = cluster.connect('waze')


@app.route('/index')
def index():
   return render_template("index.html")


# @app.route('/index')
# def index():
   # return redirect("/")


@app.route('/')
def main():
   # user = {'nickname': 'World'} # fake user
   # # mylist = [1,2,3,4]
   # mylist = []
   # return render_template("index.html", title='Home', user=user, mylist=mylist)
   return render_template("base.html")


@app.route('/graph')
def graph():
    # chartID = 'container'
    # chart_type = 'bar'
    # chart_height = 500
    # chart = {"renderTo": chartID, "type": chart_type, "height": chart_height}

    series = [{"name": 'Label1', "data": [1,2,3,4]},
              {"name": 'Label2', "data": [4,5,6,7]},
              {"name": 'Label3', "data": [3,2,5,2]}
              ]
    title = {"text": 'My Title'}
    xAxis = {"categories": ['xAxis Data1', 'xAxis Data2', 'xAxis Data3']}
    yAxis = {"title": {"text": 'yAxis Label'}}
    # return render_template('graph.html', chartID=chartID, chart=chart,
                           # series=series, title=title, xAxis=xAxis, yAxis=yAxis)

    kwargs = dict(series=series, title=title, xAxis=xAxis, yAxis=yAxis)
    return render_template('graph.html', **kwargs)



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


pg = 'date_type'
@app.route('/{}'.format(pg))
def date_type():
    # type_id = 'police'
    # stmt = "SELECT * FROM date_and_type WHERE type=%s"
    # response = session.execute(stmt, parameters=[type_id.upper()])
    # print response
    # dates = [r.date for r in response]
    # return render_template("{}.html".format(pg), dates)
    return render_template("{}.html".format(pg))

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
    ''' type_id: eg. 'accident', 'police', etc
        date: eg. '2016-1-27'
    '''

    type_id = request.form["type_id"]
    date = request.form["date"]

    # type entered is in type_id and date selected in dropdown is in date variable
    stmt = "SELECT * FROM date_and_type WHERE date=%s AND type=%s"
    response = session.execute(stmt, parameters=[date, type_id.upper()])

    type_id = str(type_id)
    date = str(date)

    chartID = 'container2'
    kwargs = dict(
        # chart = {"renderTo": chartID, "type": 'column', "height": '600px'},

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
    # print kwargs

    # NOTE for some reason this stuff breaks it:
    # {% extends "base.html" %}
    # {% block date_type %}
    # if that stuff is removed, then the graph works

    # return render_template('graph.html', **kwargs)
    return render_template("{}_op.html".format(pg), **kwargs)
    # return render_template("{}.html".format(pg), **kwargs)







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







'''
from flask import Flask, render_template
import random
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html, components

import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


@app.route('/')
def indexPage():
    # generate some random integers, sorted
    exponent = .7+random.random()*.6
    dta = []
    for i in range(50):
        rnum = int((random.random()* 10)**exponent)
        dta.append(rnum)
    y = sorted(dta)
    x = range(len(y))

    # generate Bokeh HTML elements
    # create a `figure` object
    p = figure(title='A Bokeh plot',
            plot_width=500, plot_height=400)
    # add the line
    p.line(x,y)
    # add axis labels
    p.xaxis.axis_label = "time"
    p.yaxis.axis_label = "size"
    # create the HTML elements to pass to template
    figJS, figDiv = components(p, CDN)

    # generate matplotlib plot
    fig = plt.figure(figsize=(5, 4), dpi=100)
    axes = fig.add_subplot(1, 1, 1)
    # plot the data
    axes.plot(x,y, '-')


    # labels
    axes.set_xlabel('time')
    axes.set_ylabel('size')
    axes.set_title("A matplotlib plot")
    # make the temporary file
    f = tempfile.NamedTemporaryFile(
            dir='static/temp', suffix='.png', delete=False)
    # save the figure to the temporary file
    plt.savefig(f)
    f.close()
    # close the file
    # get the file's name (rather than the whole path)
    # (the template will need that)
    plotPng = f.name.split('/')[-1]

    return (render_template('figures.html', y=y,
        figJS=figJS, figDiv=figDiv,
        # plotPng=plotPng
        ))

# if __name__ == '__main__':
    # app.debug=True
    # app.run
'''





# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route('/')
# def homepage():
    # title = "Epic Tutorials"
    # paragraph = ["wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!","wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!"]
    # try:
        # return render_template("index.html", title = title, paragraph=paragraph)
    # except Exception, e:
        # return str(e)

# @app.route('/about')
# def aboutpage():
    # title = "About this site"
    # paragraph = ["blah blah blah memememememmeme blah blah memememe"]
    # pageType = 'about'
    # return render_template("index.html", title=title, paragraph=paragraph, pageType=pageType)


# @app.route('/about/contact')
# def contactPage():
    # title = "About this site"
    # paragraph = ["blah blah blah memememememmeme blah blah memememe"]
    # pageType = 'about'
    # return render_template("index.html", title=title, paragraph=paragraph, pageType=pageType)



# @app.route('/graph')
# def graph(chartID = 'chart_ID', chart_type = 'line', chart_height = 500):
    # chart = {"renderTo": chartID, "type": chart_type, "height": chart_height,}
    # series = [{"name": 'Label1', "data": [1,2,3]}, {"name": 'Label2', "data": [4, 5, 6]}]
    # title = {"text": 'My Title'}
    # xAxis = {"categories": ['xAxis Data1', 'xAxis Data2', 'xAxis Data3']}
    # yAxis = {"title": {"text": 'yAxis Label'}}
    # return render_template('index.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis)

# if __name__ == "__main__":
    # app.run(debug = True, host='0.0.0.0', port=8080, passthrough_errors=True)



