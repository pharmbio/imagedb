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