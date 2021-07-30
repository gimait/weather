#!/usr/bin/env python3
import argparse
import datetime
import logging
import os
import pymongo as pm
import re
import requests
import subprocess
import telepot
import zipfile
from multiprocessing.pool import ThreadPool


class lock_file:
    """Class creating local object to avoid launching multiple instances of the same script
    """
    def __init__(self, file):
        self.file_ = file
        self.got_lock = False
        if os.path.isfile(file):
            raise NameError('Lock file exists')
        else:
            f = open(file, 'w')
            f.write("weather lock")
            self.got_lock = True

    def __del__(self):
        if self.got_lock:
            os.remove(self.file_)


def get_disk_usage():
    """
    Looks at the percentage of disk used in the main storage of a raspberry pi.
    :return: percentage as string: e.g. '45%'.
    """
    percent_str = subprocess.check_output("df | grep /dev/root | awk '{print $5}'", shell=True).decode('utf-8')
    return percent_str


def is_disk_full(percentage=80):
    """
    Checks if the disk use has gone above a threshold.
    :param percentage: threshold percentage checked.
    :return: True if disk usage is higher than threshold, else False.
    """
    percent_str = get_disk_usage()
    if percent_str:
        return True if int(percent_str[:-2]) > percentage else False
    else:
        return False


def export_samples_to_dir(client, dir):
    """
    Saves current samples in weather.samples db to a output dir (in a compressed file), then cleans the collection
    :param client: Mongodb client
    :param dir: Output directory where samples will be stored.
    """
    # Open zip file, check name of content
    if os.path.isdir(dir):
        zip_file = os.path.join(dir, 'samples_bkup.zip')
        with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as zip:
            # Check files in zip, they will have the shape samplesX.json
            files = zip.namelist()
            max_id = 0
            for f in files:
                idx = int(re.findall(r'\d+', f)[0])
                if idx >= max_id:
                    max_id = idx + 1
            # Write new file in zip
            aux_file = os.path.join(dir, "samples" + str(max_id) + ".json")
            subprocess.check_output("mongoexport --collection samples -d weather --out '{}'".format(aux_file),
                                    shell=True).decode('utf-8')
            zip.write(aux_file, os.path.basename(aux_file))
            os.remove(aux_file)
            client.weather.samples.delete_many({})


def report_disk_fill_rate(db_client):
    """
    Sends report about disk usage and sample information from database (first and last entry times).
    :param db_client: MongoClient for local database.
    :return:
    """
    bot_id = os.getenv('BOT_CLIENT')
    chat_id = os.getenv('BOT_CHATID')
    if bot_id and chat_id:
        percent_str = "Disk usage: " + str(get_disk_usage())
        collection = db_client['weather'].samples
        first_time = collection.find_one()['dt']
        last_time = collection.find_one({"$query": {}, "$orderby": {"_id": -1}})['dt']
        difference = last_time-first_time
        readable_first = datetime.datetime.utcfromtimestamp(first_time).strftime('%Y-%m-%d %H:%M:%S')
        readable_second = datetime.datetime.utcfromtimestamp(last_time).strftime('%Y-%m-%d %H:%M:%S')
        percent_str += '\nDisk half capacity, time since first log:'
        percent_str += str(difference)
        bot = telepot.Bot(bot_id)
        bot.sendMessage(chat_id, percent_str)
        percent_str = 'first log date: ' + readable_first + '\nlast log date: ' + readable_second
        bot.sendMessage(chat_id, percent_str)


def report_disk_usage(stats):
    """
    Sends message with disk use percentage.
    :return:
    """
    bot_id = os.getenv('BOT_CLIENT')
    chat_id = os.getenv('BOT_CHATID')
    percent_str = subprocess.check_output("df | grep /dev/root | awk '{print $5}'", shell=True).decode('utf-8')
    percent_str = "Disk usage: " + percent_str + "\n"
    percent_str += "sample count: "
    percent_str += str(stats['count'])
    bot = telepot.Bot(bot_id)
    bot.sendMessage(chat_id, percent_str)
    logging.log(logging.INFO, "Disk full!")
    logging.log(logging.INFO, percent_str)


def get_sample_by_id(city_id):
    """
    Weather request to OpenWeatherMap to given city.
    :param city_id: id of city to be checked in OpenWeatherMap.
    :return: json object containing result of request.
    """
    api_key = os.getenv('OWM_API_KEY')
    url = "https://api.openweathermap.org/data/2.5/weather?id={}&units=metric&appid={}".format(city_id, api_key)
    try:
        r = requests.get(url, timeout=20)
        return r.json()
    except Exception as e:
        return {'cod': 401, 'exception': e}


def get_sample_OCAPI(lat, lon):
    """
    Weather request to OpenWeatherMap One Call API for a city.
    It requests the historical data from the previous day.
    :lat: sample latitude
    :lon: sample longitude
    :return: json object containing result of request.
    """
    api_key = os.getenv('OWM_API_KEY')
    dt = (datetime.date.today() - datetime.timedelta(1)).strftime("%s")
    url = "http://api.openweathermap.org/data/2.5/" \
          "onecall/timemachine?lat={}&lon={}&dt={}&units=metric&appid={}".format(lat, lon, dt, api_key)
    try:
        r = requests.get(url, timeout=20)
        return r.json()
    except Exception as e:
        return {'cod': 401, 'exception': e}


