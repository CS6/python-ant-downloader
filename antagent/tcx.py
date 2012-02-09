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
import time
import lxml.etree as etree
import lxml.builder as builder

import antagent.garmin as garmin

_log = logging.getLogger("antagent.tcx")

E = builder.ElementMaker(nsmap={
    None: "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"})

def format_time(gmtime):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)

def format_intensity(intensity):
    if intensity == 1:
        return "Resting"
    else:
        return "Active"

def format_trigger_method(trigger_method):
    if trigger_method == 0: return "Manual"
    elif trigger_method == 1: return "Distance"
    elif trigger_method == 2: return "Location"
    elif trigger_method == 3: return "Time"
    elif trigger_method == 4: return "HeartRate"

def format_sport(sport):
    if sport == 0: return "Running"
    elif sport == 1: return "Biking"
    elif sport == 2: return "Other"

def format_sensor_state(sensor):
    if sensor: return "Present"
    else: return "Absent"

def create_wpt(wpt):
    elements = [E.Time(format_time(wpt.time.gmtime))]
    if wpt.posn.valid:
        elements.extend([
            E.Position(
                E.LatitudeDegrees(str(wpt.posn.deglat)),
                E.LongitudeDegrees(str(wpt.posn.deglon)))])
    if wpt.alt is not None:
        elements.append(E.AltitudeMeters(str(wpt.alt)))
    if wpt.distance is not None:
        elements.append(E.DistanceMeters(str(wpt.distance)))
    if wpt.heart_rate:
        elements.append(E.HeartRateBpm(E.Value(str(wpt.heart_rate))))
    if wpt.cadence is not None:
        elements.append(E.Cadence(str(wpt.cadence)))
    elements.append(E.SensorState(format_sensor_state(wpt.sensor)))
    if len(elements) > 2:
        return E.Trackpoint(*elements)

def create_lap(lap):
    elements = [
        E.TotalTimeSeconds("%0.2f" % (lap.total_time / 100.)),
        E.DistanceMeters(str(lap.total_dist)),
        E.MaximumSpeed(str(lap.max_speed)),
        E.Calories(str(lap.calories))]
    if lap.avg_heart_rate or lap.max_heart_rate:
        elements.extend([
            E.AverageHeartRateBpm(E.Value(str(lap.avg_heart_rate))),
            E.MaximumHeartRateBpm(E.Value(str(lap.max_heart_rate)))])
    elements.append(
        E.Intensity(format_intensity(lap.intensity)))
    if lap.avg_cadence is not None:
        elements.append(
            E.Cadence(str(lap.avg_cadence)))
    elements.append(E.TriggerMethod(format_trigger_method(lap.trigger_method)))
    wpts = [el for el in (create_wpt(w) for w in lap.wpts) if el is not None]
    if wpts:
        elements.append(E.Track(*wpts))
    return E.Lap(
        {"StartTime": format_time(lap.start_time.gmtime)},
        *elements)

def create_activity(run):
    return E.Activity(
        {"Sport": format_sport(run.sport_type)},
        E.Id(format_time(run.time.gmtime)),
        *list(create_lap(l) for l in run.laps))

def create_document(runs):
    doc = E.TrainingCenterDatabase(
        E.Activities(
            *list(create_activity(r) for r in runs)))
    return doc


# vim: ts=4 sts=4 et
