import os
import json

# conf file location can be overridden by ENV-VAR
conf_file = os.getenv("CONF_FILE", "settings_dev_local.json")
with open(conf_file) as json_file:
  js_conf = json.load(json_file)

  IMAGES_ROOT_FOLDER  = os.getenv("IMAGES_ROOT_DIR", js_conf["IMAGES_ROOT_DIR"])
  IMAGES_CACHE_FOLDER = os.getenv("IMAGES_CACHE_DIR", js_conf["IMAGES_CACHE_DIR"])
  IMAGES_THUMB_FOLDER = os.getenv("IMAGES_THUMB_DIR", js_conf["IMAGES_THUMB_DIR"])
  ERROR_LOG_DIR = os.getenv("ERROR_LOG_DIR", js_conf["ERROR_LOG_DIR"])

  DB_USER = os.getenv("DB_USER", js_conf["DB_USER"])
  DB_PASS = os.getenv("DB_PASS", js_conf["DB_PASS"])
  DB_PORT = os.getenv("DB_PORT", js_conf["DB_PORT"])
  DB_NAME = os.getenv("DB_NAME", js_conf["DB_NAME"])
  DB_HOSTNAME = os.getenv("DB_HOSTNAME", js_conf["DB_HOSTNAME"])

  ADMINER_URL = os.getenv("ADMINER_URL", js_conf["ADMINER_URL"])

  PIPELINEGUI_URL = os.getenv("PIPELINEGUI_URL", js_conf["PIPELINEGUI_URL"])
  PIPELINEGUI_STATIC_RESULTS_DIR = os.getenv("PIPELINEGUI_STATIC_RESULTS_DIR", js_conf["PIPELINEGUI_STATIC_RESULTS_DIR"])
