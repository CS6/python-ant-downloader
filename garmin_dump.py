#!/usr/bin/python

import sys
import pprint
import logging

import antagent.garmin as garmin

logging.basicConfig(
		level=logging.DEBUG,
		out=sys.stderr,
		format="[%(threadName)s]\t%(asctime)s\t%(levelname)s\t%(message)s")

with open(sys.argv[1]) as file:
	device = garmin.FileDevice(file)
