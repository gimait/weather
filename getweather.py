#!/usr/bin/env python
# encoding: utf-8
import argparse
import json
import requests
import pymongo as pm


def reset_city_list(client):
	city_db = client['weather']
	city_db.to_check.delete_many({})
	city_list = get_city_list(client)
	city_db.to_check.insert_many(city_list)


def update_city_to_check(client, cities):
	city_db = client['weather']
	city_db.to_check.delete_many({})
	city_db.to_check.insert_many(cities)


def get_city_list(client):
	city_list = []
	cities = client['weather'].cities
	for ex in cities.find({}):
		city_list.append({"id": ex['id']})
	return city_list


def get_list_to_check(client):
	client['weather'].to_check.find({})
	city_ids = []
	to_check = client['weather'].to_check
	for ex in to_check.find({}):
		city_ids.append({"id": ex['id']})
	return city_ids


def get_coordinates_by_id(client, id):
	query = client['weather'].cities.find_one({"id": id})
	return query['lat'], query['lon']


def get_sample_by_id(id, api_key):
	url = "https://api.openweathermap.org/data/2.5/weather?id={}&units=metric&appid={}".format(id, api_key)
	r = requests.get(url)
	return r.json()


def sample_cities(client, key, n=50):
	cities_to_check = get_list_to_check(client)
	if len(cities_to_check) <= 0:
		return
	for i in range(50):
		if len(cities_to_check) <= 0:
			update_city_to_check({})
			return
		sample = get_sample_by_id(cities_to_check.pop(0)["id"], key)
		client['weather'].samples.insert_one(sample)

	update_city_to_check(client, cities_to_check)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-n", "--new-sample",
						help="A new sample will be measured",
						action='store_true')
	args = parser.parse_args()
	client = pm.MongoClient()
	if args.new_sample:
		reset_city_list(client)
		return

	api_key = 'da5438549b419b84ea6890de543fb25c'  # a valid API key
	sample_cities(client, api_key, 1)


if __name__ == '__main__':
	main()
