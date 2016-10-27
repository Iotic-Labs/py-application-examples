# /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example demonstrating:

- Use of energenie's discovery mode and an "ask" function
- creation of new iotic object(s) in response to events (discovery of a new energenie)
- an object that keeps a list of the iotic objects it's created and how it calls their functions

"""

# Python 2 backwards compatibility
from __future__ import unicode_literals, print_function

from time import sleep
import logging
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from IoticAgent import ThingRunner
from IoticSocket import IoticSocket
import energenie

NEW_DEVICE_IDS = []


class EnergenieSocketRunner(ThingRunner):

    def __init__(self, config=None):
        super(EnergenieSocketRunner, self).__init__(config=config)
        self.__socket_list = []

    def on_startup(self):
        # nothing to do here as we're doing dynamic creation
        pass

    def new_socket(self, device):
        self.__socket_list.append(IoticSocket(client=self.client, device=device))

    def main(self):
        while True:
            logger.info('main loop')
            for socket in self.__socket_list:
                socket.check_switch_state()

            # better than using time.sleep() as this will break immediately
            if self.wait_for_shutdown(1):
                return


def in_background(socket_runner):
    global NEW_DEVICE_IDS  # pylint: disable=global-statement
    socket_runner.run(background=True)
    try:
        while True:
            logger.info('Calling Energenie Loop')
            NEW_DEVICE_IDS = []
            energenie.loop()
            for productid, sensorid in NEW_DEVICE_IDS:
                logger.info("device_id: %s", sensorid)
                auto_name = "auto_%s_%s" % (str(hex(productid)), str(hex(sensorid)))
                socket_runner.new_socket(energenie.registry.get(auto_name))
            sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        socket_runner.stop()


def energenie_ask_fn(address, message):
    global NEW_DEVICE_IDS  # pylint: disable=global-statement, global-variable-not-assigned
    logger.debug("address %s", str(address))
    logger.debug("message %s", str(message))

    try:
        # check that the device id is ok - i.e. it's a mihome plug adapter and
        # save a tuple of product and sensor id if it is
        if message['header']['productid'] == energenie.Devices.PRODUCTID_MIHO005:
            NEW_DEVICE_IDS.append((message['header']['productid'], message['header']['sensorid']))
    except KeyError:
        pass

    return True


def main():
    energenie.init()
    socket_runner = EnergenieSocketRunner(config='m2_fan.ini')
    energenie.discovery_ask(energenie_ask_fn)
    in_background(socket_runner)
    energenie.finished()

if __name__ == "__main__":
    main()
