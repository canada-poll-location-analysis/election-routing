import json
import logging
import urllib.parse
import urllib.request
from collections import defaultdict

import pandas as pd
from tqdm import tqdm

from google_directions import data_exists, get_data, write_result
from sean_logger import setup_logging


def bing_directions(start, stop, BingMapsKey, folder, name=None, outputFormat='json', distanceUnit='km'):
    travelModes = ["transit"]
    data = defaultdict(dict)
    for travelMode in travelModes:
        if data_exists(name, travelMode, folder):
            logging.debug("getting_data")
            directions = get_data(name, travelMode, folder)
            # data[travelMode]['dist'] = directions[0]["legs"][0]["distance"]["value"]
            # data[travelMode]['time'] = directions[0]["legs"][0]["duration"]["value"]
            continue
        wayPpoint1 = ','.join(str(v) for v in start)
        viaWaypoint2 = ','.join(str(v) for v in stop)
        maxSolutions = 3
        if travelMode == "transit":
            routeAttributes = "transitStops"
            timeType = "Arrival"  # Arrival, Departure, LastAvailable
            dateTime = "10/19/2020 20:30:00"
        else:
            routeAttributes = "routePath"
            timeType = "Departure"
            dateTime = "10/19/2015 18:00:00"
        url = f"http://dev.virtualearth.net/REST/v1/Routes/" \
            f"{travelMode}?wayPoint.1={wayPpoint1}&waypoint.2={viaWaypoint2}" \
            f"&routeAttributes={routeAttributes}" \
            f"&timeType={timeType}&dateTime={dateTime}&maxSolutions={maxSolutions}" \
            f"&distanceUnit={distanceUnit}&key={BingMapsKey}"
        url = url.replace(" ", "+")
        logging.debug(name)
        logging.debug(url)
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        logging.debug(response)
        data = json.loads(response.read())
        write_result(data, name, travelMode, folder)
    pass


if __name__ == '__main__':
    setup_logging()
    key_file = "C:/Users/seang/OneDrive/api_keys/api_keys.json"
    in_data_file = "D:/Users/seang/Dropbox/Dropbox/Project Chad/Data For Holly/PolLocsFilteredForHolly_20191201_122250.csv"
    BingMapsKey = json.load(open(key_file)).get("bing_maps")[0]
    folder = './msft-test/'
    direction_data = pd.read_csv(in_data_file, usecols=list(range(22)))
    direction_data = direction_data[direction_data["city"] == "Toronto"]
    p_bar = tqdm(total=len(direction_data))
    for index, row in direction_data.iterrows():
        name = f"{row.ed_num}-{row.pd_pfx}-{row.pd_sufx}"
        name += f"-{row.pd_ab}" if not pd.isna(row.pd_ab) else ""
        logging.debug(name)
        if 500 <= row.pd_pfx <= 599:  # is a mobile polling location
            logging.debug(f"{name} probably is a mobile")
            continue
        if pd.isna(row.pol_loc_lat) and pd.isna(row.pol_loc_lon):
            logging.debug(f"{name} probably aint nothing")
            continue
        stop = (row.pol_loc_lat, row.pol_loc_lon)
        start = (row.pol_div_lat, row.pol_div_lon)
        try:
            bing_directions(
            start,
            stop,
            BingMapsKey,
            folder,
            name=name,
            outputFormat='json',
            distanceUnit='km'
        )
        except:
            pass
        p_bar.update()
        p_bar.set_postfix_str(name)
