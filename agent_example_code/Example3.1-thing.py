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

# Example: Things

from __future__ import unicode_literals

from IoticAgent import IOT


def create_thing():
    print("Create Thing Example")

    with IOT.Client('examples.ini') as client:
        my_thing = client.create_thing('example_created_thing')
        print("My Thing object:", my_thing)
        print("My Thing local ID (lid):", my_thing.lid)
        print("My Thing globally unique ID (guid):", my_thing.guid)


def rename_thing():
    print("Rename Thing Example")

    with IOT.Client('examples.ini') as client:
        # create Thing to rename
        my_thing = client.create_thing('to_be_renamed')
        print("Local id for my thing:", my_thing.lid)
        # rename Thing
        my_thing.rename('example_renamed_thing')
        print("New lid for my thing:", my_thing.lid)


def reassign_thing():
    print("Reassign Thing Example")
    # Note: when a Thing is reassigned, it can no longer be deleted whilst using this agent
    new_agent_id = 'f63044a51a94fe74415f81494721b0ed'

    with IOT.Client('examples.ini') as client:
        # create Thing to reassign
        my_thing = client.create_thing('example_reassigned')

        # using try/except in case of error with new agent id
        try:
            my_thing.reassign(new_agent_id)
        except IOTException as exc:
            # handle individual exception
            print(exc)


def set_thing_public():
    print("Set Thing Public Example")
    # This allows your Thing to become searchable

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('example_public_thing')

        # set to public
        my_thing.set_public()

        # set to private
        my_thing.set_public(False)


def delete_thing():
    print("Delete Thing Example")

    with IOT.Client('examples.ini') as client:
        # create Thing to delete
        client.create_thing('example_delete_thing')

        # delete Thing
        client.delete_thing('example_delete_thing')


def list_my_agent_things():
    print("List [My] Things Example")
    # Lists have a default limit of 500 and offset of 0

    with IOT.Client('examples.ini') as client:
        print("List of Things in this agent:")
        my_list = client.list()
        print(my_list)

        # limit parameter
        print("List limited to 3 Things:")
        limited_list = client.list(limit=3)
        print(limited_list)

        # offset parameter
        print("List offset by 2 Things:")
        offset_list = client.list(offset=2)
        print(offset_list)


def list_all_my_things():
    print("List All [My] Things Example")

    with IOT.Client('examples.ini') as client:
        print("List of Things across all agents owned:")
        full_list = client.list(all_my_agents=True)
        print(full_list)


def delete_all():
    created_things = ['example_created_thing',
                      'example_renamed_thing',
                      'example_public_thing', ]

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
    print("Things Examples\n-----------------------")
    try:
        create_thing()
        rename_thing()
        reassign_thing()
        set_thing_public()
        delete_thing()
        list_my_agent_things()
        list_all_my_things()
        delete_all()  # clear up what we have made; comment this line out if want to keep changes
    except:
        delete_all()

main()
