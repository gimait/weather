#!/usr/bin/env python
# encoding: utf-8
from peewee import *

db = MySQLDatabase('weather', user='rasp314', password='19921992',
						 host='localhost', port=3306)

class CitySample(Model):
	cityID = IntegerField()

	class Meta:
		database = db # This model uses the "people.db" database.

class Sample(Model):
	sampleID = ForeignKeyField(CitySample, backref='samples')
	reference_time = BigIntegerField()
	status = CharField()
	detailed_status = CharField()
	temp = FloatField()
	temp_min = FloatField()
	temp_max = FloatField()
	temp_kf = FloatField()
	humidity = IntegerField()
	press = IntegerField()
	wind_speed = FloatField()
	wind_deg = FloatField()
	clouds = IntegerField()
	rain = FloatField()
	snow = FloatField()
	visibility_distance = IntegerField()
	sunrise_time = BigIntegerField()
	sunset_time = BigIntegerField()
	dewpoint = CharField()
	weather_code = CharField()
	humidex = CharField()
	sea_level = CharField()
	heat_index = CharField()
	weather_icon_name = CharField()

	class Meta:
		database = db # This model uses the "people.db" database.