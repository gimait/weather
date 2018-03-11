#!/usr/bin/env python
# encoding: utf-8

import pyowm
import json

owm = pyowm.OWM('da5438549b419b84ea6890de543fb25c')  # a valid API key

# Have a pro subscription? Then use:
# owm = pyowm.OWM(API_key='your-API-key', subscription_type='pro')

# Will it be sunny tomorrow at this time in Milan (Italy) ?
#forecast = owm.daily_forecast("Odense,dk")
#tomorrow = pyowm.timeutils.tomorrow()
#forecast.will_be_sunny_at(tomorrow)  # Always True in Italy, right? ;-)

# Search for current weather in London (UK)
file = "/mnt/D02E63BE2E639C6A/workspace/code/scripts/python/weather/selected_list.txt"
cityIDs = list()
with open(file) as f:
    lines = f.read().splitlines()
    for y in lines:
        t = y.split()
        try:
         	cityIDs.append(int(t[0]))
        except:
        	print ("Something went wrong, read :" + t[0])


for city in cityIDs:
	observation = owm.weather_at_id(city)
	w = observation.get_weather()
	sample = json.loads(w.to_JSON())
	print(sample)

	#print(w.get_temperature('celsius'))                      # <Weather - reference time=2013-12-18 09:20,
                              # status=Clouds>

# Weather details
# w.get_wind()                  # {'speed': 4.6, 'deg': 330}
# w.get_humidity()              # 87
# w.get_temperature('celsius')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}

# Search current weather observations in the surroundings of
# lat=22.57W, lon=43.12S (Rio de Janeiro, BR)
# observation_list = owm.weather_around_coords(0, 0)
# print(observation_list)
# w = observation_list[0].get_weather()
# print(w.get_temperature('celsius'))                      # <Weather - reference time=2013-12-18 09:20,