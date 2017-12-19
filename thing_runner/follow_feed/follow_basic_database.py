# -*- coding: utf-8 -*-
# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.

from __future__ import unicode_literals, print_function

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] {%(threadName)s} %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from IoticAgent.Core.compat import Queue, Empty
from IoticAgent.IOT.RemotePoint import RemoteFeed
from IoticAgent.ThingRunner import RetryingThingRunner
from IoticAgent import Datatypes

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker

Base = declarative_base()  # pylint:disable=invalid-name


class Feed(Base):
    __tablename__ = "Feeds"

    guid = Column(String, primary_key=True)
    label = Column(String)
    comment = Column(String)


class FeedData(Base):
    __tablename__ = "FeedData"

    data_id = Column(Integer, primary_key=True)
    feed_id = Column(String, ForeignKey('Feeds.guid'))
    time_st = Column(DateTime)
    int_data = Column(Integer)
    str_data = Column(String)
    unit = Column(String)


class FollowBasicDatabase(RetryingThingRunner):
    LOOP_TIMER = 10  # minimum number of seconds duration of the main loop

    def __init__(self, config=None):
        """Instantiation code in here, after the call to super().__init__()
        """
        super(FollowBasicDatabase, self).__init__(config=config)
        self.__thing = None

        self.__eng = create_engine('sqlite:///feeddata.db')
        self.__feeds = None
        self.__data = None
        self.__sesh = None  # SQLAlchemy database session
        self.__queue = Queue()  # Queue to communicate between callback threads and main thread

    @staticmethod
    def __callback(args):
        logger.debug("Unparseable feed data received. Shared at %s", args['time'])

        # Used for any feed data that can't be parsed
        try:
            logger.debug('Found feed data for key %s: value: %s', 'count', args['data']['count'])
        except KeyError as exc:
            logger.warning('Failed to find key %s in recent data %s', exc, args)
            raise

    def __callback_parsed(self, args):
        logger.debug("Feed data received. Shared at %s", args['time'])

        # add the feed data to the queue to be added to the db in the main thread
        self.__queue_data_add(args['pid'], args['time'], args['parsed'])

    def __cb_subscribed(self, arg):
        if isinstance(arg, RemoteFeed):
            logger.info("Subscribed to a new remote Feed")
            rm_feed_info = self.client.describe(arg)

            # Choose whether to follow parsed (if we know the values) or not
            if not rm_feed_info['meta']['values']:  # Not a public feed or feed has no values
                logger.info("Following Feed with no values")
                self.__thing.follow(arg.guid, callback=self.__callback)
            else:
                logger.info("Following Feed with known values")
                # add the feed to the queue to be added to the db in the main thread
                self.__queue_feed_add(arg.guid, rm_feed_info)
                self.__thing.follow(arg.guid, callback_parsed=self.__callback_parsed)

    def __queue_feed_add(self, guid, rm_feed_info):
        """Construct a Feed object and put it on the queue to be added to the database in the main thread
        """
        feed = Feed(guid=guid,
                    label=rm_feed_info['meta']['label'],
                    comment=rm_feed_info['meta']['comment'])
        self.__queue.put(feed)

    def __db_feed_add(self, feed):
        """Add the feed to the database if it doesn't already exist
        """
        # add the feed to the Feeds table
        try:
            self.__sesh.merge(feed)  # merge() rather than add() in case we're subscribed to the same feed twice
            self.__sesh.commit()
        except Exception:  # pylint: disable=broad-except
            logger.exception("merge / commit", exc_info=True)

    def __queue_data_add(self, guid, date_time, args):
        """Construct FeedData objects from the feed data and put them in the queue for adding in the main thread
        """
        # use the parseable feed data to populate the FeedData objects look for numbers and then strings
        values = args.filter_by(types=(Datatypes.INTEGER, Datatypes.DECIMAL, Datatypes.INT,
                                       Datatypes.FLOAT, Datatypes.LONG, Datatypes.DOUBLE))
        if values:
            for value in values:
                logger.debug('Integer Found parsed data for key %s: value: %s', value.label, value.value)
                data = FeedData(feed_id=guid,
                                time_st=date_time,
                                int_data=value.value,
                                str_data=None,
                                unit=value.unit)
                self.__queue.put(data)
        else:
            logger.debug("Numeric data not found - won't add")

        values = args.filter_by(types=(Datatypes.STRING,))
        if values:
            for value in values:
                logger.debug('String Found parsed data for key %s: value: %s', value.label, value.value)
                data = FeedData(feed_id=guid,
                                time_st=date_time,
                                int_data=None,
                                str_data=value.value,
                                unit=value.unit)
                self.__queue.put(data)
        else:
            logger.debug("String data not found - won't add")

    def __db_data_add(self, data):
        """Add the feed data to the database
        """
        try:
            self.__sesh.add(data)
            self.__sesh.commit()
        except Exception:  # pylint: disable=broad-except
            logger.exception("add / commit", exc_info=True)

    def on_startup(self):
        """Called once at the beginning, before main().
        Use this method to create your things, rebind connections, setup hardware, etc.
        """
        print("Started. Press CTRL+C to end")

        self.__thing = self.client.create_thing('follow_basic')

        # create the database
        Base.metadata.bind = self.__eng
        Base.metadata.create_all()
        # and a session
        self.__sesh = sessionmaker(bind=self.__eng)()

        # register a callback for any new subscriptions that have been made for you - perhaps in the UI
        self.client.register_callback_subscribed(self.__cb_subscribed)

    def main(self):
        """Called after on_startup.
        Use this method for your main loop
        Set self.LOOP_TIMER for your regular tick
        In this example, we wait for queue items to be posted to us from the callback and then dispatch them
        to the database.
        This approach prevents the use of the Session object by more than one thread, which Sqlite doesn't like
        """
        while not self.shutdown_requested:
            try:
                item = self.__queue.get(timeout=self.LOOP_TIMER)
            except Empty:  # didn't get a queue item
                pass
            else:  # got a queue item, put it in the correct part of the database
                if isinstance(item, Feed):
                    self.__db_feed_add(item)
                elif isinstance(item, FeedData):
                    self.__db_data_add(item)

    def on_shutdown(self, exc_info):  # pylint: disable=unused-argument
        """One-off tasks to perform on just before agent shutdown. exc_info is a tuple (as for `sys.exc_info()`) of the
        exception which caused the shutdown (from the `main()` function)
        Here, we'll just print out what we put in the database
        """
        print("Stopping...")

        rset = self.__sesh.query(Feed).all()
        for feed in rset:
            logger.debug("Feed id: %s, Feed label: %s, Feed comment: %s", feed.guid, feed.label, feed.comment)

        rset = self.__sesh.query(FeedData).all()
        for data in rset:
            logger.debug("Feed id: %s, Feed time: %s, Feed int: %s, Feed str: %s, Feed unit: %s",
                         data.feed_id, data.time_st, data.int_data, data.str_data, data.unit)

        self.__sesh.close()


def main():
    FollowBasicDatabase(config="agent2.ini").run()

if __name__ == '__main__':
    main()
