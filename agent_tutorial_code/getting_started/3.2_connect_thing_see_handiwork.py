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

# 3.1_connect_thing_see_handiwork.py 12/02/2016 Iotic Labs.
# Connects an already created virtual Thing, or creates a new one.
# Prints information about that Thing (Thing object, lid, guid).
# Gets and prints metadata (eg metadata added in the UI).
# Lists and prints tags (eg tags added in the UI).
# Lists and prints information about any Iotic connections (eg feeds followed in the UI).

# PYTHON2 COMPATIBILITY -----------------------------------------------------------------------------------------------
from __future__ import unicode_literals, print_function

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


def connect_thing(client):
    print("Connecting My First Thing")

    # Create your Thing in this script
    # Note:
    #  Calling 'create_thing' will connect a your script to a virtual Thing if the Local id (lid) is already in use,
    #  if not it creates a new Thing with this lid.
    my_thing = client.create_thing('My_First_Thing')  # GIVE IT A NAME

    # Let's have a look at it
    # print some information about your Thing
    print("About my Thing")
    print("My Thing object:", my_thing)
    print("My Thing local ID (lid):", my_thing.lid)
    print("My Thing globally unique ID (guid):", my_thing.guid)

    return my_thing


def show_metadata(my_thing):
    print("My metadata (simplified)")

    # Get and print the metadata you set in the UI
    with my_thing.get_meta() as my_metadata:
        # get the label
        my_labels = my_metadata.get_labels()
        print("Returned labels:")
        print(my_labels)
        # get the description
        my_descriptions = my_metadata.get_descriptions()
        print("Returned descriptions:")
        print(my_descriptions)
        # get the location
        # Note:
        #  If location not set, returns error
        my_lat, my_lon = my_metadata.get_location()
        print("Returned location lat = %f & lon = %f" % (my_lat, my_lon))

        # List and print tags you set in the UI
        print("Tags")
        print("List of Tags for this Thing:")
        tag_list = my_thing.list_tag()
        print(tag_list)


def show_subscriptions(my_thing):
    print("My subscriptions")

    # List and print any subscriptions (Feeds following or Controls attached to)
    # Note:
    #  In sub_list, 'id' is the Feed/Control global point ID (gpid)
    sub_list = my_thing.list_connections()
    print("Subscription list: ", sub_list)


# MAIN -------------------------------------------------------------------------------------------------------------
def main():
    with IOT.Client(config='Getting_Started.ini') as client:  # ADD OWN CONFIG .ini HERE
        my_thing = connect_thing(client)
        show_metadata(my_thing)
        show_subscriptions(my_thing)

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
