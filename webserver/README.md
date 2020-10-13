# webserver - imagedb

```
# Run with docker-compose

# server devel
WEBROOT=/home/anders/projekt/imagedb/webserver SHARE_IMAGEDB=/share/imagedb SHARE_MIKRO=/share/mikro docker-compose up

# Tunnel web


# Build dockerfile
docker build -t pharmbio/imagedb-webserver .

# Push
docker login
docker push pharmbio/imagedb-webserver

```

