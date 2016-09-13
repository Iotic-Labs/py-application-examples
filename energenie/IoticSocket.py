# /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example demonstrating:

- Separating out the Iotic API interactions into their own object
- Advertising a control and responding to it being actuated
- Advertising a feed and sharing it on an external event (switch state changing)
"""

# Python 2 backwards compatibility
from __future__ import unicode_literals, print_function

import logging
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from IoticAgent import Datatypes


class IoticSocket(object):
    # pylint: disable=attribute-defined-outside-init
    # pylint: disable=too-many-instance-attributes

    # Changing the LID of a self.__thing/feed/control will create a new one rather than replace it
    # Change thing_lid (and maybe tags) to run a second copy of this script with different agent credentials
    thing_lid = 'fan_2_newstyle'
    thing_label = 'Newstyle fan_2'
    thing_description = 'Energenie plug using new iotic style and new energenie code'
    # Set to None to not have location set
    thing_location = (51.4826, -0.0077)
    thing_tags = ['Energenie', 'Your Tag Here']
    # Set to False to not make metadata about self.__thing and its feeds & controls public
    # NOTE: Value-based feed/control data usage (e.g. get_skeleton) will not work if not public!
    thing_public = True

    # Advertise feed & share data
    feed_lid = 'switch_state'
    feed_label = 'Switch State'

    # Advertise control and accept ask/tell requests
    control_lid = 'switch_control'
    control_label = 'Switch control'
    # Require control requests to specify correct passphrase. Set to None for no check
    control_secret = 'DEADBEEF'

    def __init__(self, client=None, device=None):
        """client: Iotic client object
           device: Energenie device object
        """
        if client is None:
            raise ValueError("must specify an Iotic client")
        self.__client = client
        if device is None:
            raise ValueError("must specify an energenie device")
        self.__device = device

        self.__thing = None
        self.__feed = None
        self.__control = None
        self.__switch_old_state = None
        self.__switch_now_state = None
        self.__create()

    def __create(self):
        logger.info('Creating thing %s:', self.thing_lid + str(self.__device.get_device_id()))
        self.__thing = self.__client.create_thing(self.thing_lid + str(self.__device.get_device_id()))
        with self.__thing.get_meta() as meta:
            meta.set_label(self.thing_label + " : " + str(self.__device.get_device_id()))
            meta.set_description(self.thing_description)
            if self.thing_location:
                meta.set_location(*self.thing_location)
            else:
                meta.delete_location()
        self.__thing.create_tag(self.thing_tags)

        self.__advertise_feed()

        self.__advertise_control()

        self.__thing.set_public(self.thing_public)

    def __advertise_feed(self):
        logger.info('Advertising feed')
        self.__feed = self.__thing.create_feed(self.feed_lid)
        with self.__feed.get_meta() as meta:
            meta.set_label(self.feed_label)
        self.__feed.create_value('switch_state', Datatypes.BOOLEAN, description='State of switch')

    def __advertise_control(self):
        logger.info('Advertising control')
        self.__control = self.__thing.create_control(self.control_lid, None,
                                                     callback_parsed=self.__switch_control_callback)
        with self.__control.get_meta() as meta:
            meta.set_label(self.control_label)
        self.__control.create_value('switch_request',
                                    Datatypes.STRING,
                                    description='Send "ON" to turn on, "OFF" to turn off')
        self.__control.create_value('secret', Datatypes.STRING, description='Passphrase to authenticate request')

    def __share_feed(self):
        logger.info('SHAREing feed')
        self.__skel_feed = self.__feed.get_skeleton()

        self.__skel_feed.values.switch_state = self.__switch_now_state
        self.__feed.share(self.__skel_feed)

    def __switch_control_callback(self, args):
        values = args['parsed'].values
        if self.control_secret is None or self.control_secret == values.secret:
            logger.info('Got control request: %s', values.switch_request)
            self.__device.set_switch(True if values.switch_request == "ON" else False)
            success = True
            # confirm the control request, if requested to do so
            if args['confirm']:
                logger.debug('Confirm tell')
                self.__client.confirm_tell(args, success)
        else:
            logger.warning('Ignoring control request due to unexpected secret: %s', values.secret)

    def check_switch_state(self):
        self.__switch_now_state = self.__device.get_switch()
        if self.__switch_old_state != self.__switch_now_state:
            self.__switch_old_state = self.__switch_now_state
            self. __share_feed()
