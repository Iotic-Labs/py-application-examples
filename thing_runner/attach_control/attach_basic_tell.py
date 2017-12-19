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


class AttachBasic(RetryingThingRunner):
    LOOP_TIMER = 10  # minimum number of seconds duration of the main loop

    def __init__(self, config=None):
        """Instantiation code in here, after the call to super().__init__()
        """
        super(AttachBasic, self).__init__(config=config)
        self.__thing = None
        self.__remote_control = None

    def on_startup(self):
        """Called once at the beginning, before main().
        Use this method to create your things, rebind connections, setup hardware, etc.
        """
        print("Started. Press CTRL+C to end")
        self.__thing = self.client.create_thing('attach_basic')
        self.__remote_control = self.__thing.attach(('offer_basic', 'offer_basic_control'))

    def main(self):
        """Called after on_startup.
        Use this method for your main loop (we need one here).
        Set self.LOOP_TIMER for your regular tick
        """
        # use the template metadata for safe creation of control request
        templ_control = self.__remote_control.get_template()

        while True:
            start = monotonic()
            # loop code in here
            templ_control.values.temp = randint(50, 100)
            # tell() requires the far end to confirm that they've done the action.
            # tell_result will be True for success or contain a string reason for failure, e.g. timeout
            tell_result = self.__remote_control.tell(templ_control)
            if tell_result is not True:
                logger.warning("Tell failed - reason: %s", tell_result)
            stop = monotonic()
            if self.wait_for_shutdown(max(0, self.LOOP_TIMER - (stop - start))):
                break


def main():
    AttachBasic(config="agent2.ini").run()

if __name__ == '__main__':
    main()
