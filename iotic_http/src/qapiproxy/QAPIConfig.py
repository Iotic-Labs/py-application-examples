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

import logging
logger = logging.getLogger(__name__)

import os.path

from configparser import ConfigParser  # pylint: disable=import-error,wrong-import-order


class QAPIConfig(object):

    def __init__(self, config=None, fname=None):
        self.__config = {}
        if config is not None:
            self.__config = config
        elif fname is not None:
            if not os.path.exists(fname):
                raise FileNotFoundError('File "%s" not found' % fname)
            configpar = ConfigParser()
            configpar.read(fname)
            for ese in configpar.sections():
                self.__config[ese.lower()] = {}
                for eva in configpar.options(ese):
                    self.__config[ese.lower()][eva.lower()] = configpar.get(ese, eva)

    def config_list(self):
        return self.__config['config']['agents'].strip().split("\n")

    def config_read(self, name):
        return self.__config[name.lower()]  # TODO: checking etc

    def __getitem__(self, name):
        return self.__config[name]
