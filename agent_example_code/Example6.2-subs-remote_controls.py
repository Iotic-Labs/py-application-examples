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

# Example: Subscriptions - Remote Controls

from __future__ import unicode_literals

from IoticAgent import IOT


def attach_remote_control():
    print("Attach Remote Control Example")
    # Attach your Thing to someone else's Control Point with the intention of
    # sending an order (asking or telling) to it to do something
    # Note: Calling 'attach' will return the subscription object regardless of if it already existed
    example_remote_control_gpid = 'a9baf4e57fdf6c0e6e3e31860d9cbd75'

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('attach_example_remote_control')

        # attach to Control
        remote_control = my_thing.attach(example_remote_control_gpid)
        print("Remote Control subscription object:", remote_control)


def unattach_remote_control():
    print("Unattach Remote Control (Unsubscribe) Example")
    # This example attaches in standard way
    example_remote_control_gpid = 'a9baf4e57fdf6c0e6e3e31860d9cbd75'

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('unattach_remote_control')

        # attach to Control
        remote_control = my_thing.attach(example_remote_control_gpid)
        print("Remote Control object:", remote_control)

        # unfollow using remote feed subscription id
        print("Unattaching control with subid:", remote_control.subid)  # TODO
        my_thing.unattach(remote_control.subid)


def list_connections():
    print("List All Subscription Connections Example")
    # also options for limit and offset: list_connections(limit=500, offset=0)
    remote_control_gpid = 'a9baf4e57fdf6c0e6e3e31860d9cbd75'

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('list_connections_control_thing')

        # create Control subscription
        my_thing.attach(remote_control_gpid)

        # list subscriptions
        sub_list = my_thing.list_connections()
        print("Subscription list: ", sub_list)


def ask_control_action():
    print("Ask Remote Control to Act Example")
    # There is no notification of success when just 'asking'
    remote_control_gpid = 'a9baf4e57fdf6c0e6e3e31860d9cbd75'
    data = {'something_useful': 'useful value'}

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('ask_control_thing')

        # create Control subscription
        remote_control = my_thing.attach(remote_control_gpid)

        # ask to send data to the Control
        remote_control.ask(data)


def ask_control_action_mime():
    print("Ask Remote Control to Act with Mime Example")
    # mime is the type of data that you are sharing
    # 'idx/1' is the default ('application/ubjson')
    # 'idx/2' corresponds to 'text/plain' - recommended for sending byte sized data e.g. utf8 string
    # also 'text/xml' & other valid mime types etc.
    remote_control_gpid = 'a9baf4e57fdf6c0e6e3e31860d9cbd75'
    data = 'a string I want to share'

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('ask_mime_control_thing')

        # create Control subscription
        remote_control = my_thing.attach(remote_control_gpid)

        # ask to send data to the Control
        remote_control.ask(data.encode('utf8'), 'idx/2')


def tell_control_action():
    print("Tell Remote Control to Act Example")
    # timeout is the delay in seconds before the 'tell' request times out
    # mime and timeout are optional
    remote_control_gpid = 'a9baf4e57fdf6c0e6e3e31860d9cbd75'
    data = 'a string I want to share'

    with IOT.Client('examples.ini') as client:
        # create Thing
        my_thing = client.create_thing('tell_control_thing')

        # create Control subscription
        remote_control = my_thing.attach(remote_control_gpid)

        # ask to send data to the Control
        remote_control.tell(data.encode('utf8'), timeout=10, mime='idx/2')


def delete_all():
    created_things = ['attach_example_remote_control',
                      'unattach_remote_control',
                      'list_connections_control_thing',
                      'ask_control_thing',
                      'ask_mime_control_thing',
                      'tell_control_thing', ]

    with IOT.Client('examples.ini') as client:
        for thing in created_things:
            try:
                client.delete_thing(thing)
                print("Thing '%s' deleted" % thing)
            except:
                print("Thing '%s' does not exist" % thing)
                continue


def main():
    print("Subscription Remote Control Examples\n-----------------------")
    try:
        attach_remote_control()
        unattach_remote_control()
        list_connections()
        ask_control_action()
        ask_control_action_mime()
        tell_control_action()
        delete_all()  # clear up what we have made; comment this line out if want to keep changes
    except:
        delete_all()

main()
