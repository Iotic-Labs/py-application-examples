# /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 Simple Iotic/Energenie using the style adopted by D.J.Whale
 Based on
 mihome_energy_monitor.py  28/05/2016  D.J.Whale:
 "A simple demo of monitoring and logging energy usage of mihome devices"

Example demonstrating:

- Creation of Iotic Things for each of the three types of Energenie devices, Motion/Open-Close/PlugSocket
- Creation of Iotic Feeds of data for each of these devices
- Setting of Values for these devices (Old style without using value-skeleton wrappers)
"""

# Python 2 backwards compatibility
from __future__ import unicode_literals, print_function

from time import sleep
import Logger

import energenie
import datetime

import pprint
PPR = pprint.PrettyPrinter(indent=4)

from IoticAgent import IOT, Datatypes, Units

APP_DELAY = 2


def create_energenie_thing(client):

    t_energenie = client.create_thing("energenie2")

    with t_energenie.get_meta() as t_energenie_meta:
        t_energenie_meta.set_label("Energenie 2")
        t_energenie_meta.set_description("Example energenie using DW's latest code")
        t_energenie_meta.set_location(52.00, 0.00)

    t_energenie.create_tag(["energenie", "mihome"])

    return t_energenie


def create_monitor_feed(t_energenie):
    f_monitor = t_energenie.create_feed("Power-monitor-feed")
    with f_monitor.get_meta() as f_monitor_meta:
        f_monitor_meta.set_label("latest monitor values")

    f_monitor.create_value('timestamp', Datatypes.DATETIME, lang='en', description="Time of reading")
    f_monitor.create_value('power', Datatypes.DECIMAL, lang='en', unit=Units.WATT, description="Real Power")

    return f_monitor


def create_open_feed(t_energenie):
    f_open = t_energenie.create_feed("Open-sensor-feed")
    with f_open.get_meta() as f_monitor_meta:
        f_monitor_meta.set_label("latest open sensor values")

    f_open.create_value('timestamp', Datatypes.DATETIME, lang='en', description="Time of reading")
    f_open.create_value('open', Datatypes.BOOLEAN, lang='en', description="Open or closed")

    return f_open


def create_motion_feed(t_energenie):
    f_motion = t_energenie.create_feed("Open-sensor-feed")
    with f_motion.get_meta() as f_monitor_meta:
        f_monitor_meta.set_label("latest motion sensor values")

    f_motion.create_value('timestamp', Datatypes.DATETIME, lang='en', description="Time of reading")
    f_motion.create_value('motion', Datatypes.BOOLEAN, lang='en', description="Motion detected")

    return f_motion


def sensor_monitor_loop(feeds, devices):

    d_plug, d_open, d_motion = devices
    f_monitor, f_open, f_motion = feeds
    # Process any received messages from the real radio
    energenie.loop()

    print("Checking device status d_plug")
    try:
        power = d_plug.get_real_power()
        print("Power: %s" % str(power))
        share_dict = {u"timestamp": datetime.datetime.now().isoformat(), u"power": power}
        PPR.pprint(share_dict)
        f_monitor.share_async(share_dict)
    except Exception as e:  # pylint: disable=broad-except
        print("failed to get power")
        print(e)

    print("Checking device status d_open")
    try:
        switch = d_open.get_switch_state()
        print("Open: %s" % str(switch))
        if switch is not None:
            share_dict = {u"timestamp": datetime.datetime.now().isoformat(), u"open": switch}
            PPR.pprint(share_dict)
            f_open.share_async(share_dict)
    except Exception as e:  # pylint: disable=broad-except
        print("failed to get switch state")
        print(e)

    print("Checking device status d_motion")
    try:
        switch = d_motion.get_switch_state()
        print("Motion: %s" % str(switch))
        if switch is not None:
            share_dict = {u"timestamp": datetime.datetime.now().isoformat(), u"motion": switch}
            PPR.pprint(share_dict)
            f_motion.share_async(share_dict)
    except Exception as e:  # pylint: disable=broad-except
        print("failed to get switch")
        print(e)

    sleep(APP_DELAY)


def main():
    print("Starting energy monitor example")

    energenie.init()

    # Replace the names here with those in your own registry.kvs
    d_plug = energenie.registry.get("plug893")
    d_open = energenie.registry.get("open2664")
    d_motion = energenie.registry.get("motion4162")
    devices = (d_plug, d_open, d_motion)

    with IOT.Client(config="energenie_pi_staging.ini") as client:
        # create energenie "Thing"
        t_energenie = create_energenie_thing(client)
        # create a feed for each room and add its instance to the rooms dict
        f_monitor = create_monitor_feed(t_energenie)
        f_open = create_open_feed(t_energenie)
        f_motion = create_motion_feed(t_energenie)
        feeds = (f_monitor, f_open, f_motion)
        t_energenie.set_public(True)

        # provide a default incoming message handler, useful for logging every message
        def incoming(address, message):
            print("\nIncoming from %s" % str(address))
            Logger.logMessage(message)
        energenie.fsk_router.when_incoming(incoming)
        print("Logging to file:%s" % Logger.LOG_FILENAME)

        try:
            while True:
                sensor_monitor_loop(feeds, devices)
        finally:
            energenie.finished()

if __name__ == "__main__":
    main()
