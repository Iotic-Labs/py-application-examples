# -*- coding: utf-8 -*-
# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.

from __future__ import unicode_literals, print_function

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] {%(threadName)s} %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from time import sleep

from IoticAgent.Core.compat import monotonic
from IoticAgent.ThingRunner import RetryingThingRunner


class TemplateTR(RetryingThingRunner):
    LOOP_TIMER = 10  # minimum number of seconds duration of the main loop

    def __init__(self, config=None):
        """Instantiation code in here, after the call to super().__init__()
        """
        super(TemplateTR, self).__init__(config=config)

    def on_startup(self):
        """Called once at the beginning, before main().
        Use this method to create your things, rebind connections, setup hardware, etc.
        """
        pass

    def main(self):
        """Called after on_startup.
        Use this method for your main loop (if you need one).
        Set LOOP_TIMER for your regular tick
        """
        while True:
            start = monotonic()
            # loop code in here
            stop = monotonic()
            if self.wait_for_shutdown(max(0, self.LOOP_TIMER - (stop - start))):
                break


def main():
    runner = TemplateTR(config="your_config.ini")
    runner.run(background=True)

    try:
        while True:
            print("Press ctrl+C to end")
            # Runner-unrelated action goes here
            sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        runner.stop()

    logger.info('Ended')


if __name__ == '__main__':
    main()
