FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip

# opencv-python lib deps
RUN apt-get install -y \
        libsm6 \
        libxext6 \
        libxrender-dev

# install postgres devtools
RUN apt-get update && apt-get install -y \
        libpq-dev

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

ADD . /app
WORKDIR /app

CMD ["python3", "server.py", "--develop"]
