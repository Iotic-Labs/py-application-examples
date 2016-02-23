#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2016 Iotic Labs Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/Iotic-Labs/py-application-examples/blob/master/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# INFO-----------------------------------------------------------------------------------------------------------------

# 7.1_offer_control.py 12/02/2016 Iotic Labs.
# Creates a new Thing (or connects an existing one).
# Prints information about that Thing (Thing object, lid, guid).
# Adds Thing metadata and tags.
# Advertises a Control.
# Adds Control metadata and tags
# Makes Thing private
# Adds Control callback and prints data received.

# PYTHON2 COMPATIBILITY -----------------------------------------------------------------------------------------------
from __future__ import unicode_literals, print_function  # pylint: disable=unused-import

# LOGGING -------------------------------------------------------------------------------------------------------------
# Logging set to only CRITICAL messages by default.  To see more, use logging.INFO, or to see loads, logging.DEBUG
import logging
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.CRITICAL)

# IMPORTS -------------------------------------------------------------------------------------------------------------
import time

# IOTIC AGENT IMPORTS -------------------------------------------------------------------------------------------------
from IoticAgent import IOT

# ---------------------------------------------------------------------------------------------------------------------


def create_thing(client):
    print("Creating my Thing")

    # Create your Thing in this script
    # Note:
    #  Calling 'create_thing' will create a new Thing, unless the Thing local ID (lid) is already in use.
    #  If it is, it will connect your script to that Thing.
    my_thing = client.create_thing('My_Controllable_Thing')  # GIVE IT A NAME

    # Let's have a look at it
    # print some information about your Thing
    print("About my Thing")
    print("My Thing object:", my_thing)
    print("My Thing local ID (lid):", my_thing.lid)
    print("My Thing globally unique ID (guid):", my_thing.guid)

    return my_thing


def set_private(my_thing):
    # Make Thing private
    my_thing.set_public(False)  # to make it public, change to True


def add_thing_metadata(my_thing):
    print ("Adding Thing metadata")

    # Add Thing metadata
    # get the metadata
    with my_thing.get_meta() as my_metadata:
        # set a label
        print("Setting default language label")
        my_metadata.set_label('My Controllable Thing')  # uses default language
        # set a description
        print("Setting default language description")
        my_metadata.set_description('Offers a control.')  # uses default language
        print("Setting location")
        # set a location
        latitude = 51.5049707142585
        longitude = -0.087662711739
        my_metadata.set_location(latitude, longitude)

        # print what you just set
        # get and print the labels
        my_labels = my_metadata.get_labels()
        print("Returned labels:")
        print(my_labels)
        # get and print the descriptions
        my_descriptions = my_metadata.get_descriptions()
        print("Returned descriptions:")
        print(my_descriptions)
        # get the location
        my_lat, my_lon = my_metadata.get_location()
        print("Returned location lat = %f & lon = %f" % (my_lat, my_lon))


def add_thing_tags(my_thing):
    print("Adding Thing tags")

    # Create tags
    # If language (lang) is not set, it will add the tags using the default
    tags = ['HelloWorld', 'Controllable', 'Test']
    # Requires a list of strings without spaces
    # create tags (returns nothing)
    print("Creating default language Thing tags")
    my_thing.create_tag(tags)
    # list those tags
    print("List of Tags for this Thing:")
    tag_list = my_thing.list_tag()
    print(tag_list)


def create_control(my_thing):
    print("Creating a Control")
    # create a Control
    my_control = my_thing.create_control('My_Controllable_Point', ctrl_callback)

    # Let's have a look at it
    # Print some information about the Control you created
    print("About my Control")
    print("My Control object:", my_control)
    print("My Control local ID (pid):", my_control.pid)
    print("My Thing local ID that advertises this Control (lid):", my_control.lid)
    print("My Control globally unique ID (guid):", my_control.guid)  # guid or gpid
    print("Check this is a feed or control:", my_control.foc)

    return my_control


def add_control_metadata(my_control):
    print("Setting Control metadata")

    # Create control metadata
    # get the metadata
    with my_control.get_meta() as my_metadata:
        # create a label
        print("Setting default language Control label")
        my_metadata.set_label('My Controllable Point')  # uses default language
        # create a description
        print("Setting default language Control label")
        my_metadata.set_description('"Just prints the data received"')  # uses default language

        # print what you just set
        # get and print the labels
        my_labels = my_metadata.get_labels()
        print("Returned labels:")
        print(my_labels)
        # get and print the descriptions
        my_descriptions = my_metadata.get_descriptions()
        print("Returned descriptions:")
        print(my_descriptions)


def ctrl_callback(data):
    print("Callback receiving data:", data)


# MAIN -------------------------------------------------------------------------------------------------------------
def main():
    with IOT.Client('Control_Offer.ini') as client:
        my_thing = create_thing(client)
        my_control = create_control(my_thing)
        set_private(my_thing)
        add_thing_metadata(my_thing)
        add_thing_tags(my_thing)
        add_control_metadata(my_control)

        while True:
            try:
                print("Main running, press ctrl+c to quit.")
                time.sleep(10)
            except KeyboardInterrupt:
                break


# RUN --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# END --------------------------------------------------------------------------------------------------
