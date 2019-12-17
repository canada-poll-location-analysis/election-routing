import datetime
import json
import logging
import os
from collections import defaultdict

import googlemaps

from toolbox import make_directory
# class googlemaps:
#     class Client:
#         def __init__(*args, **kwargs):
#             pass
#         def directions(*args, **kwargs):
#             return []

def google_directions(start, stop, api_key, folder, name=None, outputFormat='json', units='metric'):
    gmaps = googlemaps.Client(key=api_key)
    travel_modes = ["driving", "walking", "transit"]  # , "bicycling", "transit"]
    departure_times = [
        datetime.datetime(2019, 12, 16, 12, 00)
    ]
    arrival_times = [
        datetime.datetime(2019, 12, 16, 9, 30),
        datetime.datetime(2019, 12, 16, 21, 30)
    ]
    data = defaultdict(dict)
    t_dot = {35007, 35018, 35019, 35020, 35021, 35024, 35027, 35028, 35081, 35090, 35093, 35094, 35095, 35096, 35097,
             35098, 35101, 35108, 35109, 35110, 35115, 35118, 35120, 35121}
    ottawa = {35041, 35064, 35075, 35076, 35077, 35078, 35079}
    kingston = {35044, 35049}
    timmins = {35107}
    for mode in travel_modes:
        fed = int(name.split("-")[0])
        if mode == "transit": #and fed in set().union(t_dot, ottawa, kingston, timmins):
            logging.debug(f"{mode} {fed}")
            for arrival_time in arrival_times:
                directions = get_transit(name, mode, folder, start, stop, units, gmaps, arrival_time, arrival=True)
                if directions:
                    data.update(directions)
            for departure_time in departure_times:
                directions = get_transit(name, mode, folder, start, stop, units, gmaps, departure_time, arrival=False)
                if directions:
                    data.update(directions)
        elif mode in {"driving", "walking"}:
            directions = get_driving_walking(name, mode, folder, start, stop, units, gmaps)
            if directions:
                data.update(directions)
    return data


def get_transit(name, mode, folder, start, stop, units, gmaps, time, arrival):
    data = defaultdict(dict)
    if arrival:
        name = f'{name}-transit-arriveby-{time.strftime("%H%M")}'
    else:
        name = f'{name}-transit-departat-{time.strftime("%H%M")}'
    logging.debug(name)
    key = f'transit-arriveby-{time.strftime("%H%M")}' if arrival else f'transit-deparby-{time.strftime("%H%M")}'
    if data_exists(name, key, folder):
        logging.debug("getting_data")
        directions = get_data(name, key, folder)
        if len(directions) <= 0:
            return None
        data[key]['dist'] = directions[0]["legs"][0]["distance"]["value"]
        data[key]['time'] = directions[0]["legs"][0]["duration"]["value"]
        data[key]['only_walk'] = only_walk(directions)
        return data
    logging.debug("Running")
    if arrival:
        parameters = dict(origin=start, destination=stop, units=units, mode=mode, arrival_time=time)
    else:
        parameters = dict(origin=start, destination=stop, units=units, mode=mode, departure_time=time)
    [logging.debug(f" {k} : {v}") for k, v in parameters.items()]
    directions = gmaps.directions(**parameters)
    if len(directions) <= 0:
        write_result(directions, name, key, folder)
        logging.debug(f"no result for {name}")
        with open("missed.txt", "a+") as missed:
            missed.write(f"{name} \t{start}\t{stop}\t{key}\n")
        return None
    write_result(directions, name, key, folder)
    data[key]['dist'] = directions[0]["legs"][0]["distance"]["value"]
    data[key]['time'] = directions[0]["legs"][0]["duration"]["value"]
    data[key]['only_walk'] = only_walk(directions)
    return data


def only_walk(directions):
    steps = directions[0]['legs'][0]['steps']
    travel_modes = set()
    for step in steps:
        travel_modes.add(step['travel_mode'])
    if len(travel_modes) > 1:
        return False
    return True


def get_driving_walking(name, mode, folder, start, stop, units, gmaps):
    data = defaultdict(dict)
    if data_exists(name, mode, folder):
        logging.debug("getting_data")
        directions = get_data(name, mode, folder)
        data[mode]['dist'] = directions[0]["legs"][0]["distance"]["value"]
        data[mode]['time'] = directions[0]["legs"][0]["duration"]["value"]
        return data
    logging.debug("Running")
    parameters = dict(origin=start, destination=stop, units=units, mode=mode)
    [logging.debug(f" {k} : {v}") for k, v in parameters.items()]
    directions = gmaps.directions(**parameters)
    if len(directions) <= 0:
        logging.debug(f"no result for {name}")
        write_result(directions, name, mode, folder)
        with open("missed.txt", "a+") as missed:
            missed.write(f"{name} \t{start}\t{stop}\n")
        return None
    write_result(directions, name, mode, folder)
    data[mode]['dist'] = directions[0]["legs"][0]["distance"]["value"]
    data[mode]['time'] = directions[0]["legs"][0]["duration"]["value"]
    return data


def data_exists(name, mode, folder):
    fn = f"{folder}{name}-{mode}.json"
    try:
        return os.path.isfile(fn)
    except FileNotFoundError:
        return False


def get_data(name, mode, folder):
    fn = f"{folder}{name}-{mode}.json"
    with open(fn) as json_file:
        data = json.load(json_file)
    return data


def write_result(data, name, mode, folder):
    fn = f"{folder}{name}-{mode}.json"
    make_directory(fn)
    with open(fn, "w") as json_file:
        json.dump(data, json_file, indent=4)
