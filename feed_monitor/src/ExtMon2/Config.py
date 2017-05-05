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
"""Wrapper object for the ExtMon2 Configuration file
"""

from __future__ import unicode_literals

import os.path
import logging
logger = logging.getLogger(__name__)

from IoticAgent.Core.compat import PY3

if PY3:
    from configparser import ConfigParser  # pylint: disable=import-error,wrong-import-order
else:
    from ConfigParser import ConfigParser  # pylint: disable=import-error,wrong-import-order


class Config(object):

    def __init__(self, fn):
        """Config helper reads/writes .ini files.
        """
        self.__config = {}
        self.__fname = fn
        conf_name = self.__fname
        if os.path.exists(self.__fname):
            conf_stream = open(self.__fname, 'r')
        #
        cpa = ConfigParser()
        if PY3:
            cpa.read_file(conf_stream, source=conf_name)  # pylint: disable=no-member
        else:
            cpa.readfp(conf_stream, conf_name)  # pylint: disable=deprecated-method
        for ese in cpa.sections():
            for eva in cpa.options(ese):
                self.__set(ese, eva, cpa.get(ese, eva))

    def get(self, section, val=None):
        """Get a setting or the default

        `Returns` The current value of the setting `val` or the default, or `None` if not found
        Or dictionary of whole section if val is None

        `section` (mandatory) (string) the section name in the config E.g. `"agent"`

        `val` (optional) (string) the section name in the config E.g. `"host"`
        """
        if section in self.__config:
            if val is None:
                return self.__config[section]
            if val in self.__config[section]:
                val = val.lower()
                data = self.__config[section][val]
                if '\n' in data:
                    return data.split('\n')[1:]
                return data
        return None

    def __set(self, section, val, data):
        """Add a setting to the config

        `section` (mandatory) (string) the section name in the config E.g. `"agent"`

        `val` (mandatory) (string) the section name in the config E.g. `"host"`

        `data` (mandatory) (as appropriate) the new value for the `val`
        """
        val = val.lower()
        if section not in self.__config:
            self.__config[section] = {}
        self.__config[section][val] = data
