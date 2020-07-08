#!/usr/bin/env python3
import json
import argparse
import pymongo as pm
import random

# TODO: Change this so that you can give a list of cities as argument to the script.
# The intention is that given a max number of cities, the script will sample evenly the 
# n weather points (cities) closest to the given cities, instead of being given an area 
# to search.
asturias = ((43.67, -7.26), (42.87, -4.49))
sydney = ((-32.472695, 150.222610), (-35.056980, 152.584333))
world = ((90, -180), (-90, 180))
max_cities = 1500


def sort_coordinates(coord):
    """
    Translates the pair of coordinate points to latitude and longitude limits
    :param coord: Pair of coordinate points, with shape ((lat1, lon1), (lat2, lon2))
    :return: [[max_lat, min_lat], [max_lon, min_lon]]
    """
    p1 = coord[0]
    p2 = coord[1]
    if p1[0] > p2[0]:
        limits1 = [p1[0], p2[0]]
    else:
        limits1 = [p2[0], p1[0]]

    if p1[1] > p2[1]:
        limits2 = [p1[1], p2[1]]
    else:
        limits2 = [p2[1], p1[1]]
    return [limits1, limits2]


def get_lon_lat(city):
    """
    Looks for city coordinates in different formats
    :param city: dict object describing a city
    :return: longitude, latitude
    """
    if 'coordinates' in city['coord']:
        ll = city['coord']['coordinates']
        return ll[0], ll[1]
    elif 'lon' in city['coord']:
        return city['coord']['lon'], city['coord']['lat']
    else:
        return city['coord'][0], city['coord'][1]


def randomly_select(item_list, n_samples):
    """
    Select a number of random samples from a list, without repetition.
    It returns the complete list if the number of requested samples is bigger
    than the number of items in the list
    :param item_list: list of items to select from
    :param n_samples: integer, number of samples to take
    :return: list of items, randomly selected
    """
    if n_samples < len(item_list):
        shuffled_list = item_list.copy()
        random.shuffle(shuffled_list)
        return shuffled_list[0:n_samples]
    else:
        return item_list


def get_cities_in_area(coordinates, json_file, exceptions=None, max_cities=None):
    """
    Given the coordinates of two points, finds all cities within these coordinates
    :param coordinates: Pair of coordinate points, with shape ((lat1, lon1), (lat2, lon2))
    :param json_file: json object containing information about all available cities to search
    :param exceptions: list of city ids to be ignored in the search. This is used to avoid duplicates in entry list.
    :param max_cities: integer describing limit of cities to return.
    :return: list of cities within the given coordinate limits
    """
    cities = []
    limits = sort_coordinates(coordinates)
    ignored_ids = [e['id'] for e in exceptions] if exceptions else []
    for city in json_file:
        if city['id'] in ignored_ids:
            continue

        c = city.copy()
        lon, lat = get_lon_lat(city)
        if limits[0][0] > lat > limits[0][1] and limits[1][0] > lon > limits[1][1]:
            c['coord'] = {'coordinates': [lon, lat]}
            cities.append(c)

    if max_cities:
        cities = randomly_select(cities, max_cities)

    return cities


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("city_list",
                        help="File with all cities in owm",
                        default="city.list.json")
    parser.add_argument("-coord", nargs=4,
                        help="Points delimiting a square where cities will be located",
                        default=None)
    args = parser.parse_args()
    file = args.city_list
    if args.coord:
        # TODO: get coordinates from argument
        print(args.coord)

    client = pm.MongoClient()
    db = client['weather']
    cities = db.cities
    cities.create_index([("coord.coordinates", pm.GEO2D)])
    cities_OneCallAPI = db.cities_OneCallAPI
    cities_OneCallAPI.create_index([("coord.coordinates", pm.GEO2D)])

    with open(file) as f:
        cl = json.load(f)
        print("Loading cities from file..")

        asturias_list = get_cities_in_area(asturias, cl)
        sydney_list = get_cities_in_area(sydney, cl)
        localized_cities = asturias_list + sydney_list

        print("Done.")
        if max_cities < len(localized_cities):
            print("too many cities, reduce area!!")
            return

        # Load sparse cities from the rest of the list for one call API
        worlwide_list = get_cities_in_area(world, cl, localized_cities, 1000)

        # Clear all cities:
        print("Clearing old configuration..")
        cities.delete_many({})
        cities_OneCallAPI.delete_many({})
        print("Done.")
        print("Saving selected cities..")
        cities.insert_many(localized_cities)
        cities_OneCallAPI.insert_many(worlwide_list)
        print("Done.")


if __name__ == '__main__':
    main()
