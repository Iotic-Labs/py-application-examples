# -*- coding: utf-8 -*-
# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.

from __future__ import unicode_literals, print_function

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] {%(threadName)s} %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from IoticAgent.Core.compat import monotonic
from IoticAgent.IOT.RemotePoint import RemoteFeed
from IoticAgent.ThingRunner import RetryingThingRunner
from IoticAgent import Datatypes, Units


class FollowBasicSubscription(RetryingThingRunner):
    LOOP_TIMER = 10  # minimum number of seconds duration of the main loop

    def __init__(self, config=None):
        """Instantiation code in here, after the call to super().__init__()
        """
        super(FollowBasicSubscription, self).__init__(config=config)
        self.__thing = None

    @staticmethod
    def __callback(args):
        logger.debug("Unparseable feed data received. Shared at %s", args['time'])

        # Used for any feed data that can't be parsed
        try:
            logger.debug('Found feed data for key %s: value: %s', 'count', args['data']['count'])
        except KeyError as exc:
            logger.warning('Failed to find key %s in recent data %s', exc, args)
            raise

    @staticmethod
    def __callback_parsed(args):
        logger.debug("Feed data received. Shared at %s", args['time'])

        values = args['parsed'].filter_by(types=(Datatypes.INTEGER,), units=(Units.COUNTS_PER_MIN,), text=("random",))
        if values:
            logger.debug('Found parsed data for key %s: value: %s', values[0].label, values[0].value)
        else:
            logger.debug('Parsed data not found')

    def __cb_subscribed(self, arg):
        if isinstance(arg, RemoteFeed):
            logger.info("Subscribed to a new remote Feed")
            rm_feed_info = self.client.describe(arg)
            logger.debug("Remote feed describe %s", rm_feed_info)
            if not rm_feed_info['meta']['values']:  # Not a public feed or feed has no values
                logger.info("Following Feed with no values")
                self.__thing.follow(arg.guid, callback=self.__callback)
            else:
                logger.info("Following Feed with known values")
                self.__thing.follow(arg.guid, callback_parsed=self.__callback_parsed)

    def on_startup(self):
        """Called once at the beginning, before main().
        Use this method to create your things, rebind connections, setup hardware, etc.
        """
        print("Started. Press CTRL+C to end")

        self.__thing = self.client.create_thing('follow_basic')

        # register a callback for any new subscriptions that have been made for you - perhaps in the UI
        self.client.register_callback_subscribed(self.__cb_subscribed)

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
    FollowBasicSubscription(config="agent2.ini").run()

if __name__ == '__main__':
    main()
