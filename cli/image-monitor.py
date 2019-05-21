#!/usr/bin/env python3
import time
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Starting monitor loop")

while True:
    time.sleep(3600)