def rearrange_OCAPI_response(city, res):
    """
    Converts results of One Call API to individual sample documents.
    :param city: json object, city description.
    :param res: json object, response of sample request.
    :type res: list of samples ready to be appended to database.
    """
    def ocapi_to_sample(ocapi):
        sample = ocapi
        sample['sys'] = {
                'country': city['country'],
                }
        sample['id'] = city['id']
        return sample
    sample_list = [ocapi_to_sample(res['current'])]
    for s in res['hourly']:
        sample_list += [ocapi_to_sample(s)]

    return sample_list


class WeatherDbManager:
    """
    Class managing the weather samples on local database.

    Parameters
    ----------
    client : MongoClient for the used database.

    """
    def __init__(self, client):
        self.client_ = client
        self.db_ = client['weather']
        self.logger = logging.getLogger(name=__name__)

    def get_sample_stats(self):
        return self.db_.command("collstats", "samples")

    def reset_city_list(self):
        """
        Resets the list of cities to be sampled in following requests.
        """
        city_list = self.get_city_list()
        self.update_city_to_check(city_list)

    def update_city_to_check(self, cities):
        """
        Updates the list of cities to be sampled in following requests.
        :param cities: list of city ids with shape [{'id': 1}, {'id': 2}, ...].
        """
        self.db_.to_check.delete_many({})
        if len(cities) > 0:
            self.db_.to_check.insert_many(cities)

    def get_city_list(self):
        """
        Looks for available cities in the 'cities' collection of the database.
        :return: list of city ids with shape [{'id': 1}, {'id': 2}, ...].
        """
        city_list = []
        city_collection = self.db_.cities
        for city in city_collection.find({}):
            city_list.append({"id": city['id']})
        return city_list

    def get_list_to_check(self):
        """
        Looks for city ids in the 'to_check' collection.
        :return: id list with shape [{'id': 1}, {'id': 2}, ...].
        """
        city_ids = []
        to_check_collection = self.db_.to_check
        for id in to_check_collection.find({}):
            city_ids.append({"id": id['id']})
        return city_ids

    def get_coordinates_by_id(self, city_id):
        """
        Gets the coordinates of a city given its id.
        :param city_id: city id as integer.
        :return: float values for latitude and longitude.
        """
        query = self.db_.cities.find_one({"id": city_id})
        return query['lat'], query['lon']

    def sample_cities(self, n=50):
        """
        Checks the weather on n cities from the 'to_check' collection list.
        and stores them in the 'samples' collection.
        :param n: Number of cities to be checked, default is 50.
        """
        cities_to_check = self.get_list_to_check()
        # If there is too little entries, get the full list and set it up again
        if len(cities_to_check) < n:
            cities_to_check += self.get_city_list()
            self.update_city_to_check(cities_to_check)
        # If it's anyways empty, leave
        if len(cities_to_check) <= 0:
            return

        def sampler(city):
            sample = get_sample_by_id(city["id"])
            if sample['cod'] == 200:
                self.db_.samples.insert_one(sample)
                return True
            else:
                self.logger.error(sample)
                return False

        with ThreadPool(10) as pool:
            sampling = cities_to_check[0:n]
            del cities_to_check[0:n]
            success = pool.map(sampler, sampling)
            repeat = [c for s, c in zip(success, sampling) if s is False]
            if len(repeat) == n:
                self.logger.error("Something went wrong when processing these ids, I'll ignore them next time:")
                self.logger.error(repeat)
            cities_to_check = repeat + cities_to_check

        self.update_city_to_check(cities_to_check)

    def sample_OCAPI(self):
        """
        Requests the weather from the previous day for all cities listed in cities_OneCallAPI collection.
        """
        def sampler(city):
            res = get_sample_OCAPI(city["coord"]["coordinates"][1], city["coord"]["coordinates"][0])
            if res['cod'] == 200:
                sample_list = rearrange_OCAPI_response(city, res)
                self.db_.samples.insert_many(sample_list)
                return True
            else:
                return False

        with ThreadPool(10) as pool:
            sampling = [x for x in self.db_.cities_OneCallAPI.find()]
            success = pool.map(sampler, sampling)
            repeat = [c for s, c in zip(success, sampling) if s is False]
            if len(repeat) == len(sampling):
                self.logger.error("Something went wrong with last One Call API sampling.")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--one-call",
                        help="Request and store information from previous day",
                        action='store_true')
    parser.add_argument("-b", "--bkup_dir",
                        help="Address of output data file (where database is dumped when grows too much)",
                        default="/media/elements/mongodb")
    parser.add_argument("-d", "--debug", action='store_true')

    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s:%(levelname)s:\033[32m%(name)s\033[0m: %(message)s",
                        level=logging.DEBUG if args.debug else logging.INFO,
                        filename="/logs/weather_{}.log".format("OneCall" if args.one_call else "sample"),
                        filemode="a")

    client = pm.MongoClient()
    db_manager = WeatherDbManager(client)

    if is_disk_full():
        report_disk_usage()
        return

    if client.weather.command("collstats", "samples")['count'] > 200000:
        export_samples_to_dir(client, args.bkup_dir)

    if args.one_call:
        report_disk_usage(db_manager.get_sample_stats())
        db_manager.sample_OCAPI()
        return

    db_manager.sample_cities()


if __name__ == '__main__':
    # Check if another instance of the script is running.
    try:
        lock = lock_file(".lock")
        # Run main if get_lock works.
        try:
            main()
        except Exception as inst:
            print(inst)
    except NameError:
        print('lock exists, exiting')
