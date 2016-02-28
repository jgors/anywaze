# anywaze

**Anywaze** is a project I created while at [Insight Data Science](http://insightdatascience.com), while participating in the [Data Engineering](http://insightdataengineering.com) track of the program.  It's a web app that performs large scale analytics on Waze data, as well as doing real-time streaming of this data for inspecting the current state of the Waze community.  

check it out at [anywaze.xyz](http://anywaze.xyz)

also, here's a video of **anywaze** in action: [click me](https://www.youtube.com/embed/z166DG1ZCKE)

_________________________________________________________

More specifically, I gathered data from the 25 largest metropolitan areas in the U.S. via a sort of unofficial data collection method.  The resulting data was very messy, so had to be heavily cleaned and preprocessed, which was then used to perform analytics on a number of metrics that seemed interesting.  Additionally, as mentioned, the real-time data stream was also used to create a Waze community map for the most current user generated events.

Here is the pipeline I used:

![pipeline1](https://github.com/jgors/anywaze/blob/master/misc/pipeline1.png)

...yup, so this is the big picture, but more details to come.
