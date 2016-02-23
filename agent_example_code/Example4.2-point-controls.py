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

# Example: Controls

from __future__ import unicode_literals

from IoticAgent import IOT


def create_control():
    print("Create Control Example")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_to_create_control')

        # create a Control
        my_control = my_thing.create_control('my_new_control', ctrl_callback)
        print("My Control object:", my_control)
        print("My Control local ID (pid):", my_control.pid)
        print("My Thing local ID that advertises this Control (lid):", my_control.lid)
        print("My Thing's globally unique ID (gpid):", my_control.guid)
        print("Check this is a feed or control:", my_control.foc)


def rename_control():
    print("Rename Control Example")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_to_rename_control')

        # create Control to rename
        my_control = my_thing.create_control('to_be_renamed', ctrl_callback)
        print("Point id for my control:", my_control.pid)

        # rename Control
        my_control.rename('example_renamed_control')
        print("New pid for my thing:", my_control.pid)


def delete_control():
    print("Delete Control Example")

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('example_delete_control')

        # create Control to delete
        my_thing.create_control('delete_control', ctrl_callback)

        # delete Control
        my_thing.delete_control('delete_control')


def list_controls():
    print("List Controls for [My] Thing Example")
    # Lists have a default limit of 500 and offset of 0

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('list_control_thing')

        # create a couple of Controls
        my_thing.create_control('first_control', ctrl_callback)
        my_thing.create_control('second_control', ctrl_callback)

        # list all the Controls
        print("List of Things in this agent:")
        list_all_controls = my_thing.list_controls()
        print(list_all_controls)

        # list the details of one particular Control
        print("Detailed list for one Control:")
        control_list = my_thing.list_controls('first_control')
        print(control_list)


def ctrl_callback(data):
    print("Callback receiving data:", data)


def delete_all():
    created_things = ['thing_to_create_control',
                      'thing_to_rename_control',
                      'example_delete_control',
                      'list_control_thing', ]

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
    print("Controls Examples\n-----------------------")
    create_control()
    rename_control()
    delete_control()
    list_controls()
    delete_all()  # clear up what we have made; comment this line out if want to keep changes

main()
