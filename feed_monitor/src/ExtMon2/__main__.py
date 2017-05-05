# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/Iotic-Labs/py-application-examples/blob/master/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Iotic Labs ExtMon2: Simple feed status
"""

from __future__ import unicode_literals

import logging
logging.getLogger('rdflib').setLevel(logging.WARNING)
logging.getLogger('IoticAgent').setLevel(logging.WARNING)
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

from sys import argv, exit  # pylint: disable=redefined-builtin
from os import environ, mkdir
from os.path import exists, isdir, abspath, join, split
from threading import Thread
from functools import partial
from datetime import datetime

from humanize import naturaltime

from jinja2 import Environment, FileSystemLoader

from IoticAgent import IOT
from IoticAgent.Core.compat import Event, Lock, monotonic

from .Config import Config


EXTMON2 = 'extmon2'

FEEDS = 'FD'
CHANGED = 'CH'
LASTCHANGE = 'LC'

LAST_SEEN = 'L_S'
SEEN = 'SE'

# Note: used in html template or config
NAME = 'name'
LASTSEEN = 'lastseen'
CLASS = 'class'
MAX_AGE = 'max_age'
WARN_AGE = 'warn_age'
ERROR_AGE = 'error_age'

# If no feeddata has arrived update the HTML after N seconds
MINCHANGE = 30


def __feeddata(client, stash, stashlock, data):
    with stashlock:
        if data['pid'] in stash[FEEDS]:
            logger.debug("Received FEEDATA from %s", data['pid'])
        else:
            logger.warning("Got feeddata for unknown GUID: %s", data['pid'])
            name = "<i>Feed: %s" % data['pid']
            point_desc = client.describe(data['pid'])
            if point_desc is not None:
                name += "<br/>" + point_desc['meta']['label']
                thing_desc = client.describe(point_desc['meta']['parent'])
                if thing_desc is not None:
                    name += "<br/>" + thing_desc['meta']['label']
            name += "</i>"
            stash[FEEDS][data['pid']] = {
                MAX_AGE: 600,
                WARN_AGE: 1200,
                ERROR_AGE: 2400,
                NAME: name
            }
        stash[FEEDS][data['pid']][LAST_SEEN] = datetime.utcnow()
        stash[FEEDS][data['pid']][SEEN] = True
        stash[CHANGED] = True


def extmon(config, stop):
    stash = {FEEDS: {},
             CHANGED: True,
             LASTCHANGE: 0}
    stashlock = Lock()

    templatedir = split(config.get(EXTMON2, 'template'))[0]
    templatefile = split(config.get(EXTMON2, 'template'))[1]
    wwwfile = join(config.get(EXTMON2, 'wwwpath'), 'index.html')

    feeds_list = config.get(EXTMON2, 'feeds')
    for feed in feeds_list:
        guid = config.get(feed, 'guid')
        stash[FEEDS][guid] = config.get(feed)
        stash[FEEDS][guid][SEEN] = False
        stash[FEEDS][guid][LAST_SEEN] = datetime.utcnow()
        max_age = stash[FEEDS][guid][MAX_AGE] = int(stash[FEEDS][guid][MAX_AGE])
        if WARN_AGE not in stash[FEEDS][guid]:
            stash[FEEDS][guid][WARN_AGE] = max_age * 2
        else:
            stash[FEEDS][guid][WARN_AGE] = int(stash[FEEDS][guid][WARN_AGE])
        if ERROR_AGE not in stash[FEEDS][guid]:
            stash[FEEDS][guid][ERROR_AGE] = max_age * 3
        else:
            stash[FEEDS][guid][ERROR_AGE] = int(stash[FEEDS][guid][ERROR_AGE])

    client = IOT.Client(config=config.get(EXTMON2, 'agent'))
    client.register_catchall_feeddata(partial(__feeddata, client, stash, stashlock))

    while not stop.is_set():
        with client:
            try:
                thing = client.create_thing("extmon2")
            except:
                logger.error("Failed to create_thing(extmon2).  Giving up.")
                stop.set()
                return

            with stashlock:
                for guid in stash[FEEDS]:
                    try:
                        thing.follow(guid)
                    except:
                        logger.error("Failed to follow('%s').  Giving up.", guid)
                        stop.set()
                        return
                    if NAME not in stash[FEEDS][guid]:
                        desc = client.describe(guid)
                        if desc is None:
                            stash[FEEDS][guid][NAME] = 'No Public Meta GUID: ' + guid
                        else:
                            stash[FEEDS][guid][NAME] = desc['meta']['label']

            while not stop.is_set():
                with stashlock:
                    if stash[CHANGED] or monotonic() - stash[LASTCHANGE] >= MINCHANGE:
                        logger.debug("Stash changed, updating HTML")
                        nowtime = datetime.utcnow()
                        stash[LASTCHANGE] = monotonic()

                        for guid in stash[FEEDS]:
                            delta = nowtime - stash[FEEDS][guid][LAST_SEEN]
                            delta_secs = delta.total_seconds()
                            stash[FEEDS][guid][LASTSEEN] = naturaltime(delta_secs)

                            if delta_secs < stash[FEEDS][guid][MAX_AGE] and stash[FEEDS][guid][SEEN]:
                                stash[FEEDS][guid][CLASS] = 'green'
                            elif delta_secs < stash[FEEDS][guid][WARN_AGE]:
                                stash[FEEDS][guid][CLASS] = 'yellow'
                            else:
                                stash[FEEDS][guid][CLASS] = 'red'

                            if stash[FEEDS][guid][SEEN] is False:
                                stash[FEEDS][guid][LASTSEEN] = "Not seen since restart: " + stash[FEEDS][guid][LASTSEEN]

                        j2env = Environment(loader=FileSystemLoader(templatedir), trim_blocks=True)
                        with open(wwwfile, 'w') as f:
                            f.write(j2env.get_template(templatefile).render(feeds=stash[FEEDS]))

                        stash[CHANGED] = False

                stop.wait(timeout=1)

    # If this function ends prematurely ensure stop is set!
    stop.set()


def usage():
    logger.error('Usage: python3 -m Ioticiser ../cfg/example.ini')
    return 1


def main():  # pylint: disable=too-many-return-statements,too-many-branches
    if len(argv) < 2:
        if not exists(argv[1]):
            return usage()
    try:
        cfg = Config(argv[1])
    except:
        logger.exception("Failed to load/parse Config file '%s'. Giving up.", argv[1])
        return 1

    wwwpath = cfg.get(EXTMON2, 'wwwpath')
    if wwwpath is None:
        logger.error("Config file must have [extmon2] section with wwwpath = /path/to/storage")
        return 1
    wwwpath = abspath(wwwpath)
    if not exists(wwwpath):
        mkdir(wwwpath)
    elif exists(wwwpath) and not isdir(wwwpath):
        logger.error("Config file must have [extmon2] wwpath not a directory")
        return 1

    template = cfg.get(EXTMON2, 'template')
    if template is None or not exists(template):
        logger.error("Config file must have [extmon2] section with template = /path/to/file.html")
        return 1

    agent = cfg.get(EXTMON2, 'agent')
    if agent is None or not exists(agent):
        logger.error("Config file must have [extmon2] section with agent = /path/to/agent.ini")
        return 1

    feeds_list = cfg.get(EXTMON2, 'feeds')
    if feeds_list is None:
        logger.error("Config file must have [extmon2] feeds = \n\nFeedeName\n\tFeed_Two")
        return 1

    for feed in feeds_list:
        if cfg.get(feed, 'guid') is None or cfg.get(feed, MAX_AGE) is None:
            logger.error("Config section for feed [%s] must have guid and max_age", feed)
            return 1

    stop_evt = Event()
    thread = Thread(target=extmon, name='extmon', args=(cfg, stop_evt,))
    thread.start()

    if 'IOTIC_BACKGROUND' in environ:
        from signal import signal, SIGINT, SIGTERM

        logger.info("Started in non-interactive mode.")

        def exit_handler(signum, frame):  # pylint: disable=unused-argument
            logger.info('Shutdown requested')
            stop_evt.set()

        signal(SIGINT, exit_handler)
        signal(SIGTERM, exit_handler)

        while not stop_evt.is_set():
            stop_evt.wait(timeout=5)
        stop_evt.set()
    else:
        try:
            while not stop_evt.is_set():
                logger.info('Enter ctrl+c to exit')
                stop_evt.wait(timeout=600)
        except SystemExit:
            pass
        except KeyboardInterrupt:
            pass
        stop_evt.set()

    logger.info("Waiting for thread to finish...")
    thread.join()
    return 0


if __name__ == '__main__':
    exit(main())
