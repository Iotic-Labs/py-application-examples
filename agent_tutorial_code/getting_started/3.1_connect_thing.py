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

# 3.1_connect_thing.py 12/02/2016 Iotic Labs.
# Connects an already created virtual Thing, or creates a new one.
# Prints information about that Thing (Thing object, lid, guid)

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


def connect_thing(client):
    print("Connecting my first Thing")

    # Create your Thing in this script
    # Note:
    #  Calling 'create_thing' will connect a your script to a virtual Thing if the Local id (lid) is already in use,
    #  if not it creates a new Thing with this lid.
    my_thing = client.create_thing('My_First_Thing')  # GIVE IT A NAME

    # That's all you need to connect (or create) a Thing.

    # Let's have a look at it
    # Print some information about your Thing
    print("About my Thing")
    print("My Thing object:", my_thing)
    print("My Thing local ID (lid):", my_thing.lid)
    print("My Thing globally unique ID (guid):", my_thing.guid)

    return my_thing


# MAIN -------------------------------------------------------------------------------------------------------------
def main():
    with IOT.Client(config='Getting_Started.ini') as client:  # ADD OWN CONFIG .ini HERE
        connect_thing(client)

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
