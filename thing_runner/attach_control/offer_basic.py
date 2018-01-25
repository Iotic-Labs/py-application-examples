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


class OfferBasic(RetryingThingRunner):
    LOOP_TIMER = 10  # minimum number of seconds duration of the main loop

    def __init__(self, config=None):
        """Instantiation code in here, after the call to super().__init__()
        """
        super(OfferBasic, self).__init__(config=config)
        self.__thing = None
        self.__control = None

    @staticmethod
    def __callback(args):  # pylint: disable=unused-argument
        pass

    def __callback_parsed(self, args):
        logger.debug("Control request received.")

        values = args['parsed'].filter_by(types=(Datatypes.DECIMAL,), units=(Units.CELSIUS,), text=("thermostat",))
        if values:
            logger.debug('Found parsed data for key %s: value: %s', values[0].label, values[0].value)
        else:
            logger.debug('Parsed data not found')

        if args['confirm']:  # we've been asked to confirm - return False for the sake of the `tell` example
            self.client.confirm_tell(args, False)

    def on_startup(self):
        """Called once at the beginning, before main().
        Use this method to create your things, rebind connections, setup hardware, etc.
        """
        print("Started. Press CTRL+C to end")
        self.__thing = self.client.create_thing('offer_basic')
        with self.__thing.get_meta() as meta:
            meta.set_label('offer basic label')
            meta.set_description('offer basic description')
            meta.set_location(51.7520, -1.2577)  # Oxford as an example

        self.__thing.create_tag(['test', 'example'])

        # self.__callback not used here, but is a mandatory parameter.
        # We'll use __callback_parsed to take advantage of control request template to validate their input
        self.__control = self.__thing.create_control('offer_basic_control', self.__callback,
                                                     callback_parsed=self.__callback_parsed)
        with self.__control.get_meta() as meta:
            meta.set_label('offer basic control label')

        self.__control.create_value('temp', Datatypes.DECIMAL, description="Thermostat setting", unit=Units.CELSIUS)

        self.__thing.set_public(public=True)

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
    OfferBasic(config="agent1.ini").run()

if __name__ == '__main__':
    main()
