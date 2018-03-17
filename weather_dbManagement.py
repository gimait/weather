#!/usr/bin/env python
# encoding: utf-8
from peewee import *

db = MySQLDatabase('weather', user='root', password='1992199Dos',
						 host='localhost', port=3306)

class Cities(Model):
	cityID = IntegerField(unique=True)
	latitude = FloatField()
	longitude = FloatField()
	name = CharField()
	countryCode = CharField()

	class Meta:
		database = db # This model uses the "people.db" database.

class Sample(Model):
	originCity = ForeignKeyField(Cities, field='cityID', backref='samples')
	reference_time = BigIntegerField(default=0)
	status = CharField(default="")
	detailed_status = CharField(default="")
	temp = FloatField(default=0)
	temp_min = FloatField(default=0)
	temp_max = FloatField(default=0)
	temp_kf = FloatField(default=0)
	humidity = IntegerField(default=-1)
	press = IntegerField(default=-1)
	wind_speed = FloatField(default=0)
	wind_deg = FloatField(default=0)
	clouds = IntegerField(default=-1)
	rain = FloatField(default=0)
	snow = FloatField(default=0)
	visibility_distance = IntegerField(default=-1)
	sunrise_time = BigIntegerField(default=0)
	sunset_time = BigIntegerField(default=0)
	dewpoint = CharField(default="")
	weather_code = CharField(default="")
	humidex = CharField(default="")
	sea_level = CharField(default="")
	heat_index = CharField(default="")
	weather_icon_name = CharField(default="")

	class Meta:
		database = db # This model uses the "people.db" database.






def update_cityTable(file):

	with open(file) as f:
		lines = f.read().splitlines()
		for y in lines:
			values = y.split()
			try:
				existingid = Cities.select().where(Cities.cityID == int(values[0])).exists()
				if not existingid:
					city_name = str()
					for k in values[1:-3]:
						city_name += k + " "

					newCity = Cities(cityID = int(values[0]), latitude = float(values[-3]), longitude = float(values[-2]), name = city_name, countryCode = values[-1])
					newCity.save()
			except:
				print ("Something went wrong, read :" + values[0])

#def addNew_sample(smpl):
#	local_sample = Sample(originCity = )




