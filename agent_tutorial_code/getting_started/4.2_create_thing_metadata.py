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

# 04_create_thing.py 12/02/2016 Iotic Labs.
# Creates a new Thing (or connects an existing Thing).

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
    my_thing = client.create_thing('My_New_Thing')  # GIVE IT A NAME

    # Let's have a look at it
    # print some information about your Thing
    print("About my Thing")
    print("My Thing object:", my_thing)
    print("My Thing local ID (lid):", my_thing.lid)
    print("My Thing globally unique ID (guid):", my_thing.guid)

    return my_thing


def add_thing_metadata(my_thing):
    print ("Adding Thing metadata")

    # Add Thing metadata
    # get the metadata
    with my_thing.get_meta() as my_metadata:
        # create a label
        print("Setting default language label")
        my_metadata.set_label('My First Thing')  # uses default language
        # create a description
        print("Setting default language description")
        my_metadata.set_description('This is a description.')  # uses default language
        print("Setting location")
        # create a location
        latitude = 51.5049707142585
        longitude = -0.087662711739
        my_metadata.set_location(latitude, longitude)

    # Print what you have set
    with my_thing.get_meta() as my_metadata:
        print("My Thing's metadata object:", my_metadata)


def add_thing_tags(my_thing):

    # If language (lang) is not set, it will add the tags using the default
    print("Adding Thing tags")
    tags = ['HelloWorld', 'tag1', 'tag2']
    # Requires a list of strings without spaces
    # create tags (returns nothing)
    print("Creating default language Thing tags")
    my_thing.create_tag(tags)

    # list those tags
    print("List of Tags for this Thing:")
    tag_list = my_thing.list_tag()
    print(tag_list)


# MAIN -------------------------------------------------------------------------------------------------------------------------------------
def main():
    with IOT.Client(config='Getting_Started.ini') as client:  # ADD OWN CONFIG .ini HERE
        my_thing = create_thing(client)
        add_thing_metadata(my_thing)
        add_thing_tags(my_thing)

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
