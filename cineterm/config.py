import os
import json

LIB_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../cineterm"))

ROOT_PATH = os.path.dirname(LIB_PATH)

LOG_PATH = ROOT_PATH + "/logfile.log"

CACHE_PATH = f"{LIB_PATH}/cache/yts_movies_df.pkl"

with open(f"{ROOT_PATH}/config.json", 'r') as f:
    config = json.load(f)

# qbittorrent details
QB_USERNAME = config["qb_username"]
QB_PASSWORD = config["qb_password"]
# Download dir
DOWNLOAD_DIR = config["download_dir"]
home_dir = os.path.expanduser('~')
DOWNLOAD_DIR = DOWNLOAD_DIR.replace('~', home_dir)
