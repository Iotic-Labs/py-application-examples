# -*- coding: utf-8 -*-
# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.

from __future__ import unicode_literals, print_function

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] {%(threadName)s} %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from IoticAgent.Core.compat import monotonic
from IoticAgent.ThingRunner import RetryingThingRunner
from IoticAgent import Datatypes, Units
from IoticAgent.IOT.Exceptions import IOTUnknown
from IoticAgent.Core.Const import SearchScope
from rdflib.namespace import Namespace, RDF

KEY_FEED = "Feed"

'''These are semantic examples. Choose your own ontologies. In this example,
we imagine this definition of the iotics:category property in the
/examples/ ontology...
iotics:category
    rdf:type rdf:Property ;
    rdfs:range iotics:category ;
    .

...and in the /example/categories, this definition of iotics_categories:Example
as a skos:Concept.
iotics_categories:Example
    rdf:type skos:Concept .
'''
IOTICS_NS = "http://iotics.com/example/"
IOTICS = Namespace(IOTICS_NS)

IOTICS_CATEGORIES_NS = "http://iotics.com/example/categories#"
IOTICS_CATEGORIES = Namespace(IOTICS_CATEGORIES_NS)


class FollowSearchLocalProperty(RetryingThingRunner):
    LOOP_TIMER = 10  # minimum number of seconds duration of the main loop

    def __init__(self, config=None):
        """Instantiation code in here, after the call to super().__init__()
        """
        super(FollowSearchLocalProperty, self).__init__(config=config)
        self.__thing = None

    @staticmethod
    def __callback_parsed(args):
        logger.debug("Feed data received. Shared at %s", args['time'])

        values = args['parsed'].filter_by(types=(Datatypes.INTEGER,), units=(Units.COUNTS_PER_MIN,), text=("random",))
        if values:
            logger.debug('Found parsed data for key %s: value: %s', values[0].label, values[0].value)
        else:
            logger.debug('Parsed data not found')

    def __find_and_bind(self, predicate, point_type):
        """Search the local registry for the predicate(s) you want - restricted to just stuff you own
        """
        # SearchScope sets the range of search LOCAL_OWN is your things in the local space only
        thing_list = self.client.search_property(predicate, scope=SearchScope.LOCAL_OWN)
        for thing_guid in thing_list:
            point_list = thing_list[thing_guid]['points']
            for point_guid in point_list:
                if point_list[point_guid]['type'] == point_type:
                    try:
                        self.__thing.follow(point_guid, callback_parsed=self.__callback_parsed)
                    except IOTUnknown:  # might have been deleted in between search results and follow
                        logger.warning("failed to follow thing: %s, feed %s", thing_guid, point_guid)
                    break  # subscribe to the first one only then stop

    def on_startup(self):
        """Called once at the beginning, before main().
        Use this method to create your things, rebind connections, setup hardware, etc.
        """
        print("Started. Press CTRL+C to end")

        self.__thing = self.client.create_thing('follow_search_local')
        self.__find_and_bind((IOTICS.category, IOTICS_CATEGORIES.Example), KEY_FEED)

    def main(self):
        """Called after on_startup.
        Use this method for your main loop (we don't need one here).
        Set self.LOOP_TIMER for your regular tick
        """
        while True:
            start = monotonic()
            # loop code in here
            stop = monotonic()
            if self.wait_for_shutdown(max(0, self.LOOP_TIMER - (stop - start))):
                break


def main():
    FollowSearchLocalProperty(config="agent2.ini").run()

if __name__ == '__main__':
    main()
