#!/usr/bin/env python3
# Copyright (c) 2016 Iotic Labs Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/Iotic-Labs/IoticHttp/blob/master/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Iotic Labs HTTPS QAPI Proxy main
"""

# pylint: disable=invalid-name

from sys import argv
from os import environ
import logging

from .QAPIManager import QAPIManager
from .QAPIConfig import QAPIConfig
from . import RESTServer

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

qapimanager = server = thread = None


def stop():
    global qapimanager, server, thread
    logger.info("Stopping...")
    RESTServer.stopServer(server, thread)
    qapimanager.stop()


def main():
    global qapimanager, server, thread

    if len(argv) < 2:
        logger.error('Usage: python3 -m qapiproxy /path/to/config.ini')
        exit(1)
    try:
        config = QAPIConfig(fname=argv[1])
    except FileNotFoundError as exc:
        logger.error(str(exc))
        logger.error('Usage: python3 -m qapiproxy /path/to/config.ini')
        exit(1)
    # todo except blah

    # TODO: config validation etc

    qapimanager = QAPIManager(config)
    qapimanager.start()

    insecure_mode = False
    if 'insecure_mode' in config['https']:
        if bool(config['https']['insecure_mode']) is True:
            insecure_mode = True

    server, thread = RESTServer.setupServer(
        (config['https']['host'], int(config['https']['port'])),
        config['https']['ssl_ca'],
        config['https']['ssl_crt'],
        config['https']['ssl_key'],
        config['https']['ssl_pass'],
        qapimanager,
        insecure_mode
    )

    if 'IOTIC_BACKGROUND' in environ:
        from signal import signal, SIGINT, SIGTERM
        from time import sleep

        logger.info("Started in non-interactive mode.")

        def exit_handler(signum, frame):  # pylint: disable=unused-argument
            logger.info('Shutdown requested')
            stop()

        signal(SIGINT, exit_handler)
        signal(SIGTERM, exit_handler)

        while qapimanager.is_alive():
            sleep(5)
    else:
        try:
            while True:
                print('Enter "q" to exit')
                try:
                    if input() == 'q':
                        break
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        except SystemExit:
            pass
        stop()
    return 0


if __name__ == '__main__':
    exit(main())
