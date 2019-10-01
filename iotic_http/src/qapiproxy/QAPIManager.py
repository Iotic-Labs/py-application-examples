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

from threading import Thread, Event, Lock

from IoticAgent import Core as IoticAgentCore

from .QAPIWorker import QAPIWorker
from .QAPIConfig import QAPIConfig
QAPIMysql = None
try:
    from .QAPIMysql import QAPIMysql
except ImportError:
    logger.info("Failed to import MySQLdb.")


class QAPIManager(object):

    def __init__(self, config):
        self.__config = config
        #
        if self.__config['config']['mode'] == 'ini':
            self.__config_reader = QAPIConfig(config=self.__config)  # TODO: validation
        elif self.__config['config']['mode'] == 'mysql':
            if QAPIMysql is None:
                raise ValueError("Config Mode is mysql but MySQLdb import failed.")
            self.__config_reader = QAPIMysql(  # TODO: validation
                self.__config['config']['dbhost'],
                self.__config['config']['dbport'],
                self.__config['config']['dbname'],
                self.__config['config']['dbuser'],
                self.__config['config']['dbpass']
            )
        else:
            raise ValueError("Config Mode must be 'ini' or 'mysql'")
        #
        self.__thread = None
        self.__stop = Event()
        #
        self.__new_workertime = int(self.__config['qapimanager']['new_worker'])
        self.__workers = {}
        self.__workers_lock = Lock()

    def start(self):
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def stop(self):
        self.__stop.set()
        self.__thread.join()
        self.__thread = None

    def is_alive(self):
        return self.__thread is not None

    def __check_epid(self, epid, authtoken):
        """check_epid & accessToken helper

        Raises: ValueError for no ep / bad auth_token.
        """
        if epid in self.__workers:
            if self.__workers[epid].check_authtoken(authtoken):
                return True
        raise KeyError("no such epId")

    def default_lang(self, epid, authtoken):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].default_lang

    def get_feeddata(self, epid, authtoken):
        with self.__workers_lock:
            try:
                self.__check_epid(epid, authtoken)
            except:
                return []
            return self.__workers[epid].get_feeddata()

    def get_controlreq(self, epid, authtoken):
        with self.__workers_lock:
            try:
                self.__check_epid(epid, authtoken)
            except:
                return []
            return self.__workers[epid].get_controlreq()

    def get_unsolicited(self, epid, authtoken):
        with self.__workers_lock:
            try:
                self.__check_epid(epid, authtoken)
            except:
                return []
            return self.__workers[epid].get_unsolicited()

    def request_entity_create(self, epid, authtoken, lid, tepid=None):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_create(lid, tepid=tepid)

    def request_entity_rename(self, epid, authtoken, lid, newlid):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_rename(lid, newlid)

    def request_entity_reassign(self, epid, authtoken, lid, nepid=None):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_reassign(lid, nepid)

    def request_entity_delete(self, epid, authtoken, lid):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_delete(lid)

    def request_entity_list(self, epid, authtoken, limit=500, offset=0):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_list(limit=limit, offset=offset)

    def request_entity_list_all(self, epid, authtoken, limit=500, offset=0):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_list_all(limit=limit, offset=offset)

    def request_entity_meta_get(self, epid, authtoken, lid, fmt="n3"):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_meta_get(lid, fmt=fmt)

    def request_entity_meta_set(self, epid, authtoken, lid, meta, fmt="n3"):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_meta_set(lid, meta, fmt=fmt)

    def request_entity_meta_setpublic(self, epid, authtoken, lid, public=True):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_meta_setpublic(lid, public=public)

    def request_entity_tag_update(self, epid, authtoken, lid, tags, delete=False):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_tag_update(lid, tags, delete=delete)

    def request_entity_tag_list(self, epid, authtoken, lid, limit=100, offset=0):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_entity_tag_list(lid, limit=limit, offset=offset)

    def __dummy_cb(self, *args, **kwargs):
        pass

    def request_point_create(self, epid, authtoken, foc, lid, pid, save_recent=0):
        cb = None
        if foc == IoticAgentCore.Const.R_CONTROL:
            cb = self.__dummy_cb
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_create(foc, lid, pid, control_cb=cb, save_recent=save_recent)

    def request_point_rename(self, epid, authtoken, foc, lid, pid, newpid):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_rename(foc, lid, pid, newpid)

    def request_point_delete(self, epid, authtoken, foc, lid, pid):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_delete(foc, lid, pid)

    def request_point_list(self, epid, authtoken, foc, lid, limit=500, offset=0):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_list(foc, lid, limit=limit, offset=offset)

    def request_point_list_detailed(self, epid, authtoken, foc, lid, pid):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_list_detailed(foc, lid, pid)

    def request_point_meta_get(self, epid, authtoken, foc, lid, pid, fmt="n3"):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_meta_get(foc, lid, pid, fmt=fmt)

    def request_point_meta_set(self, epid, authtoken, foc, lid, pid, meta, fmt="n3"):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_meta_set(foc, lid, pid, meta, fmt=fmt)

    def request_point_value_create(self, epid, authtoken, lid, pid, foc, label, vtype,
                                   lang=None, comment=None, unit=None):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_value_create(lid, pid, foc, label,
                                                                   vtype, lang=lang, comment=comment, unit=unit)

    def request_point_value_delete(self, epid, authtoken, lid, pid, foc, label=None):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_value_delete(lid, pid, foc, label=label)

    def request_point_value_list(self, epid, authtoken, lid, pid, foc, limit=500, offset=0):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_value_list(lid, pid, foc, limit=limit, offset=offset)

    def request_point_tag_update(self, epid, authtoken, foc, lid, pid, tags, delete=False):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_tag_update(foc, lid, pid, tags, delete=delete)

    def request_point_tag_list(self, epid, authtoken, foc, lid, pid, limit=500, offset=0):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_tag_list(foc, lid, pid, limit=limit, offset=offset)

    def request_sub_create(self, epid, authtoken, lid, foc, gpid):
        cb = None
        if foc == IoticAgentCore.Const.R_FEED:
            cb = self.__dummy_cb
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_sub_create(lid, foc, gpid, callback=cb)

    def request_sub_create_local(self, epid, authtoken, slid, foc, lid, pid):
        cb = None
        if foc == IoticAgentCore.Const.R_FEED:
            cb = self.__dummy_cb
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_sub_create_local(slid, foc, lid, pid, callback=cb)

    def request_point_share(self, epid, authtoken, lid, pid, data, mime=None):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_point_share(lid, pid, data, mime=mime)

    def request_sub_ask(self, epid, authtoken, sub_id, data, mime=None):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_sub_ask(sub_id, data, mime=mime)

    def request_sub_tell(self, epid, authtoken, sub_id, data, timeout, mime=None):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_sub_tell(sub_id, data, timeout, mime=mime)

    def request_sub_delete(self, epid, authtoken, sub_id):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_sub_delete(sub_id)

    def request_sub_list(self, epid, authtoken, lid, limit=500, offset=0):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_sub_list(lid, limit=limit, offset=offset)

    def request_sub_recent(self, epid, authtoken, sub_id, count=None):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_sub_recent(sub_id, count=count)

    def request_search(self, epid, authtoken, text=None, lang=None, location=None, unit=None,
                       limit=100, offset=0, type_='full', scope=IoticAgentCore.Const.SearchScope.PUBLIC):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_search(text=text, lang=lang, location=location,
                                                       unit=unit, limit=limit, offset=offset, type_=type_, scope=scope)

    def request_describe(self, epid, authtoken, guid, scope=IoticAgentCore.Const.DescribeScope.AUTO):
        with self.__workers_lock:
            self.__check_epid(epid, authtoken)
            return self.__workers[epid].request_describe(guid, scope=scope)

    def __run(self):
        #
        # Main loop starting/stopping QAPIWorker(s)
        logger.info("Started")
        while not self.__stop.is_set():
            agents = self.__config_reader.config_list()
            with self.__workers_lock:
                if self.__config['config']['mode'] == 'mysql':
                    # Remove Agents that have been removed from the config
                    done = False
                    while not done:
                        done = True
                        for epid in self.__workers:
                            if epid not in agents:
                                logger.info("Worker %s removed from config list.  Killing!", epid)
                                done = False
                                self.__workers[epid].stop()
                                del self.__workers[epid]
                                break
                # Stop/Re-start Agents that have changed in the config
                for name in agents:
                    #
                    try:
                        details = self.__config_reader.config_read(name)
                    except KeyError:
                        logger.error("Cannot find agent name: '%s' Skipping!", name)
                        continue
                    epid = details['epid']
                    #
                    if 'vhost' in self.__config['qapimanager']:
                        details['vhost'] = self.__config['qapimanager']['vhost']
                    if 'prefix' in self.__config['qapimanager']:
                        details['prefix'] = self.__config['qapimanager']['prefix']
                    if 'sslca' in self.__config['qapimanager']:
                        details['sslca'] = self.__config['qapimanager']['sslca']
                    if 'queue_size' in self.__config['qapimanager']:
                        details['queue_size'] = self.__config['qapimanager']['queue_size']
                    if 'throttle' in self.__config['qapimanager']:
                        details['throttle'] = self.__config['qapimanager']['throttle']
                    #
                    if epid in self.__workers:
                        if not self.__workers[epid].check_details(details):
                            logger.info("Worker %s bad details.  Killing!", epid)
                            self.__workers[epid].stop()
                            del self.__workers[epid]
                    #
                    if epid not in self.__workers:
                        logger.info("Starting new worker:  %s = %s", name, epid)
                        self.__workers[epid] = QAPIWorker(
                            details,
                            self.__stop,
                            keepFeeddata=self.__config['qapimanager']['keep_feeddata'],
                            keepControlreq=self.__config['qapimanager']['keep_controlreq'],
                            keepUnsolicited=self.__config['qapimanager']['keep_unsolicited']
                        )
                        self.__workers[epid].start()
            #
            logger.debug("QAPIManager sleeping for %s", str(self.__new_workertime))
            self.__stop.wait(self.__new_workertime)
        #
        logger.info("Waiting for workers to die...")
        with self.__workers_lock:
            for epid in self.__workers:
                self.__workers[epid].stop()
        #
        logger.info("Stopped")
