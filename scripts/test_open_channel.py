#!/usr/bin/python

import gant
import logging
import sys
import time

logging.basicConfig(level=logging.DEBUG, out=sys.stderr, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger()

device = gant.GarminAntDevice()
net = device.networks[0]
chan = device.channels[0]
net.network_key = "\xa8\xa4\x23\xb9\xf5\x5e\x63\xc1"
chan.network = net
chan.channel_type = 0x00
chan.period = 0x1000
chan.search_timeout = 0xff
chan.rf_freq = 0x32
chan.device_type = 0x00
chan.trans_type = 0x00
chan.search_waveform = 0x53
chan.open()
time.sleep(60)


# vim et ts=4 sts=8
