# imagedb

Start database:
```
docker-compose -f docker-compose-imagemongo.yml up -d
```

Run project
```
# create venv

# activate venv
source venv/bin/activate

# sync requirements file with venv
pip freeze > requirements.txt

# build container
docker build -t pharmbio/imagedb-app .

# run app with docker-compose and dev-settings
SHARE_MIKRO=/home/anders/pharmbio/imageDB/share/mikro SHARE_IMAGEDB=/home/anders/pharmbio/imageDB/share/imagedb APPROOT=/home/anders/pharmbio/imageDB/ docker-compose up

# log-in to container and run script
docker exec -it imagedb-app bash

python3 import-images-v01.py

```

