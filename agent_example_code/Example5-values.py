# Copyright (c) 2015 Iotic Labs Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=invalid-name

# Example: Values

from __future__ import unicode_literals
import datetime

from IoticAgent import IOT, Datatypes, Units


def create_value():
    print("Create Value Example")
    # Note: Values can only be created for Feeds, not Controls

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('create_value_thing')

        # create a Feed
        my_feed = my_thing.create_feed('create_value_point')

        # create some Values for this Feed
        my_feed.create_value('my_value_label', Datatypes.STRING)
        my_feed.create_value('time', Datatypes.FLOAT, 'en', 'Time in seconds', Units.SECOND)
        my_feed.create_value('yet_another_val', Datatypes.DATE, description='Date format: YYYY-MM-DD')

        print("Values created for Feed '%s':" % my_feed.pid)
        print(my_feed.list_value())


def delete_value():
    print("Delete Value Example")
    # If language (lang) is not set, it will add the tags using the default

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('create_delete_value_thing')

        # create a Feed
        my_feed = my_thing.create_feed('create_value_point')

        # create some Values to delete
        my_feed.create_value('level', Datatypes.DECIMAL, description='an example level')
        my_feed.create_value('french_val', Datatypes.STRING, 'fr', 'french value example')

        # delete Value
        my_feed.delete_value('level')
        my_feed.delete_value('french_val', 'fr')


def list_values():
    print("List Values Example")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('create_list_values_thing')

        # create a Feed
        my_feed = my_thing.create_feed('create_value_point')

        # create some Values for this Feed
        my_feed.create_value('my_value_label', Datatypes.STRING)
        my_feed.create_value('time', Datatypes.FLOAT, 'en', 'Time in seconds', Units.SECOND)
        my_feed.create_value('yet_another_val', Datatypes.DATE, description='Date format: YYYY-MM-DD')

        print("Values created for Feed '%s':" % my_feed.pid)
        print(my_feed.list_value())


def share_value():
    print("Share Value Data Example")
    data = {}
    data['current_datetime'] = datetime.datetime.now().isoformat()
    data['random_watt'] = 76

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('create_sharing_thing')

        # create a Feed
        my_feed = my_thing.create_feed('create_value_point')

        # create some Values
        my_feed.create_value('current_datetime', Datatypes.DATETIME, 'en', 'date-time right now')
        my_feed.create_value('random_watt', Datatypes.INT, 'en', 'a random integer', Units.WATT)

        # share data
        my_feed.share(data)


def share_value_with_mime():
    print("Share Value Data with Mime Example")
    # The Mime option is useful to show recipients that you are sending more than just bytes
    # e.g. "idx/2" Corresponds to "text/plain"

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('create_sharing_mime_thing')

        # create a Feed
        my_feed = my_thing.create_feed('create_value_point')

        # create some Values
        my_feed.create_value('random_string', Datatypes.DATETIME, 'en', 'a random string')

        # share data with mime
        my_feed.share('random string data'.encode('utf8'), mime="idx/2")


def delete_all():
    created_things = ['create_value_thing',
                      'create_delete_value_thing',
                      'create_list_values_thing',
                      'create_sharing_thing',
                      'create_sharing_mime_thing', ]

    with IOT.Client('examples.ini') as client:
        for thing in created_things:
            try:
                client.delete_thing(thing)
                print("Thing '%s' deleted" % thing)
            except:
                print("Thing '%s' does not exist" % thing)
                continue


def main():
    # run the examples
    print("Values Examples\n-----------------------")
    try:
        create_value()
        delete_value()
        list_values()
        share_value()
        share_value_with_mime()
        delete_all()  # clear up what we have made; comment this line out if want to keep changes
    except:
        delete_all()

main()
