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

# Example: Client

from __future__ import unicode_literals

from IoticAgent import IOT


def start_client_implicit_basic():
    print("Implicit Basic Example")
    # Calling start() implicitly using 'with'
    # minimal example with no exception handling

    with IOT.Client("examples.ini") as client:
        # do something
        print("Connected? ...", client.is_connected())


def start_client_implicit_full():
    print("Implicit Full Example")
    # Calling start() implicitly using 'with'
    # full exception handling

    try:
        with IOT.Client("examples.ini") as client:
            try:
                # do something
                print("Connected? ...", client.is_connected())
            except IOTException as exc:
                # handle exception
                print("An exception occured when using the client")
    except Exception as exc:  # not possible to connect
        print(exc)
        import sys
        sys.exit(1)


def start_client_explicit():
    print("Explicit Full Example")
    # Calling start() explicitly (no with)
    # full exception handling
    # Note: a finally in your try block ensures client won't remain connected

    try:
        client = IOT.Client("examples.ini")
        client.start()
    except Exception as exc:
        print(exc)
        import sys
        sys.exit(1)

    try:
        print("Connected? ...", client.is_connected())
    except IOTException as exc:
        # handle individual exception
        print("An exception occured when using the client")
    finally:
        client.stop()


def main():
    # run the examples
    print("Start Client Examples\n-----------------------")
    start_client_implicit_basic()
    start_client_implicit_full()
    start_client_explicit()

main()
