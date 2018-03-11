#!/usr/bin/env python
# encoding: utf-8
from peewee import *

db = MySQLDatabase('weather', user='rasp314', password='19921992',
						 host='localhost', port=3306)

class CitySample(Model):
	cityID = IntField()

	class Meta:
		database = db # This model uses the "people.db" database.

class Sample(Model):
	sampleID = ForeignKeyField(CitySample, backref='samples')
	reference_time = IntField()
	status = CharField()
	detailed_status = CharField()
	temp = FloatField()
	temp_min = FloatField()
	temp_max = FloatField()
	temp_kf = FloatField()
	humidity = IntField()
	press = IntField()
	wind_speed = FloatField()
	wind_deg = FloatField()
	clouds = IntField()
	rain = FloatField()
	snow = FloatField()
	visibility_distance = IntField()
	sunrise_time = IntField()
	sunset_time = IntField()
	dewpoint = CharField()
	weather_code = CharField()
	humidex = CharField()
	sea_level = CharField()
	heat_index = CharField()
	weather_icon_name = CharField()

	class Meta:
		database = db # This model uses the "people.db" database.