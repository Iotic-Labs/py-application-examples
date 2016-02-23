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

# Example: Describe

from __future__ import unicode_literals

from IoticAgent import IOT


def describe_thing():
    print("Describe a Thing Example")

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('describe_thing')

        print("Thing description by object:")
        my_thing_description = client.describe(my_thing)
        print(my_thing_description)

        print("Thing description by guid:")
        my_thing_desc2 = client.describe(my_thing.guid)
        print(my_thing_desc2)


def describe_point():
    print("Describe a Point (Feed/Control) Example")
    # Note: the two methods shown here are interchangeable (using object or subid)

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('describe_point_thing')

        # create Feed & Control Points
        my_feed = my_thing.create_feed('describe_feed')
        my_control = my_thing.create_control('describe_control', ctrl_callback)

        print("Feed description by object:")
        my_feed_description = client.describe(my_feed)
        print(my_feed_description)

        print("Control description by guid:")
        my_control_description = client.describe(my_control.guid)
        print(my_control_description)


def describe_remote_point():
    print("Describe a Remote Point Example")
    # Note: the two methods shown here are interchangeable (using object or subid)
    remote_feed_gpid = '54e835716fddf8722e41ce7cd452bba6'
    remote_control_gpid = 'a9baf4e57fdf6c0e6e3e31860d9cbd75'

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('describe_remote_point_thing')

        # create Feed subscription
        remote_feed = my_thing.follow(remote_feed_gpid)

        print("Remote Feed description (object):")
        remote_feed_description = client.describe(remote_feed)
        print(remote_feed_description)

        # create Control subscription
        remote_control = my_thing.attach(remote_control_gpid)

        print("Remote Control description (subscription id):")
        remote_control_description = client.describe(remote_control.subid)
        print(remote_control_description)


def ctrl_callback(data):
    print("Control Point callback with data:", data)


def delete_all():
    created_things = ['describe_thing',
                      'describe_point_thing',
                      'describe_remote_point_thing', ]

    with IOT.Client('examples.ini') as client:
        for thing in created_things:
            try:
                client.delete_thing(thing)
                print("Thing '%s' deleted" % thing)
            except:
                print("Thing '%s' does not exist" % thing)
                continue


def main():
    print("Describe Instances Examples\n-----------------------")
    try:
        describe_thing()
        describe_point()
        describe_remote_point()
        delete_all()  # clear up what we have made; comment this line out if want to keep changes
    except:
        delete_all()

main()
