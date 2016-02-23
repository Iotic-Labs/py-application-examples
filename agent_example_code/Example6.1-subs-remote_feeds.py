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

# Example: Subscriptions - Remote Feeds

from __future__ import unicode_literals

from IoticAgent import IOT


def follow_remote_feed():
    print("Follow Remote Feed Example")
    # Follow someone else's Feed with a callback to do something with the returned results
    # Note: Calling 'follow' will return the subscription object regardless of if it already existed
    example_remote_feed_gpid = '54e835716fddf8722e41ce7cd452bba6'

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('follow_example_remote_feed')

        # follow Feed
        remote_feed = my_thing.follow(example_remote_feed_gpid, follow_feed_callback)
        print("Remote Feed subscription object:", remote_feed)


def unfollow_remote_feed():
    print("Unfollow Remote Feed (Unsubscribe) Example")
    # This example follows a Feed in standard way
    example_remote_feed_gpid = '54e835716fddf8722e41ce7cd452bba6'

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('unfollow_remote_feed')

        # follow Feed
        remote_feed = my_thing.follow(example_remote_feed_gpid, follow_feed_callback)
        print("Remote Feed object:", remote_feed)

        # unfollow using remote feed subscription id
        print("Unfollowing feed with subid:", remote_feed.subid)
        my_thing.unfollow(remote_feed.subid)


def list_connections():
    print("List All Subscription Connections Example")
    remote_feed_gpid = '54e835716fddf8722e41ce7cd452bba6'

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('list_connections_feed_thing')

        # create Feed subscription
        my_thing.follow(remote_feed_gpid, follow_feed_callback)

        # list subscriptions (limit, offset) available
        sub_list = my_thing.list_connections()
        print("Subscription list: ", sub_list)


def list_followers():
    print("List Followers of Feed Example")
    # list followers of a Feed

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('list_followers_thing')

        # create a Feed
        my_feed = my_thing.create_feed('followers_feed')

        # list the followers (none in this example)
        followers = my_feed.list_followers()
        print("List of followers:", followers)


def simulate_feed_data():
    print("Simulate Remote Feed Data Example")
    remote_feed_gpid = '54e835716fddf8722e41ce7cd452bba6'
    data = {'random_int': 452351, 'random_string': 'a random string'}

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('simulate_feed_data_thing')

        # create Feed subscription
        subscription = my_thing.follow(remote_feed_gpid, follow_feed_callback)

        # simulate some Feed data
        subscription.simulate(data)


def get_last_feed_data():
    print("Get Last Remote Feed Data Example")
    # Note: for this example the user will get an exception error message if they
    # have not simulated data and/or have never received any data from Feed
    remote_feed_gpid = '54e835716fddf8722e41ce7cd452bba6'
    data = {'random_int': 452351, 'random_string': 'a random string'}

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('last_feed_data_thing')

        # create Feed subscription
        subscription = my_thing.follow(remote_feed_gpid, follow_feed_callback)

        # simulate some Feed data
        subscription.simulate(data)

        # get last data
        try:
            last_data = subscription.get_last()
            print("Last data from Remote Feed:", last_data)
        except KeyError:
            print("There is no data to get")
        except RuntimeError:
            print("The key-value database is disabled")


def follow_feed_callback(data):
    print("This is the Feed Callback with data:", data)


def delete_all():
    created_things = ['follow_example_remote_feed',
                      'unfollow_remote_feed',
                      'list_connections_feed_thing',
                      'list_followers_thing',
                      'simulate_feed_data_thing',
                      'last_feed_data_thing', ]

    with IOT.Client('examples.ini') as client:
        for thing in created_things:
            try:
                client.delete_thing(thing)
                print("Thing '%s' deleted" % thing)
            except:
                print("Thing '%s' does not exist" % thing)
                continue


def main():
    print("Subscription Remote Feed Examples\n-----------------------")
    try:
        follow_remote_feed()
        unfollow_remote_feed()
        list_connections()
        list_followers()
        simulate_feed_data()
        get_last_feed_data()
        delete_all()  # clear up what we have made; comment this line out if want to keep changes
    except:
        delete_all()

main()
