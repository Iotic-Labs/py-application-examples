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

# Example: Thing Tags

from __future__ import unicode_literals

from IoticAgent import IOT


def get_default_language():
    print("Get Default Language Example")

    with IOT.Client('examples.ini') as client:
        print("Default language:", client.default_lang)


def create_point_tag():  # TODO: should the output be shown?
    print("Create Thing Tags Example")
    # If language (lang) is not set, it will add the tags using the default
    # Requires a list of strings without spaces
    feed_tags = ['tagF1', 'tagF2']
    control_tags = ['tagC1', 'tagC2']

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_point_with_tags')

        # create a Feed and Control
        my_feed = my_thing.create_feed('feed_with_tags')
        my_control = my_thing.create_control('control_with_tags', ctrl_callback)

        # create tags - same process for both types of Point
        my_feed.create_tag(feed_tags)
        my_control.create_tag(control_tags)


def create_point_tag_lang():
    print("Create Thing Tags with Language Example")
    fr_tags = ['un', 'deux']

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_point_with_fr_tags')

        # create a Feed (also works for Control)
        my_feed = my_thing.create_feed('french_feed')

        # create tags
        my_feed.create_tag(fr_tags, lang='fr')


def delete_point_tag():
    print("Delete Thing Tags Example")
    # If language (lang) is not set, it will add the tags using the default
    # Requires a list of strings without spaces
    del_tags = ['tag_to_delete', 'tag_2_delete']

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_point_delete_tags')

        # create a Feed and Control
        my_feed = my_thing.create_feed('feed_with_tags')
        my_control = my_thing.create_control('control_with_tags', ctrl_callback)

        # create tags - same process for both types of Point
        my_feed.create_tag(del_tags)
        my_control.create_tag(del_tags)

        # how to delete one tag from each
        my_feed.delete_tag(['tag_to_delete'])
        my_control.delete_tag(['tag_2_delete'])


def delete_point_tag_lang():
    print("Delete Thing Tags with Language Example")
    fr_del_tag = ['aurevoir']

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_point_delete_fr_tags')

        # create a Feed (also works for Control)
        my_feed = my_thing.create_feed('french_feed')

        # create tag allocated to lang 'fr'
        my_feed.create_tag(fr_del_tag, lang='fr')

        # delete tag associated with lang 'fr'
        my_feed.delete_tag(fr_del_tag, lang='fr')


def list_point_tags():
    print("List Thing Tags Example")
    tag_list = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5']
    fr_tag_list = ['un', 'deux', 'tois', 'quatre']

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_point_tag_list')

        # create a Feed (also works for Control)
        my_feed = my_thing.create_feed('feed_with_tags')

        # create some tags for it
        my_feed.create_tag(tag_list)
        my_feed.create_tag(fr_tag_list, lang='fr')

        # list those tags
        print("List of Tags for this Point:")
        tag_list = my_feed.list_tag()  # TODO: error??
        print(tag_list)

        # list with a limit
        print("List of Tags with a limit of 2 and offset of 2:")
        tag_list2 = my_feed.list_tag(limit=2, offset=2)
        print(tag_list2)


def ctrl_callback(data):
    print("Callback receiving data:", data)


def delete_all():
    created_things = ['thing_point_with_tags',
                      'thing_point_with_fr_tags',
                      'thing_point_delete_tags',
                      'thing_point_delete_fr_tags',
                      'thing_point_tag_list', ]

    with IOT.Client('examples.ini') as client:
        for thing in created_things:
            try:
                client.delete_thing(thing)
                print("Thing '%s' deleted" % thing)
            except:
                print("Thing '%s' does not exist" % thing)
                continue


def main():
    print("Point Tags Examples\n-----------------------")
    create_point_tag()
    create_point_tag_lang()
    delete_point_tag()
    delete_point_tag_lang()
    list_point_tags()
    delete_all()  # clear up what we have made; comment this line out if want to keep changes

main()
