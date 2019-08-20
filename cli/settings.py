import os

IMAGES_ROOT_FOLDER  = os.getenv("IMAGES_ROOT_FOLDER", "/share/mikro/IMX/MDC_pharmbio/")
IMAGES_CACHE_FOLDER = os.getenv("IMAGES_CACHE_FOLDER", "/share/imagedb/image-cache")
IMAGES_THUMB_FOLDER = os.getenv("IMAGES_THUMB_FOLDER", "/share/imagedb/thumbs/")

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "example")
DB_PORT = os.getenv("DB_PORT", 27017)
DB_HOSTNAME = os.getenv("DB_HOSTNAME", "image-mongo")

# Get env and set false as default value, convert to python boolean by lowercase string comparison
EXHAUSTIVE_INITIAL_POLL = os.getenv('EXHAUSTIVE_INITIAL_POLL', 'false').lower() == 'true'
POLL_DIRS_MARGIN_DAYS = os.getenv('POLL_DIRS_MARGIN_DAYS', 3)
POLL_INTERVAL = os.getenv('POLL_INTERVAL', 300) # sec
LATEST_FILE_CHANGE_MARGIN = os.getenv('LATEST_FILE_CHANGE_MARGIN', 7200) # sec (always try insert images within this time from latest_filedate_last_poll)
PROJ_ROOT_DIRS = os.getenv('PROJ_ROOT_DIRS', [ "Aish/",
                                               "exp-CombTox/",
                                               "PolinaG-ACHN",
                                               "PolinaG-KO",
                                               "PolinaG-MCF7",
                                               "PolinaG-U2OS",
                                               "exp-TimeLapse/",
                                               "exp-WIDE/"
                                              ])
CONTINUOUS_POLLING = os.getenv('CONTINUOUS_POLLING', 'false').lower() == 'true'
