#!/usr/bin/env python
# encoding: utf-8

#For now, this is pretty much useless as google maps does not show anything unless there is a city and the requests are limited (so forget about search algorithms..)
#import googlemaps
#key for google maps:
#AIzaSyDi-9963vr8QffjEzPk_i8oNjhwyFluSMA
#gmaps = googlemaps.Client(key='AIzaSyDi-9963vr8QffjEzPk_i8oNjhwyFluSMA')
#geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
#reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))
#reverse_geocode_result = gmaps.reverse_geocode((0, 0))


#I found a list of cities from open weather map, so that is much better..
#load file first..

file = "/mnt/D02E63BE2E639C6A/workspace/code/scripts/python/weather/city_list.txt"
with open(file) as f:
    lines = f.read().splitlines()
    nofcities = len(lines)
    stepsize = int( nofcities / 49 - 1);
    file = open("/mnt/D02E63BE2E639C6A/workspace/code/scripts/python/weather/city_selected.txt", "w")
    for i in xrange(0,49):
    	k = 1 + i * stepsize 
    	file.write(lines[k])
    	file.write("\n")





