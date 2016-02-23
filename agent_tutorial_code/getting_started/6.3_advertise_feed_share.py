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

# 6.3_advertise_feed_share.py 12/02/2016 Iotic Labs.
# Creates a new Thing (or connects an existing one).
# Prints information about that Thing (Thing object, lid, guid).
# Adds Thing metadata and tags.
# Advertises a feed.
# Adds feed metadata and tags
# Makes public
# Shares timestamp as test data

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
    my_thing = client.create_thing('My_Feed_Advertiser')  # GIVE IT A NAME

    # Let's have a look at it
    # print some information about your Thing
    print("About my Thing")
    print("My Thing object:", my_thing)
    print("My Thing local ID (lid):", my_thing.lid)
    print("My Thing globally unique ID (guid):", my_thing.guid)

    return my_thing


def set_public(my_thing):
    print ("Setting to public")

    # Make Thing public
    my_thing.set_public(True)  # to make it private, change to False


def create_feed(my_thing):
    print("Creating a Feed")

    # Create a Feed
    my_feed = my_thing.create_feed('My_New_Feed')

    # Let's have a look at it
    # Print some information about the Feed you created
    print("About my Feed")
    print("My Feed object:", my_feed)
    print("My Feed local point ID (pid):", my_feed.pid)
    print("My Feed global point ID (guid):", my_feed.guid)
    print("Check this is a feed or control:", my_feed.foc)

    return my_feed


def add_thing_metadata(my_thing):
    print ("Adding Thing metadata")

    # Add thing metadata
    # get the metadata
    with my_thing.get_meta() as my_metadata:
        # create a label
        print("Setting default language label")
        my_metadata.set_label('My Feed Advertiser')  # uses default language
        # create a description
        print("Setting default language description")
        my_metadata.set_description('This Thing advertises a Feed and shares a timestamp.')  # uses default language
        print("Setting location")
        # create a location
        latitude = 51.5136
        longitude = -0.0981
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

    # If language (lang) is not set, it will add the tags using the default
    tags = ['HelloWorld', 'Advertiser', 'Timestamp']
    # Requires a list of strings without spaces
    # create tags (returns nothing)
    print("Creating default language Thing tags")
    my_thing.create_tag(tags)
    # list those tags
    print("List of Tags for this Thing:")
    tag_list = my_thing.list_tag()
    print(tag_list)


def add_feed_metadata(my_feed):
    print("Adding Feed metadata")

    # Add Feed metadata
    # get the metadata
    with my_feed.get_meta() as my_metadata:
        # create a label
        print("Setting default language Feed label")
        my_metadata.set_label('My New Feed')  # uses default language
        # create a description
        print("Setting default language Feed label")
        my_metadata.set_description('"Shares timestamp as test feed"')  # uses default language
        # print what you just set
        # get and print the labels
        my_labels = my_metadata.get_labels()
        print("Returned labels:")
        print(my_labels)
        # get and print the descriptions
        my_descriptions = my_metadata.get_descriptions()
        print("Returned descriptions:")
        print(my_descriptions)


def share_data(my_feed):
    print("Sharing Values")
    current_values = {}
    current_values["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    my_feed.share(current_values)


# MAIN -------------------------------------------------------------------------------------------------------------
def main():
    with IOT.Client('Feed_Advertise.ini') as client:
        my_thing = create_thing(client)
        my_feed = create_feed(my_thing)
        set_public(my_thing)
        add_thing_metadata(my_thing)
        add_thing_tags(my_thing)
        add_feed_metadata(my_feed)

        while True:
            try:
                print("Main running, press ctrl+c to quit.")
                share_data(my_feed)
                time.sleep(10)
            except KeyboardInterrupt:
                break


# RUN --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# END --------------------------------------------------------------------------------------------------
