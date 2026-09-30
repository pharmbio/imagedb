FROM python:3.12-slim-bookworm

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Europe/London
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libtiff-tools \
        git \
        vim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install with pip before copying all files, otherwise docker needs to build
# this layer always after file changes in app-dir
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY . /app
