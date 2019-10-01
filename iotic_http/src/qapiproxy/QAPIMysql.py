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

import MySQLdb


class QAPIMysql(object):

    def __init__(self, host, port, db, user, passwd):
        self.__host = host
        self.__port = int(port)
        self.__db = db
        self.__user = user
        self.__passwd = passwd

    def __get_conncur(self):
        conn = MySQLdb.connect(host=self.__host,
                               port=self.__port,
                               user=self.__user,
                               passwd=self.__passwd,
                               db=self.__db)
        cur = conn.cursor()
        return conn, cur

    @staticmethod
    def __close_conncur(conn, cur):
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def __dict_factory(cur, row):
        dic = {}
        for idx, col in enumerate(cur.description):
            colname = col[0].lower()
            if isinstance(row[idx], bytes):
                dic[colname] = row[idx].decode('utf8')
            elif isinstance(row[idx], str) and 'None' in row[idx]:
                dic[colname] = None
            else:
                dic[colname] = row[idx]
        return dic

    def config_list(self):
        ret = []
        conn, cur = self.__get_conncur()
        try:
            cur.execute("SELECT `epId` FROM `qaconfig`;")
            for row in cur.fetchall():
                ret.append(row[0])
        except:
            raise
        self.__close_conncur(conn, cur)
        return ret

    def config_read(self, userid):
        ret = None
        conn, cur = self.__get_conncur()
        try:
            cur.execute("SELECT host, vhost, prefix, epId, passwd, token FROM qaconfig WHERE epId = '%s';"
                        % str(userid))
            for row in cur.fetchall():
                ret = self.__dict_factory(cur, row)
        except:
            raise
        self.__close_conncur(conn, cur)
        return ret
