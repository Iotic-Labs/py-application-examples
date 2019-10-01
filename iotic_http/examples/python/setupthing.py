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


# Imports ---------------------------

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.INFO)

# Globals ---------------------------

CONTENT_TYPE = 'application/json; charset=utf-8'
PROXY_URL = 'iotic.example.com'
PROXY_CRT = 'path/file.crt'
PROXY_KEY = 'path/file.key'
# Agent credentials
EPID = 'agentEPID'
AUTH = 'agentAUTH'
X_LANGUAGE = 'en'

PROXY_HEADERS = {'epId':EPID, 'authToken':AUTH, 'content-type':CONTENT_TYPE, 'X-Language': X_LANGUAGE}

# CLASS APIRequester --------------------------------------------------------------------------------------

class APIRequester(object):
    '''
        This class manages the calls to the API
    '''
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

    @classmethod
    def request(cls, method, url, body = None):

        full_url = PROXY_URL + url
        response = requests.Response()

        try:
            if method == cls.GET:
                response = requests.get(full_url, cert=(PROXY_CRT, PROXY_KEY), headers=PROXY_HEADERS, verify=False)
            elif method == cls.POST:
                response = requests.post(full_url, cert=(PROXY_CRT, PROXY_KEY), headers=PROXY_HEADERS, data=body, verify=False)
            elif method == cls.PUT:
                response = requests.put(full_url, cert=(PROXY_CRT, PROXY_KEY), headers=PROXY_HEADERS, data=body, verify=False)
            elif method == cls.DELETE:
                response = requests.delete(full_url, cert=(PROXY_CRT, PROXY_KEY), headers=PROXY_HEADERS, verify=False)
            else:
                response = requests.head(full_url, cert=(PROXY_CRT, PROXY_KEY), headers=PROXY_HEADERS, verify=False)

            response.raise_for_status()

        except Exception as e:
            logger.error("__call_api error: %s", str(e))
        if response.ok:
            logger.info("HTTP: %i", response.status_code)
            logger.info(response.text)
            return response
        else:
            logger.error("__call_api error %i", response.status_code)

# MAIN ------------------------------------------------------------------------------------------------------

def main():

    logger.info('Create a new entity')
    thing_lid = 'test_thing_lid'

    payload = {'lid':thing_lid}
    body = json.dumps(payload)
    response = APIRequester.request(APIRequester.POST, '/entity', body)

    logger.info('Set Metadata')
    payload = {"label": "a label in english", "description": "some describing stuff", "lat": 12, "lon": 34}
    body = json.dumps(payload)
    response = APIRequester.request(
        APIRequester.PUT,
        '/entity/' + thing_lid + '/metahelper',
        body)

    logger.info('Set Public')
    payload = {'public': True}
    body = json.dumps(payload)
    response = APIRequester.request(
        APIRequester.PUT,
        '/entity/' + thing_lid + '/setpublic',
        body)

    logger.info('Add tags')
    payload = {'tags': ['hello', 'fish'], 'lang': 'en'}
    body = json.dumps(payload)
    response = APIRequester.request(
        APIRequester.POST,
        '/entity/' + thing_lid + '/tag',
        body)

    logger.info('Create a feed on an entity')
    point_lid = 'data'

    payload = {'pid': point_lid, 'lid': thing_lid, 'saveRecent': 1}
    body = json.dumps(payload)
    response = APIRequester.request(
        APIRequester.POST,
        '/point/feed',
        body)

    logger.info('Create feed value: number')
    payload = {"label":"number", "vtype": "integer"}
    body = json.dumps(payload)
    response = APIRequester.request(
        APIRequester.POST,
        '/value/feed/' + thing_lid + '/' + point_lid,
        body)

    logger.info('Create feed value: word')
    payload = {"label":"word", "vtype": "string"}
    body = json.dumps(payload)
    response = APIRequester.request(
        APIRequester.POST,
        '/value/feed/' + thing_lid + '/' + point_lid,
        body)

    logger.info('Share data from a feed')
    payload = {'number': 87, 'word': 'turtle'}
    body = json.dumps(payload)
    response = APIRequester.request(
        APIRequester.POST,
        '/point/' + thing_lid + '/' + point_lid + '/share',
        body)





# RUN --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# END --------------------------------------------------------------------------------------------------