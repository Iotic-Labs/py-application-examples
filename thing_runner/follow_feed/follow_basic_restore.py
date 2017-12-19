# -*- coding: utf-8 -*-
# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.

from __future__ import unicode_literals, print_function

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] {%(threadName)s} %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from IoticAgent.Core.compat import monotonic
from IoticAgent.Core.Const import R_FEED
from IoticAgent.ThingRunner import RetryingThingRunner
from IoticAgent import Datatypes, Units


class FollowBasicRestore(RetryingThingRunner):
    LOOP_TIMER = 10  # minimum number of seconds duration of the main loop

    def __init__(self, config=None):
        """Instantiation code in here, after the call to super().__init__()
        """
        super(FollowBasicRestore, self).__init__(config=config)
        self.__thing = None

    @staticmethod
    def __callback_parsed(args):
        logger.debug("Feed data received. Shared at %s", args['time'])

        values = args['parsed'].filter_by(types=(Datatypes.INTEGER,), units=(Units.COUNTS_PER_MIN,), text=("random",))
        if values:
            logger.debug('Found parsed data for key %s: value: %s', values[0].label, values[0].value)
        else:
            logger.debug('Parsed data not found')

    def __restore(self, sub_dict):
        # sub_dict is a dict of *subscription* guids.
        # We need to follow the feed or control guid which is 'id' in their dictionary
        for sub_guid in sub_dict:
            if sub_dict[sub_guid]['type'] == R_FEED:
                feed_guid = sub_dict[sub_guid]['id']
                logger.debug('re-connecting to feed %s', feed_guid)
                self.__thing.follow(feed_guid, callback_parsed=self.__callback_parsed)

    def on_startup(self):
        """Called once at the beginning, before main().
        Use this method to create your things, rebind connections, setup hardware, etc.
        """
        print("Started. Press CTRL+C to end")

        self.__thing = self.client.create_thing('follow_basic')

        # get a list of your subscriptions from the infrastructure and re-follow
        self.__restore(self.__thing.list_connections())

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
    FollowBasicRestore(config="agent2.ini").run()

if __name__ == '__main__':
    main()
