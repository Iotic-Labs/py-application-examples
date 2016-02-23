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


def create_thing_tag():
    print("Create Thing Tags Example")
    tags = ['tag1', 'tag2', 'tag3', 'tag4']
    # If language (lang) is not set, it will add the tags using the default
    # Requires a list of strings without spaces

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_with_tags')

        # create tags (returns nothing)
        my_thing.create_tag(tags)


def create_thing_tag_lang():
    print("Create Thing Tags with Language Example")
    fr_tags = ['un', 'deux']

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_with_fr_tags')

        # create tags (returns nothing)
        my_thing.create_tag(fr_tags, lang='fr')


def list_thing_tags():
    print("List Thing Tags Example")
    tags = ['tag1', 'tag2', 'tag3', 'tag4']

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_tag_list')

        # create tags (returns nothing)
        my_thing.create_tag(tags)

        # list those tags
        print("List of Tags for this Thing:")
        tag_list = my_thing.list_tag()
        print(tag_list)


def list_thing_tags_with_options():
    print("List Thing Tags with Limit/Offset Options Example")
    tag_list = ['tag1', 'tag2', 'tag3', 'tag4', 'tag5']
    fr_tag_list = ['un', 'deux', 'tois', 'quatre']

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_tag_list_options')

        # create some tags for it
        my_thing.create_tag(tag_list)
        my_thing.create_tag(fr_tag_list, lang='fr')

        # list with a limit and offset - returns last the 2 tags in this list of 5
        print("List of Tags with a limit of 2 and offset of 3:")
        tag_list2 = my_thing.list_tag(limit=2, offset=3)
        print(tag_list2)


def delete_thing_tag():
    print("Delete Thing Tags Example")
    del_tags = ['tag_to_delete', 'tag_2_delete']
    # If language (lang) is not set, it will add the tags using the default
    # Requires a list of strings without spaces

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_delete_tags')

        # create tags
        my_thing.create_tag(del_tags)

        # list those tags
        print("List of Tags for this Thing:")
        tag_list = my_thing.list_tag()
        print(tag_list)

        # delete tags
        my_thing.delete_tag(del_tags)

        # list tags again
        print("List of Tags for this Thing after Deletion:")
        tag_list_del = my_thing.list_tag()
        print(tag_list_del)


def delete_thing_tag_lang():
    print("Delete Thing Tags with Language Example")
    fr_del_tag = ['aurevoir']

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('thing_delete_fr_tags')

        # create tag allocated to lang 'fr'
        my_thing.create_tag(fr_del_tag, lang='fr')

        # delete tag associated with lang 'fr'
        my_thing.delete_tag(fr_del_tag, lang='fr')


def delete_all():
    created_things = ['thing_with_tags',
                      'thing_with_fr_tags',
                      'thing_delete_tags',
                      'thing_delete_fr_tags',
                      'thing_tag_list',
                      'thing_tag_list_options', ]

    with IOT.Client('examples.ini') as client:
        for thing in created_things:
            try:
                client.delete_thing(thing)
                print("Thing '%s' deleted" % thing)
            except:
                print("Thing '%s' does not exist" % thing)
                continue


def main():
    print("Thing Tags Examples\n-----------------------")
    create_thing_tag()
    create_thing_tag_lang()
    list_thing_tags()
    list_thing_tags_with_options()
    delete_thing_tag()
    delete_thing_tag_lang()
    delete_all()  # clear up what we have made; comment this line out if want to keep changes

main()
