import json
import logging

import pandas as pd
from tqdm import tqdm

from google_directions import google_directions
from sean_logger import setup_logging
from twillo_info import alert_complete, alert_messge

key_file = "C:/Users/seang/OneDrive/api_keys/api_keys.json"
in_data_file = "D:/Users/seang/Dropbox/Dropbox/Project Chad/Data For Holly/PolLocsFilteredForHolly_20191201_122250.csv"
results = "./directions/"

google_api_keys = json.load(open(key_file)).get("google_maps")
bing_api_keys = json.load(open(key_file)).get("bing_maps")
direction_data = pd.read_csv(in_data_file, usecols=list(range(22)))

new_modes = ["driving", "walking"]
dist_types = ["dist", "time"]

setup_logging()

for mode in new_modes:
    for dist_type in dist_types:
        direction_data[f'{mode}_{dist_type}'] = ""

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
    pol_loc_lon_lat = (row.pol_loc_lat, row.pol_loc_lon)
    pol_div_lon_lat = (row.pol_div_lat, row.pol_div_lon)
    data = google_directions(pol_div_lon_lat, pol_loc_lon_lat, google_api_keys[0],
                             name=name, outputFormat='json', units='metric', folder=results)
    if data is None:
        continue
    for mode, dist_types in data.items():
        for dist_type, value in dist_types.items():
            direction_data.at[index, f'{mode}_{dist_type}'] = value
    p_bar.update()
    p_bar.set_postfix_str(name)
    if index % 100 == 0:
        logging.debug('writing to files')
        direction_data.to_csv("distance_matrix.csv", index=False)
        try:
            direction_data.to_csv("D:/Users/seang/Dropbox/Dropbox/Project Chad/Data For Holly/distance_matrix.csv", index = False)
        except:
            pass
alert_complete()

print("Fin")
