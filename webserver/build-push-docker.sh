docker build -t pharmbio/imagedb-web:master .
docker push pharmbio/imagedb-web:master

docker build -t ghcr.io/pharmbio/imagedb-web:master .
docker push ghcr.io/pharmbio/imagedb-web:master
