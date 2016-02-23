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

# Example: Feeds

from __future__ import unicode_literals

from IoticAgent import IOT


def create_feed():
    print("Create Feed Example")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_to_create_feed')

        # create a Feed
        my_feed = my_thing.create_feed('my_new_feed')
        print("My Feed object:", my_feed)
        print("My Feed local ID (pid):", my_feed.pid)
        print("My Thing local ID that advertises this Feed (lid):", my_feed.lid)
        print("My Thing's globally unique ID (guid):", my_feed.guid)
        print("Check this is a feed or control:", my_feed.foc)


def rename_feed():
    print("Rename Feed Example")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_to_rename_feed')

        # create Feed to rename
        my_feed = my_thing.create_feed('to_be_renamed')
        print("Point id for my feed:", my_feed.pid)

        # rename Feed
        my_feed.rename('example_renamed_feed')
        print("New pid for my thing:", my_feed.pid)


def delete_feed():
    print("Delete Feed Example")

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('example_delete_feed')

        # create Feed to delete
        my_thing.create_feed('delete_feed')

        # delete Feed
        my_thing.delete_feed('delete_feed')


def list_feeds():
    print("List Feeds for [My] Thing Example")
    # Lists have a default limit of 500 and offset of 0

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('list_feed_thing')

        # create a couple of Feeds
        my_thing.create_feed('first_feed')
        my_thing.create_feed('second_feed')

        # list all the Feeds
        print("List of Things in this agent:")
        list_all_feeds = my_thing.list_feeds()
        print(list_all_feeds)

        # list the details of one particular Feed
        print("Detailed list for one Feed:")
        feed_list = my_thing.list_feeds('first_feed')
        print(feed_list)


def delete_all():
    created_things = ['thing_to_create_feed',
                      'thing_to_rename_feed',
                      'example_delete_feed',
                      'list_feed_thing', ]

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
    print("Feeds Examples\n-----------------------")
    create_feed()
    rename_feed()
    delete_feed()
    list_feeds()
    delete_all()  # clear up what we have made; comment this line out if want to keep changes

main()
