import os
import json

conf_file = os.getenv("CONF_FILE", "settings_dev_local.json")
with open(conf_file) as json_file:
  js_conf = json.load(json_file)

  IMAGES_CACHE_FOLDER = os.getenv("IMAGES_CACHE_DIR", js_conf["IMAGES_CACHE_DIR"])
  IMAGES_THUMB_FOLDER = os.getenv("IMAGES_THUMB_DIR", js_conf["IMAGES_THUMB_DIR"])
  ERROR_LOG_DIR = os.getenv("ERROR_LOG_DIR", js_conf["ERROR_LOG_DIR"])

  DB_USER = os.getenv("DB_USER", js_conf["DB_USER"])
  DB_PASS = os.getenv("DB_PASS", js_conf["DB_PASS"])
  DB_PORT = os.getenv("DB_PORT", js_conf["DB_PORT"])
  DB_NAME = os.getenv("DB_NAME", js_conf["DB_NAME"])
  DB_HOSTNAME = os.getenv("DB_HOSTNAME", js_conf["DB_HOSTNAME"])

  # Get env and set false as default value, convert to python boolean by lowercase string comparison
  EXHAUSTIVE_INITIAL_POLL = os.getenv('EXHAUSTIVE_INITIAL_POLL', js_conf["EXHAUSTIVE_INITIAL_POLL"]).lower() == 'true'
  POLL_DIRS_MARGIN_DAYS = os.getenv('POLL_DIRS_MARGIN_DAYS', js_conf["POLL_DIRS_MARGIN_DAYS"])
  POLL_INTERVAL = os.getenv('POLL_INTERVAL', js_conf["POLL_INTERVAL"]) # sec
  LATEST_FILE_CHANGE_MARGIN = os.getenv('LATEST_FILE_CHANGE_MARGIN', js_conf["LATEST_FILE_CHANGE_MARGIN"]) # sec (always try insert images within this time from latest_filedate_last_poll)
  PROJ_ROOT_DIRS = os.getenv('PROJ_ROOT_DIRS', js_conf["PROJ_ROOT_DIRS"])
  CONTINUOUS_POLLING = os.getenv('CONTINUOUS_POLLING', js_conf["CONTINUOUS_POLLING"]).lower() == 'true'
