# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.
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

# PYTHON2 COMPATIBILITY -----------------------------------------------------------------------------------------------
from __future__ import unicode_literals, print_function  # pylint: disable=unused-import

# LOGGING -------------------------------------------------------------------------------------------------------------
# Logging set to only CRITICAL messages by default.  To see more, use logging.INFO, or to see loads, logging.DEBUG
import logging
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.CRITICAL)

# IMPORTS -------------------------------------------------------------------------------------------------------------

import sys
from functools import partial

# IOTIC AGENT IMPORTS -------------------------------------------------------------------------------------------------

from IoticAgent import IOT
from IoticAgent import Datatypes

# THING SETUP -----------------------------------------------------------------------------------------------


# Adds basic chat tags to the new Thing
def add_tags(my_thing):

    # Delete thing's tags
    my_thing_tags = my_thing.list_tag()

    if any(my_thing_tags):
        my_thing.delete_tag(my_thing_tags['en'])

    # Add new tags
    tags = ['messenger']
    my_thing.create_tag(tags)


# Adds basic metadata to the new Thing
def add_metadata_information(thing_meta):
    # Thing visible name in Iotic Space
    thing_meta.set_label('iotic_communicator')
    # Thing description
    thing_meta.set_description('basic thing to chat with other thing in Iotic Space')


# Initialize a new thing assigned to the Agent
def setup_thing(client, name):
    print("Connecting to your thing", sep=' ', end=' ... ')
    sys.stdout.flush()

    # 1- Get/Create a thing with the given name
    my_thing = client.create_thing(name)

    # 2-Add tags for searching
    add_tags(my_thing)

    # 3-Add metada to the thing
    with my_thing.get_meta() as meta_thing:
        add_metadata_information(meta_thing)

    # 4-Makes the thing visible
    my_thing.set_public()

    return my_thing


# Setups the feed for share information with others
def setup_thing_feed(my_thing):

    # 1-Get feed from thing
    my_feed = my_thing.create_feed('message_data')

    # 2-Put metadata information
    with my_feed.get_meta() as meta_feed:
        meta_feed.set_label('Message data')
        meta_feed.set_description('data sended in the messages')

    # 3-Create skeleton structure
    my_feed.create_value('user', Datatypes.STRING, lang='en', description="Name of the user")
    my_feed.create_value('message', Datatypes.STRING, lang='en', description="Message sent by the user")

    return my_feed


# Attachs a callback function to each feed
def connect_subscriptions(client, my_thing, callback_function):

    # Get tags to search other thing with same tags
    my_thing_tags = my_thing.list_tag()
    string_tags = ' '.join(my_thing_tags['en'])

    iotic_chat_things = client.search_reduced(text=string_tags)

    # Delete our thing from the search result if exists
    if my_thing.guid in iotic_chat_things:
        del iotic_chat_things[my_thing.guid]

    print("Connecting subscriptions")
    sys.stdout.flush()
    # Get global Point ID (gpid) from this information and wire up the follow to the callback
    for key in iotic_chat_things:
        for feed_guid, feed_type in iotic_chat_things[key].items():
            if feed_type == 'Feed':
                my_thing.follow(feed_guid, None, callback_parsed=callback_function)


# This callback is going to be called everytime we recieve data
def follow_feed_callback(data):

    values = data['parsed'].values
    text = '>' + values.user + ': ' + values.message
    print(text)


# Sends feed data
def share_data(my_feed, my_feed_skeleton):

    my_feed.share(my_feed_skeleton)


# Send disconected message
def share_goodbye_data(my_feed, my_feed_skeleton):

    my_feed_skeleton.values.message = my_feed_skeleton.values.user + ' left the the chat'
    my_feed_skeleton.values.user = ''

    my_feed.share(my_feed_skeleton)


# This fuction is called when someone is subscribed to your thing
def incoming_subscription_callback(data, client=None):

    print('New user is subscribed')
    # Your thing with new subscriptor
    subscribed_thing = client.create_thing(data['entityLid'])

    # Your feed's thing
    thing_feed = subscribed_thing.create_feed(data['lid'])

    # Gets all the followers even the new one
    feed_followers = thing_feed.list_followers()

    for key in feed_followers:
        # Get external things subscribed to you
        external_thing = client.describe(feed_followers[key])

        # Get the points from external thing
        external_thing_points = external_thing['meta']['points']
        for point in external_thing_points:

            if point['type'] == 'Feed':
                # Attach callback to see new messages
                subscribed_thing.follow(point['guid'], None, callback_parsed=follow_feed_callback)


# MAIN ------------------------------------------------------------------------------------------------------


def main():

    # Get the main arguments ( Agent and Thing )
    agent_file = sys.argv[1]
    thing_local_name = sys.argv[2]

    print("Connecting to your agent", sep=' ', end=' ... ')
    sys.stdout.flush()

    with IOT.Client(config=agent_file) as client:
        my_thing = setup_thing(client, thing_local_name)
        my_feed = setup_thing_feed(my_thing)
        my_feed_skeleton = my_feed.get_template()
        connect_subscriptions(client, my_thing, follow_feed_callback)

        # Create a new function which recieves a iotic-client
        manage_new_subsciptions = partial(incoming_subscription_callback, client=client)
        client.register_callback_subscription(manage_new_subsciptions)

        print("///////////////////////////////")
        print("// Welcome to the Iotic Chat //")
        print("///////////////////////////////")
        print("Write /quit to exit")

        user = input('Type your nickname: ')

        my_feed_skeleton.values.user = user

        while True:
            try:
                text = input()
                my_feed_skeleton.values.message = text
                print()

                if text != '/quit':
                    share_data(my_feed, my_feed_skeleton)
                else:

                    share_goodbye_data(my_feed, my_feed_skeleton)
                    break

            except KeyboardInterrupt:

                share_goodbye_data(my_feed, my_feed_skeleton)
                break


# # RUN --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# # END --------------------------------------------------------------------------------------------------
