#!/usr/bin/env python
# encoding: utf-8

import pyowm
import json
import weather_dbManagement as dbm

owm = pyowm.OWM('da5438549b419b84ea6890de543fb25c')  # a valid API key

dbm.db.create_tables([dbm.Cities, dbm.Sample])

UPDATE_TABLES = True
if UPDATE_TABLES:
	file = "/home/gimait/workspace/code/scripts/python/weather/selected_list.txt"
	dbm.update_cityTable(file)

cityQuerys = dbm.Cities.select()
justOnce = True
for cityQuery in cityQuerys :

	observation = owm.weather_at_id(cityQuery.cityID)
	w = observation.get_weather()
	sampleJSON = json.loads(w.to_JSON())

	sample = dbm.Sample(originCity = cityQuery.cityID, reference_time = sampleJSON['reference_time'])

	if sampleJSON['status'] and (sampleJSON['status'] != None):
		sample.status = sampleJSON['status']

	if sampleJSON['detailed_status'] and (sampleJSON['detailed_status'] != None):
		sample.detailed_status = sampleJSON['detailed_status'] 

	if sampleJSON['temperature']['temp'] and (sampleJSON['temperature']['temp'] != None):
		sample.temp = sampleJSON['temperature']['temp']

	if sampleJSON['temperature']['temp_min'] and (sampleJSON['temperature']['temp_min'] != None):
		sample.temp_min = sampleJSON['temperature']['temp_min'] 

	if sampleJSON['temperature']['temp_max'] and (sampleJSON['temperature']['temp_max'] != None):
		sample.temp_max = sampleJSON['temperature']['temp_max'] 

	if sampleJSON['temperature']['temp_kf'] and (sampleJSON['temperature']['temp_kf'] != None):
		sample.temp_kf = sampleJSON['temperature']['temp_kf']

	if sampleJSON['humidity'] and (sampleJSON['humidity'] != None):
		sample.humidity = sampleJSON['humidity'] 

	if sampleJSON['pressure']['press'] and (sampleJSON['pressure']['press'] != None):
		sample.press = sampleJSON['pressure']['press'] 

	if sampleJSON['wind']['speed'] and (sampleJSON['wind']['speed'] != None):
		sample.wind_speed = sampleJSON['wind']['speed'] 

	if sampleJSON['wind']['deg'] and (sampleJSON['wind']['deg'] != None):
		sample.wind_deg = sampleJSON['wind']['deg']

	if sampleJSON['clouds'] and (sampleJSON['clouds'] != None):
		sample.clouds = sampleJSON['clouds'] 

	if sampleJSON['rain']['3h'] and (sampleJSON['rain']['3h'] != None):
		sample.rain = sampleJSON['rain']['3h'] 

	if sampleJSON['snow'] and (sampleJSON['snow'] != None):
		sample.snow = sampleJSON['snow'] 

	if sampleJSON['visibility_distance'] and (sampleJSON['visibility_distance'] != None):
		sample.visibility_distance = sampleJSON['visibility_distance']

	if sampleJSON['sunrise_time'] and (sampleJSON['sunrise_time'] != None):
		sample.sunrise_time = sampleJSON['sunrise_time'] 

	if sampleJSON['sunset_time'] and (sampleJSON['sunset_time'] != None):
		sample.sunset_time = sampleJSON['sunset_time'] 

	if sampleJSON['dewpoint'] and (sampleJSON['dewpoint'] != None):
		sample.dewpoint = sampleJSON['dewpoint']

	if sampleJSON['weather_code'] and (sampleJSON['weather_code'] != None):
		sample.weather_code = sampleJSON['weather_code'] 

	if sampleJSON['humidex'] and (sampleJSON['humidex'] != None):
		sample.humidex = sampleJSON['humidex'] 

	if sampleJSON['pressure']['sea_level'] and (sampleJSON['pressure']['sea_level'] != None):
		sample.sea_level = sampleJSON['pressure']['sea_level']

	if sampleJSON['heat_index'] and (sampleJSON['heat_index'] != None):
		sample.heat_index = sampleJSON['heat_index'] 

	if sampleJSON['weather_icon_name'] and (sampleJSON['weather_icon_name'] != None):
		sample.weather_icon_name = sampleJSON['weather_icon_name']

	print(sampleJSON)
	sample.save()

  

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