# cli - imagedb

Start database:
```
cd ../db/
docker-compose -f ../db/docker-compose.yml up -d
```

Run project
```
# create venv

# activate venv
source venv/bin/activate

# sync requirements file with venv
source venv/bin/activate
pip freeze > requirements.txt

# build container
docker build -t pharmbio/imagedb-cli .

# push container
docker push pharmbio/imagedb-cli

# run app with docker-compose and dev-settings
SHARE_MIKRO=/home/anders/pharmbio/imageDB/share/mikro SHARE_IMAGEDB=/home/anders/pharmbio/imageDB/share/imagedb APPROOT=/home/anders/pharmbio/imageDB/ docker-compose up

SHARE_MIKRO=/share/mikro SHARE_IMAGEDB=/share/imagedb APPROOT=/home/anders/projekt/imagedb/cli docker-compose up

# log-in to container and run script
docker exec -it imagedb-app bash

python3 import-images-v01.py

```

