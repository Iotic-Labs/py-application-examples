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

# Example: Search

from __future__ import unicode_literals

from IoticAgent import IOT


def search_basic():
    print("Basic Search Example")
    # text field is always required

    with IOT.Client('examples.ini') as client:
        search_results = client.search('river', limit=10)
        print("Search Results:")
        print(search_results)


def search_reduced_basic():
    print("Basic Reduced Search Example")
    # a reduced Search just returns results containing Points and their types

    with IOT.Client('examples.ini') as client:
        search_results = client.search_reduced('river', lang='en', limit=10)
        print("Search Results:")
        print(search_results)


def search_full():
    print("Full Search Example")
    # text field is always required
    # location radius is in kilometres
    loc = {'lat': 1.2, 'long': 54.3, 'radius': 20}

    with IOT.Client('examples.ini') as client:
        search_results = client.search('river', lang='en', location=loc, unit=None, limit=5, offset=0)
        print("Search Results:")
        print(search_results)


def main():
    print("Search Examples\n-----------------------")
    search_basic()
    search_reduced_basic()
    search_full()

main()
