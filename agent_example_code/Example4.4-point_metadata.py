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

# Example: Point Metadata

from __future__ import unicode_literals

from IoticAgent import IOT


def get_point_metadata_implicit_set():
    print("Get Point's Metadata with Implicit Set Example")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('implicit_setPMD_thing')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # get the metadata
        # using 'with' calls set() implicitly so you don't have to
        with my_feed.get_meta() as my_metadata:
            print("My Point's metadata object:", my_metadata)

            # do something with the metadata here
            my_metadata.set_label('my_label')


def get_point_metadata_explicit_set():
    print("Get Point's Metadata with Explicit Set Example")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('explicit_setPMD_thing')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # get the metadata
        my_metadata = my_feed.get_meta()
        print("My Point's metadata object:", my_metadata)

        # do something with the metadata here
        my_metadata.set_label('my_label')

        # set the metadata
        my_metadata.set()


def get_point_metadata_rdf():
    print("Get Point's Metadata in RDF Example")
    # try other formats

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('point_metadata_rdf_thing')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # set some metadata for the example
        with my_feed.get_meta() as my_metadata:
            my_metadata.set_label('my_label')
            my_metadata.set_description('This is the description')

        print("Get metadata in XML:")
        xml_rdf = my_feed.get_meta_rdf(fmt='xml')
        print(xml_rdf)
        print("Get metadata in Turtle:")
        turtle_rdf = my_feed.get_meta_rdf(fmt='turtle')
        print(turtle_rdf)


def update_point_metadata():
    print("Update Point's Metadata")
    # this returns the metadata as stored online
    # any changes made locally without calling set() them will be overwritten

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('update_point_metadata')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # get the metadata
        my_metadata = my_feed.get_meta()

        # do something with the metadata here
        my_metadata.set_label('my_label')
        my_metadata.set()
        my_label = my_metadata.get_labels()
        print("My Thing's label set to '%s'" % my_label)

        my_metadata.set_label('new_label')
        new_label = my_metadata.get_labels()
        print("Changed label to '%s' without setting it" % new_label)

        # update the metadata
        my_metadata.update()
        current_label = my_metadata.get_labels()
        print("Updated metadata; label should have reverted back to previous set label '%s'" % current_label)


def create_point_meta_label():
    print("Create Point's Metadata Label")
    # Note: one label allowed per language

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('point_metadata_label')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # get the metadata
        with my_feed.get_meta() as my_metadata:
            # create a label
            my_metadata.set_label('my_label')  # uses default language

            # create a label in another language
            my_metadata.set_label('mon_label', 'fr')


def delete_point_meta_label():
    print("Delete Point's Metadata Label")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('point_metadata_label_delete')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # get the metadata
        with my_feed.get_meta() as my_metadata:
            # create a label
            my_metadata.set_label('my_label')  # uses default language

            # create a label in another language
            my_metadata.set_label('mon_label', 'fr')

        with my_feed.get_meta() as my_metadata:
            # delete the labels
            my_metadata.delete_label()
            my_metadata.delete_label(lang='fr')


def get_point_meta_labels():
    print("Get Point's Metadata Labels")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('point_metadata_get_labels')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # get the metadata
        with my_feed.get_meta() as my_metadata:
            # create a label
            print("Setting default language label")
            my_metadata.set_label('my_label')  # uses default language

            # create a label in another language
            print("Setting French language label")
            my_metadata.set_label('mon_label', 'fr')

        with my_feed.get_meta() as my_metadata:
            # get the labels
            my_labels = my_metadata.get_labels()
            print("Returned labels:")
            print(my_labels)


def create_point_meta_description():
    print("Create Points's Metadata Description")
    # Note: one description allowed per language

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('point_metadata_description')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # get the metadata
        with my_feed.get_meta() as my_metadata:
            # create a description
            my_metadata.set_description('This is a description.')  # uses default language

            # create a description in another language
            my_metadata.set_description('Ceci est une description.', 'fr')


def delete_point_meta_description():
    print("Delete Point's Metadata Description")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('point_metadata_description_delete')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # get the metadata
        with my_feed.get_meta() as my_metadata:
            # create a description
            my_metadata.set_description('This is a description.')  # uses default language

            # create a description in another language
            my_metadata.set_description('Ceci est une description.', 'fr')

        with my_feed.get_meta() as my_metadata:
            # delete the descriptions
            my_metadata.delete_description()
            my_metadata.delete_description(lang='fr')


def get_point_meta_descriptions():
    print("Get Point's Metadata Description")

    with IOT.Client('examples.ini') as client:
        # create a Thing
        my_thing = client.create_thing('point_metadata_get_descriptions')

        # create a Feed (same for Control)
        my_feed = my_thing.create_feed('metadata_feed')

        # get the metadata
        with my_feed.get_meta() as my_metadata:
            # create a description
            print("Setting default language decription")
            my_metadata.set_description('This is a description.')  # uses default language

            # create a description in another language
            print("Setting French language description")
            my_metadata.set_description('Ceci est une description.', 'fr')

        with my_feed.get_meta() as my_metadata:
            # get the descriptions
            my_descriptions = my_metadata.get_descriptions()
            print("Returned descriptions:")
            print(my_descriptions)


def delete_all():
    created_things = ['implicit_setPMD_thing',
                      'explicit_setPMD_thing',
                      'point_metadata_rdf_thing',
                      'update_point_metadata',
                      'point_metadata_label',
                      'point_metadata_label_delete',
                      'point_metadata_get_labels',
                      'point_metadata_description',
                      'point_metadata_description_delete',
                      'point_metadata_get_descriptions', ]

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
    print("Point Metadata Examples\n-----------------------")
    get_point_metadata_implicit_set()
    get_point_metadata_explicit_set()
    get_point_metadata_rdf()
    update_point_metadata()
    create_point_meta_label()
    delete_point_meta_label()
    get_point_meta_labels()
    create_point_meta_description()
    delete_point_meta_description()
    get_point_meta_descriptions()
    delete_all()  # clear up what we have made; comment this line out if want to keep changes

main()
