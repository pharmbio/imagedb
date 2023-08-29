docker build -t ghcr.io/pharmbio/imagedb-web:devel .
docker push ghcr.io/pharmbio/imagedb-web:devel

read -p "Do you want to push with \"stable\" tag also? [y|n]" -n 1 -r < /dev/tty
echo
if ! grep -qE "^[Yy]$" <<< "$REPLY"; then
    exit 1
fi

docker build -t ghcr.io/pharmbio/imagedb-web:stable .
docker push ghcr.io/pharmbio/imagedb-web:stable

