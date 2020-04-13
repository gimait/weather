#!/usr/bin/env python3
import argparse
import requests
from multiprocessing.pool import ThreadPool
from datetime import datetime
import pymongo as pm
import subprocess
import telepot


def is_disk_full(percentage=80):
	percent_str = subprocess.check_output("df | grep /dev/root | awk '{print $5}'", shell=True).decode('utf-8')
	if percent_str:
		return True if int(percent_str[:-2]) > percentage else False
	else:
		return False


def report_disk_fill_rate(client):
	percent_str = subprocess.check_output("df | grep /dev/root | awk '{print $5}'", shell=True).decode('utf-8')
	percent_str = "Disk usage: " + percent_str
	collection = client['weather'].samples
	first_time = collection.find_one()['dt']
	last_time = collection.find_one({"$query": {}, "$orderby": {"_id": -1}})['dt']
	readable_first = datetime.utcfromtimestamp(first_time).strftime('%Y-%m-%d %H:%M:%S')
	readable_second = datetime.utcfromtimestamp(last_time).strftime('%Y-%m-%d %H:%M:%S')
	difference = last_time-first_time
	percent_str += '\nDisk half capacity, time since first log:'
	percent_str += str(difference)
	bot = telepot.Bot('1297382354:AAECpBd2TseprNSrOHoeH43bZ-Rbw2HvYxc')
	bot.sendMessage('903059496', percent_str)
	percent_str = 'first log date: ' + readable_first + '\nlast log date: ' + readable_second
	bot.sendMessage('903059496', percent_str)


def report_disk_usage():
	percent_str = subprocess.check_output("df | grep /dev/root | awk '{print $5}'", shell=True).decode('utf-8')
	percent_str = "Disk usage: " + percent_str
	bot = telepot.Bot('1297382354:AAECpBd2TseprNSrOHoeH43bZ-Rbw2HvYxc')
	bot.sendMessage('903059496', percent_str)


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

	def sampler(city):
		sample = get_sample_by_id(city["id"], key)
		client['weather'].samples.insert_one(sample)

	with ThreadPool(10) as pool:
		pool.map(sampler, cities_to_check[0:n])
		del cities_to_check[0:n]

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
		report_disk_usage()
		return

	if is_disk_full():
		print("disk full!")
		return

	if is_disk_full(50):
		report_disk_fill_rate(client)

	api_key = 'da5438549b419b84ea6890de543fb25c'  # a valid API key
	sample_cities(client, api_key)


if __name__ == '__main__':
	main()
