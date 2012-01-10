#!/usr/bin/python

import gant
import logging
import sys
import time

logging.basicConfig(level=logging.DEBUG, out=sys.stderr, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger()

device = gant.GarminAntDevice()
net = device.claim_network()
chan = device.claim_channel()
for n in range(0, 1):
	net.network_key = "\xa8\xa4\x23\xb9\xf5\x5e\x63\xc1"
	chan.network = net
	chan.channel_type = 0x00
	chan.period = 0x1000
	chan.search_timeout = 0xff
	chan.rf_freq = 0x32
	chan.device_type = 0x00
	chan.trans_type = 0x00
	chan.open()
	while True:
		try: print chan.get_channel_status()
		except: log.error("channel_status failed.", exc_info=True); raise
		try: print chan.get_channel_id()
		except: log.error("channel_id failed.", exc_info=True); raise
		time.sleep(2)
	chan.close()
device.close()
# vim et ts=4 sts=8
