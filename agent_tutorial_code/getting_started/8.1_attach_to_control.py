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

# 8.1_attach_to_control.py 12/02/2016 Iotic Labs.
# Creates a new Thing (or connects an existing one).
# Prints information about that Thing (Thing object, lid, guid).
# Attaches to remote Control using hard coded local point ID.

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
    my_thing = client.create_thing('My_Controller_Thing')  # GIVE IT A NAME

    # Let's have a look at it
    # print some information about your Thing
    print("About my Thing")
    print("My Thing object:", my_thing)
    print("My Thing local ID (lid):", my_thing.lid)
    print("My Thing globally unique ID (guid):", my_thing.guid)

    return my_thing


def attach_to_control(my_thing):
    print("Attaching to remote Control")

    # Attach your Thing to someone else's Control Point with the intention of
    # sending an order (asking or telling) to it to do something
    # Note:
    #  Calling 'attach' will return the subscription object regardless of whether it already existed
    remote_control_gpid = '348603c2-e29b-fd53-e9b5-ad9d852ede5c'  # ADD THE GLOBAL POINT ID OF CONTROL YOU WISH TO ATTACH TO
    # attach to Control
    remote_control = my_thing.attach(remote_control_gpid)
    print("Remote Control subscription object:", remote_control)


# MAIN -------------------------------------------------------------------------------------------------------------
def main():
    with IOT.Client('Control_Actuate.ini') as client:
        my_thing = create_thing(client)
        attach_to_control(my_thing)

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
