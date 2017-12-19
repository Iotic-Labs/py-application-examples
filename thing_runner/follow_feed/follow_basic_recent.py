# -*- coding: utf-8 -*-
# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.

from __future__ import unicode_literals, print_function

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] {%(threadName)s} %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from IoticAgent.Core.compat import monotonic
from IoticAgent.ThingRunner import RetryingThingRunner
from IoticAgent import Datatypes, Units


class FollowBasicRecent(RetryingThingRunner):
    LOOP_TIMER = 10  # minimum number of seconds duration of the main loop

    def __init__(self, config=None):
        """Instantiation code in here, after the call to super().__init__()
        """
        super(FollowBasicRecent, self).__init__(config=config)
        self.__thing = None

    @staticmethod
    def __callback_parsed(args):
        logger.debug("Feed data received. Shared at %s", args['time'])

        values = args['parsed'].filter_by(types=(Datatypes.INTEGER,), units=(Units.COUNTS_PER_MIN,), text=("random",))
        if values:
            logger.debug('Found parsed data for key %s: value: %s', values[0].label, values[0].value)
        else:
            logger.debug('Parsed data not found')

    @staticmethod
    def __callback_recent(args):
        logger.debug("Recent data received. Shared at %s", args['time'])

        # at the moment, recent data isn't parsed to extract metadata for values so we have to use fixed keys
        try:
            logger.debug('Found recent data for key %s: value: %s', 'count', args['data']['count'])
        except KeyError as exc:
            logger.warning('Failed to find key %s in recent data %s', exc, args)
            raise

    def __fetch_recent(self, remote_point):
        # retrieve all samples, max 99 will likely be floored to container max
        samples = remote_point.get_recent(99)

        for sample in samples:
            self.__callback_recent(sample)

    def on_startup(self):
        """Called once at the beginning, before main().
        Use this method to create your things, rebind connections, setup hardware, etc.
        """
        print("Started. Press CTRL+C to end")

        self.__thing = self.client.create_thing('follow_basic')
        remote_feed = self.__thing.follow(('share_basic', 'share_basic_feed'),
                                          callback_parsed=self.__callback_parsed)

        self.__fetch_recent(remote_feed)

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
    FollowBasicRecent(config="agent2.ini").run()

if __name__ == '__main__':
    main()
