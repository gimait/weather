#!/usr/bin/env python
# encoding: utf-8
import json
import argparse
import pymongo as pm

example = {
    "id": 833,
    "name": "Ḩeşār-e Sefīd",
    "state": "",
    "country": "IR",
    "coord": {
        "lon": 47.159401,
        "lat": 34.330502
    }
}
VERBOSE = True

asturias = ((43.67, -7.26), (42.87, -4.49))
sydney = ((-32.472695, 150.222610), (-35.056980, 152.584333))
max_cities = 1500


def sort_coordinates(coord):
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


def get_cities_in_area(coordinates, json_file):
    cities = []
    limits = sort_coordinates(coordinates)
    for city in json_file:
        lon = city['coord']['lon']
        lat = city['coord']['lat']
        if limits[0][0] > lat > limits[0][1] and limits[1][0] > lon > limits[1][1]:
            if VERBOSE:
                print(city["name"])
            cities.append(city)

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
    db = client['city_list']
    cities = db.cities
    #Clear all cities:
    cities.delete_many({})
    with open(file) as f:
        cl = json.load(f)
        asturias_list = get_cities_in_area(asturias, cl)
        sydney_list = get_cities_in_area(sydney, cl)
        all_cities = asturias_list + sydney_list
        if max_cities < len(all_cities):
            print("too many cities, reduce area..")
            return

        cities.insert_many(all_cities)


if __name__ == '__main__':
    main()
