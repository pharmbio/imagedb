FROM ubuntu:22.04

RUN apt-get update && apt-get upgrade -y

RUN apt-get install software-properties-common -y

RUN add-apt-repository ppa:deadsnakes/ppa -y

RUN apt-get update && apt-get install -y \
        python3.10 \
        python3.10-dev \
        python3.10-distutils \
        python3-pip 

# install postgres devtools
RUN apt-get update && apt-get install -y \
        libpq-dev \
        curl 

RUN pip --version

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

COPY requirements.txt /app/

RUN python3.10 -m pip --version

RUN python3.10 -m pip install -r /app/requirements.txt

RUN ln -sf /usr/bin/python3.10 /usr/bin/python3

RUN apt-get install -y libpng-dev libjpeg-dev libopenexr-dev libtiff-dev libwebp-dev

RUN apt-get install -y libgl1-mesa-glx libgl1

ADD . /app
WORKDIR /app

CMD ["python3", "server.py", "--develop"]
