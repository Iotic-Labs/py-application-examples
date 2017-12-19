# -*- coding: utf-8 -*-
# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.

from __future__ import unicode_literals, print_function

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] {%(threadName)s} %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from random import randint

from IoticAgent.Core.compat import monotonic
from IoticAgent.ThingRunner import RetryingThingRunner
from IoticAgent import Datatypes, Units


class DemoException(ValueError):
    pass


class ShareBasicError(RetryingThingRunner):
    LOOP_TIMER = 10  # minimum number of seconds duration of the main loop

    def __init__(self, config=None):
        """Instantiation code in here, after the call to super().__init__()
        """
        super(ShareBasicError, self).__init__(config=config)
        self.__thing = None
        self.__feed = None

    def on_exception(self, ctx, exc_info):  # pylint: disable=no-self-use
        """Called if there are any handleable exceptions raised by the superclass.
        Return True if you want the activity (ctx) that caused the exception in the first place to be retried
        """
        if not super(ShareBasicError, self).on_exception(ctx, exc_info):
            # Not handled by superclass - probably one of yours
            logger.debug("Another exception occurred during %s, %s", ctx, exc_info[1])
            if issubclass(exc_info[0], DemoException):
                logger.debug("DemoException happened, ok to carry on")
                return True
            else:
                return False

    def on_startup(self):
        """Called once at the beginning, before main().
        Use this method to create your things, rebind connections, setup hardware, etc.
        """
        print("Started. Press CTRL+C to end")

        self.__thing = self.client.create_thing('share_basic')
        with self.__thing.get_meta() as meta:
            meta.set_label('share basic label')
            meta.set_description('share basic description')
            meta.set_location(52.2053, 0.1218)  # Cambridge as an example

        self.__thing.create_tag(['test', 'example'])

        self.__feed = self.__thing.create_feed('share_basic_feed', save_recent=-1)
        with self.__feed.get_meta() as meta:
            meta.set_label('share basic feed label')

        self.__feed.create_value('count', Datatypes.INTEGER, description="Random Counter", unit=Units.COUNTS_PER_MIN)

        # push the metadata you've just set to the public registry.  I.e. make this thing searchable
        self.__thing.set_public(public=True)

    def main(self):
        """Called after on_startup.
        Use this method for your main loop (we need one here).
        Set self.LOOP_TIMER for your regular tick
        """
        # feed template is the safe way to set up your share. It will reflect the value(s) created in on_startup
        templ_feed = self.__feed.get_template()

        count = 0
        while True:
            start = monotonic()
            # loop code in here
            templ_feed.values.count = randint(50, 100)
            self.__feed.share(templ_feed)

            # deliberately raise an exception so we can see on_exception working
            count += 1
            if count % 4 == 0:
                raise DemoException("Deliberate error")

            stop = monotonic()
            if self.wait_for_shutdown(max(0, self.LOOP_TIMER - (stop - start))):
                break


def main():
    ShareBasicError(config="agent1.ini").run()

if __name__ == '__main__':
    main()
