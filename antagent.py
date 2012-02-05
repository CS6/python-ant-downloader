#!/usr/bin/python

# Copyright (c) 2012, Braiden Kindt.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
# 
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS
# ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import logging
import sys
import time
import struct

import antagent
import antagent.garmin as garmin

logging.basicConfig(
        level=logging.DEBUG,
        out=sys.stderr,
        format="[%(threadName)s]\t%(asctime)s\t%(levelname)s\t%(message)s")

_log = logging.getLogger()

host = antagent.UsbAntFsHost()

def dump_record(record, file):
    pid, length, data = record
    file.write(struct.pack("<HH", pid, length))
    file.write(data)

def dump_list(data, file):
        for record in data:
            try:
                dump_list(record, file)
            except TypeError:
                dump_record(record, file)

try:
    while True:
        try:
            _log.info("Searching for ANT devices...")
            beacon = host.search()
            if beacon and beacon.data_availible:
                _log.info("Linking...")
                host.link()
                _log.info("Pairing with device...")
                host.auth()
                with open(time.strftime("%Y%m%d-%H%M%S.raw"), "w") as file:
                    _log.info("Dumping data to %s.", file.name)
                    dump_list(garmin.A000(garmin.stream_executor, host), file)
                    dump_list(garmin.A1000(garmin.stream_executor, host), file)
                _log.info("Closing session...")
                host.disconnect()
        except antagent.AntError:
           _log.warning("Caught error while communicating with device, will retry.", exc_info=True) 
finally:
    try: host.close()
    except Exception: _log.warning("Failed to cleanup resources on exist.", exc_info=True)

# vim: ts=4 sts=4 et
