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

import logging
logger = logging.getLogger(__name__)

from importlib import import_module
from json import loads, dumps
from base64 import b64encode
from ssl import SSLContext, CERT_REQUIRED, OP_NO_COMPRESSION, PROTOCOL_TLSv1_2, RAND_add
from socket import socket as createSocket, getaddrinfo, AI_PASSIVE, SOCK_STREAM, AF_UNSPEC
# from socketserver import ForkingMixIn

from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
from re import compile as re_compile, A as re_A, I as re_I
from urllib import parse
from threading import Thread
from os import urandom
from zlib import decompress

from ubjson import loadb as ubjloadb

import IoticAgent.Core as IoticAgentCore
from IoticAgent.Core.Exceptions import LinkException
from IoticAgent.Core.Mime import expand_idx_mimetype

from . import RDFHelper

# future todo: forking + ipc (pipe?) to workers?
# class ForkingHTTPServer(ForkingMixIn, HTTPServer):
#
#    def __init__(self, server_address, RequestHandlerClass):
#        self.__setSocketFamilyAndTypeFrom(*server_address)
#        super().__init__(server_address, RequestHandlerClass)
#
#    # set parameters based on whether address is IPv4 or IPv6
#    def __setSocketFamilyAndTypeFrom(self, host, port):
#        for af, socktype, *_ in getaddrinfo(host, port, AF_UNSPEC, SOCK_STREAM, 0, AI_PASSIVE):
#            try:
#                socket = createSocket(af, socktype)
#            except OSError:
#                continue
#            socket.close()
#            self.address_family = af  # pylint: disable=invalid-name
#            self.socket_type = socktype  # pylint: disable=invalid-name
#            return
#        raise Exception('Could not create socket for %s:%s' % (host, port))


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):

    def __init__(self, server_address, RequestHandlerClass):
        self.__setSocketFamilyAndTypeFrom(*server_address)
        super().__init__(server_address, RequestHandlerClass)

    # todo: test with ab default 5
    request_queue_size = 16

    # set parameters based on whether address is IPv4 or IPv6
    def __setSocketFamilyAndTypeFrom(self, host, port):
        for af, socktype, *_ in getaddrinfo(host, port, AF_UNSPEC, SOCK_STREAM, 0, AI_PASSIVE):
            try:
                socket = createSocket(af, socktype)
            except OSError:
                continue
            socket.close()
            self.address_family = af  # pylint: disable=invalid-name
            self.socket_type = socktype  # pylint: disable=invalid-name
            return
        raise Exception('Could not create socket for %s:%s' % (host, port))


class Handler(BaseHTTPRequestHandler):

    # support multiple requests per connection
    protocol_version = 'HTTP/1.1'
    # how long before timing out qapi calls
    timeout = 10

    # Secure mode (https tlsv1.2)
    # WARNING: This flag disables HTTPS transport.  Do not touch.
    __secure = True

    __contentTypePattern = re_compile(r'^application/json; charset=utf-8$', re_I | re_A)
    __encodingTypePattern = re_compile(r'^deflate$', re_I | re_A)

    @classmethod
    def setSecureMode(cls, secure_mode):
        cls.__secure = True
        if secure_mode is False:
            cls.__secure = False

    @classmethod
    def setSSLContext(cls, ctx):
        cls.__sslContext = ctx

    @classmethod
    def setQapiManager(cls, inst):
        cls.__qapiManager = inst

    def setup(self):
        # see https://docs.python.org/3/library/ssl.html#multi-processing
        RAND_add(urandom(1), 0.0)
        #
        # HTTPS can be disabled by changing this hardcoded setting !
        if self.__secure:
            # Wrap here so parent process doesn't have to take load of wrapping & handshake.
            self.request = self.__sslContext.wrap_socket(self.request, server_side=True)
        #
        super().setup()

    def log_message(self, fmt, *args):  # pylint: disable=arguments-differ
        logger.info("%s - - [%s] %s", self.address_string(), self.log_date_time_string(), fmt % args)

    @staticmethod
    def __log(cmd, path, headers, body):
        logger.info("%s : %s : %s : %s", headers['epId'], cmd, path, body)

    def _read_body(self):
        length = self.headers.get('Content-Length', '')
        body = None
        if (length.isnumeric() and
                int(length) > 0 and
                self.__contentTypePattern.match(self.headers.get('Content-Type', ''))):
            try:
                if self.__encodingTypePattern.match(self.headers.get('Content-Encoding', '')):
                    body = decompress(self.rfile.read(int(length))).decode('utf-8')
                else:
                    body = self.rfile.read(int(length)).decode('utf-8')
            except:
                logger.warning('Failed to decode/parse body, ignoring')
                body = None
        #
        if body is not None and body:
            try:
                payload = loads(body)
            except:
                logger.error("Failed to json.loads payload")
            return payload
        return body

    def __send_resp(self, code, payload=None):  # todo: deflate large body
        self.send_response(code)
        try:
            if payload is None:
                self.send_header('Content-Length', 0)
                self.end_headers()
            else:
                payload = dumps(payload).encode('utf-8')
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', len(payload))
                self.end_headers()
                self.wfile.write(payload)
        except:
            logger.error("Failed to send_resp, client closed connection?")
        return code

    def __path_arg(self, num):
        try:
            args = self.path.split('/')
            return parse.unquote(args[num])
        except:
            pass
        return None

    def __xrange(self):
        limit = None
        offset = None
        if 'X-Range' in self.headers:
            try:
                limit = int(self.headers['X-Range'].split('/')[1])
                offset = int(self.headers['X-Range'].split('/')[0])
            except:
                pass
        return limit, offset

    def __xlang(self):
        if 'X-Language' in self.headers:
            return self.headers['X-Language']
        return None

    def __str_to_foc(self):
        # todo: Things named feed with a control etc?
        if 'feed' in self.path.lower():
            return IoticAgentCore.Const.R_FEED
        elif 'control' in self.path.lower():
            return IoticAgentCore.Const.R_CONTROL
        return None

    def __get_epid_headers(self):
        epId = self.headers['epId']
        if epId is None:
            epId = self.headers['EpId']
        if epId is None:
            epId = self.headers['epid']
        authToken = self.headers['authToken']
        if authToken is None:
            authToken = self.headers['AuthToken']
        return epId, authToken

    def _qapi_call(self, func, *args, **kwargs):  # noqa (complexity)
        try:
            epId, authToken = self.__get_epid_headers()
            evt = func(epId, authToken, *args, **kwargs)
            evt.wait(self.timeout)
            if evt.is_set():
                mtype = IoticAgentCore.Const.E_FAILED
                if evt.success:
                    mtype = IoticAgentCore.Const.E_COMPLETE
                payload = evt.payload
                for em in evt._messages:
                    crud = [IoticAgentCore.Const.E_CREATED,
                            IoticAgentCore.Const.E_DUPLICATED,
                            IoticAgentCore.Const.E_RENAMED,
                            IoticAgentCore.Const.E_DELETED,
                            IoticAgentCore.Const.E_REASSIGNED]
                    if evt.is_crud and em[IoticAgentCore.Const.M_TYPE] in crud:
                        mtype = em[IoticAgentCore.Const.M_TYPE]
                        payload = em[IoticAgentCore.Const.M_PAYLOAD]
                        break
                    elif em[IoticAgentCore.Const.M_TYPE] == IoticAgentCore.Const.E_RECENTDATA:
                        if payload is None:
                            payload = {'samples': []}
                        if 'samples' in em[IoticAgentCore.Const.M_PAYLOAD]:
                            for sample in em[IoticAgentCore.Const.M_PAYLOAD]['samples']:
                                data, mime = self.__bytes_to_share_data(sample)
                                payload['samples'].append({'data': data, 'mime': mime, 'time': sample['time']})
                        else:
                            logger.warning("Message type E_RECENTDATA but no samples?")
                if payload and 'samples' in payload:
                    # If recent data then ensure no bytes left in payload before __send_resp!
                    payload['samples'] = self.__data_payload_to_b64(payload['samples'])
                code = 200  # sync' request OK
                if mtype == IoticAgentCore.Const.E_CREATED:
                    code = 201
                elif mtype == IoticAgentCore.Const.E_DELETED:
                    code = 204
                return self.__send_resp(code, {IoticAgentCore.Const.M_PAYLOAD: payload,
                                               IoticAgentCore.Const.M_TYPE: mtype})
            else:
                logger.warning("IoticAgent request timeout!")
                return self.__send_resp(500, {'error': 'request timeout'})
        except KeyError:
            return self.__send_resp(403, {'error': 'no such epId'})
        except ValueError as exc:
            return self.__send_resp(400, {'error': 'malformed', 'message': str(exc)})
        except LinkException as exc:
            logger.exception("IoticAgent linkerror")
            return self.__send_resp(500, {'error': 'linkerror', 'message': str(exc)})
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("IoticAgent Exception")
            return self.__send_resp(500, {'error': 'internal error', 'message': str(exc)})

    @classmethod
    def __bytes_to_share_data(cls, payload):
        """Attempt to auto-decode data"""
        rbytes = payload['data']
        mime = payload['mime']

        if mime is None:
            return rbytes, mime
        mime = expand_idx_mimetype(mime).lower()
        try:
            if mime == 'application/ubjson':
                return ubjloadb(rbytes), None
            elif mime == 'text/plain; charset=utf8':
                return rbytes.decode('utf-8'), None
            else:
                return rbytes, mime
        except:
            logger.warning('auto-decode failed, returning bytes')
            return rbytes, mime

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Allow', 'GET,PUT,DELETE,POST,OPTIONS')
        self.send_header('Content-Length', 0)
        self.end_headers()

    def do_POST(self):  # pylint: disable=too-many-return-statements
        payload = self._read_body()
        self.__log('POST', self.path, self.headers, payload)
        #
        lang = self.__xlang()
        limit, offset = self.__xrange()
        if payload is None:
            return self.__send_resp(410, {'error': 'empty payload or could not decode'})
        elif self.path.startswith('/entity'):
            return self.__do_POST_entity(payload, lang)
        elif self.path.startswith('/point'):
            return self.__do_POST_point(payload, lang)
        elif self.path.startswith('/value'):
            foc = self.__str_to_foc()
            lid = self.__path_arg(3)
            pid = self.__path_arg(4)
            return self._qapi_call(
                self.__qapiManager.request_point_value_create,
                lid,
                pid,
                foc,
                payload['label'] if 'label' in payload else '',
                payload['vtype'] if 'vtype' in payload else '',
                payload['lang'] if 'lang' in payload else None,
                payload['comment'] if 'comment' in payload else None,
                payload['unit'] if 'unit' in payload else None)
        elif self.path.startswith('/sub'):
            return self.__do_POST_sub(payload)
        elif self.path.startswith('/search'):
            return self._qapi_call(
                self.__qapiManager.request_search,
                text=payload['text'] if 'text' in payload else None,
                lang=payload['lang'] if 'lang' in payload else None,
                location=payload['location'] if 'location' in payload else None,
                unit=payload['unit'] if 'unit' in payload else None,
                type_=payload['type'] if 'type' in payload else 'full',
                scope=IoticAgentCore.Const.SearchScope(payload.get('scope', IoticAgentCore.Const.SearchScope.PUBLIC)),
                limit=limit,
                offset=offset)
        elif self.path.startswith('/describe'):
            return self._qapi_call(
                self.__qapiManager.request_describe,
                payload['guid'] if 'guid' in payload else '',
                scope=IoticAgentCore.Const.DescribeScope(payload.get('scope', IoticAgentCore.Const.DescribeScope.AUTO)))
        else:
            return self.__send_resp(405, {'error': 'invalid resource'})

    def __do_POST_entity(self, payload, lang):
        if self.path == '/entity':
            return self._qapi_call(
                self.__qapiManager.request_entity_create,
                payload['lid'] if 'lid' in payload else None,
                tepid=payload['epId'] if 'epId' in payload else None)
        elif self.path.endswith('/tag'):
            lid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_entity_tag_update,
                lid,
                payload['tags'] if 'tags' in payload else [])
        elif self.path.endswith('tag/metahelper'):
            if lang is None:
                return self.__send_resp(400, {'error': 'X-Language must be specified for metahelper functions'})
            epId, authToken = self.__get_epid_headers()
            lid = self.__path_arg(2)
            code, resp = RDFHelper.add_meta_entity_tags(self.__qapiManager,
                                                        epId,
                                                        authToken,
                                                        lid,
                                                        payload['tags'] if 'tags' in payload else [])
            return self.__send_resp(code, resp)
        #
        else:
            return self.__send_resp(400, {'error': 'malformed'})

    def __do_POST_point(self, payload, lang):
        foc = self.__str_to_foc()
        if self.path.endswith('/tag'):
            lid = self.__path_arg(3)
            pid = self.__path_arg(4)
            return self._qapi_call(
                self.__qapiManager.request_point_tag_update,
                foc,
                lid,
                pid,
                payload['tags'] if 'tags' in payload else '')
        elif self.path.endswith('/share'):
            lid = self.__path_arg(2)
            pid = self.__path_arg(3)
            return self._qapi_call(
                self.__qapiManager.request_point_share,
                lid,
                pid,
                payload['data'] if 'data' in payload else '',
                payload['mime'] if 'mime' in payload else None)
        elif self.path.endswith('tag/metahelper'):
            if lang is None:
                return self.__send_resp(400, {'error': 'X-Language must be specified for metahelper functions'})
            epId, authToken = self.__get_epid_headers()
            lid = self.__path_arg(3)
            pid = self.__path_arg(4)
            code, resp = RDFHelper.add_meta_point_tags(self.__qapiManager,
                                                       epId,
                                                       authToken,
                                                       foc,
                                                       lid,
                                                       pid,
                                                       payload['tags'] if 'tags' in payload else [])
            return self.__send_resp(code, resp)
        #
        else:
            return self._qapi_call(
                self.__qapiManager.request_point_create,
                foc,
                payload['lid'] if 'lid' in payload else '',
                payload['pid'] if 'pid' in payload else '',
                save_recent=payload['saveRecent'] if 'saveRecent' in payload else 0)

    def __do_POST_sub(self, payload):
        foc = self.__str_to_foc()
        lid = self.__path_arg(3)
        if self.path.endswith('/ask'):
            subid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_sub_ask,
                subid,
                payload['data'] if 'data' in payload else '',
                payload['mime'] if 'mime' in payload else None)
        elif self.path.endswith('/tell'):
            subid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_sub_tell,
                subid,
                payload['data'] if 'data' in payload else '',
                payload['mime'] if 'mime' in payload else None)
        elif 'gpid' in payload:
            return self._qapi_call(
                self.__qapiManager.request_sub_create,
                lid,
                foc,
                payload['gpid'])
        elif 'slid' in payload:
            pid = self.__path_arg(4)
            return self._qapi_call(
                self.__qapiManager.request_sub_create_local,
                payload['slid'],
                foc,
                lid,
                pid)
        else:
            return self.__send_resp(400, {'error': 'malformed'})

    def do_GET(self):  # pylint: disable=too-many-return-statements
        payload = self._read_body()
        self.__log('GET', self.path, self.headers, payload)
        #
        lang = self.__xlang()
        limit, offset = self.__xrange()
        #
        if self.path.startswith('/entity'):
            return self.__do_GET_entity(lang, limit, offset)
        elif self.path.startswith('/point'):
            return self.__do_GET_point(lang, limit, offset)
        elif self.path.startswith('/value'):
            foc = self.__str_to_foc()
            lid = self.__path_arg(3)
            pid = self.__path_arg(4)
            return self._qapi_call(
                self.__qapiManager.request_point_value_list,
                lid,
                pid,
                foc,
                limit=limit,
                offset=offset)
        elif self.path.startswith('/sub'):
            return self.__do_GET_sub(limit, offset)
        elif self.path == '/feeddata':
            return self.__send_resp(200, self.__data_payload_to_b64(
                self.__qapiManager.get_feeddata(self.headers['epId'], self.headers['authToken'])))
        elif self.path == '/controlreq':
            return self.__send_resp(200, self.__data_payload_to_b64(
                self.__qapiManager.get_controlreq(self.headers['epId'], self.headers['authToken'])))
        elif self.path == '/unsolicited':
            return self.__send_resp(200, self.__data_payload_to_b64(
                self.__qapiManager.get_unsolicited(self.headers['epId'], self.headers['authToken'])))
        else:
            return self.__send_resp(405, {'error': 'invalid resource'})

    def __data_payload_to_b64(self, datalist):
        ret = []
        for row in datalist:
            if isinstance(row['data'], bytes):
                row['data'] = 'base64/' + b64encode(row['data']).decode('ascii')
            elif isinstance(row['data'], dict):
                row['data'] = self.__dict_to_b64(row['data'])
            elif isinstance(row['data'], list):
                # todo: data payload can be list ?
                row['data'] = self.__list_to_b64(row['data'])
            ret.append(row)
        return ret

    def __dict_to_b64(self, data):
        ret = {}
        for key, value in data.items():
            if isinstance(value, bytes):
                value = "base64/" + b64encode(value).decode('ascii')
            elif isinstance(value, dict):
                value = self.__dict_to_b64(value)
            elif isinstance(value, list):
                value = self.__list_to_b64(value)
            ret[key] = value
        return ret

    def __list_to_b64(self, data):
        ret = []
        for value in data:
            if isinstance(value, dict):
                value = self.__dict_to_b64(value)
            elif isinstance(value, list):
                value = self.__list_to_b64(value)
            elif isinstance(value, bytes):
                value = "base64/" + b64encode(value).decode('ascii')
            ret.append(value)
        return ret

    def __do_GET_entity(self, lang, limit, offset):  # pylint: disable=too-many-return-statements
        if self.path == '/entity':
            return self._qapi_call(
                self.__qapiManager.request_entity_list,
                limit=limit,
                offset=offset)
        elif self.path.endswith('/all'):
            return self._qapi_call(
                self.__qapiManager.request_entity_list_all,
                limit=limit,
                offset=offset)
        elif self.path.endswith('/meta'):
            lid = self.__path_arg(2)
            fmt = self.__path_arg(3)
            if fmt == 'meta':
                fmt = 'n3'
            return self._qapi_call(
                self.__qapiManager.request_entity_meta_get,
                lid,
                fmt)
        elif self.path.endswith('/tag'):
            lid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_entity_tag_list,
                lid,
                limit=limit,
                offset=offset)
        elif self.path.endswith('tag/metahelper'):
            if lang is None:
                return self.__send_resp(400, {'error': 'X-Language must be specified for metahelper functions'})
            epId, authToken = self.__get_epid_headers()
            lid = self.__path_arg(2)
            code, resp = RDFHelper.get_meta_entity_tags(self.__qapiManager, epId, authToken, lid, limit=limit,
                                                        offset=offset)
            return self.__send_resp(code, resp)
        elif self.path.endswith('/metahelper'):
            if lang is None:
                return self.__send_resp(400, {'error': 'X-Language must be specified for metahelper functions'})
            epId, authToken = self.__get_epid_headers()
            lid = self.__path_arg(2)
            code, resp = RDFHelper.get_meta_entity(self.__qapiManager, epId, authToken, lid, lang)
            return self.__send_resp(code, resp)
        #
        else:
            return self.__send_resp(400, {'error': 'malformed'})

    def __do_GET_point(self, lang, limit, offset):
        foc = self.__str_to_foc()
        lid = self.__path_arg(3)
        pid = self.__path_arg(4)
        if self.path.endswith('/meta'):
            fmt = self.__path_arg(5)
            return self._qapi_call(
                self.__qapiManager.request_point_meta_get,
                foc,
                lid,
                pid,
                fmt)
        elif self.path.endswith('/tag'):
            return self._qapi_call(
                self.__qapiManager.request_point_tag_list,
                foc,
                lid,
                pid,
                limit=limit,
                offset=offset)
        elif self.path.endswith('tag/metahelper'):
            epId, authToken = self.__get_epid_headers()
            code, resp = RDFHelper.get_meta_point_tags(self.__qapiManager,
                                                       epId,
                                                       authToken,
                                                       foc,
                                                       lid,
                                                       pid,
                                                       limit=limit,
                                                       offset=offset)
            return self.__send_resp(code, resp)
        elif self.path.endswith('/metahelper'):
            if lang is None:
                return self.__send_resp(400, {'error': 'X-Language must be specified for metahelper functions'})
            epId, authToken = self.__get_epid_headers()
            code, resp = RDFHelper.get_meta_point(self.__qapiManager, epId, authToken, foc, lid, pid, lang)
            return self.__send_resp(code, resp)
        #
        else:
            if pid is not None:
                return self._qapi_call(
                    self.__qapiManager.request_point_list_detailed,
                    foc,
                    lid,
                    pid)
            else:
                return self._qapi_call(
                    self.__qapiManager.request_point_list,
                    foc,
                    lid,
                    limit=limit,
                    offset=offset)

    def __do_GET_sub(self, limit, offset):
        if self.path.endswith('/recent'):
            sub_id = self.__path_arg(2)
            count = self.__path_arg(3)
            if count == 'recent':
                count = None
            else:
                try:
                    count = int(count)
                except ValueError:
                    count = None
            return self._qapi_call(
                self.__qapiManager.request_sub_recent,
                sub_id,
                count=count)
        else:
            lid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_sub_list,
                lid,
                limit=limit,
                offset=offset)

    def do_PUT(self):
        payload = self._read_body()
        self.__log('PUT', self.path, self.headers, payload)
        lang = self.__xlang()
        #
        if payload is None:
            return self.__send_resp(410, {'error': 'empty payload or could not decode'})
        #
        elif self.path.startswith('/entity'):
            return self.__do_PUT_entity(payload, lang)
        elif self.path.startswith('/point'):
            return self.__do_PUT_point(payload, lang)
        else:
            return self.__send_resp(405, {'error': 'invalid resource'})

    def __do_PUT_entity(self, payload, lang):
        if self.path.endswith('/rename') and 'newlid' in payload:
            lid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_entity_rename,
                lid,
                payload['newlid'])
        elif self.path.endswith('/reassign') and 'epId' in payload:
            lid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_entity_reassign,
                lid,
                payload['epId'])
        elif self.path.endswith('/meta') and 'meta' in payload:
            lid = self.__path_arg(2)
            fmt = self.__path_arg(3)
            return self._qapi_call(
                self.__qapiManager.request_entity_meta_set,
                lid,
                payload['meta'],
                fmt)
        elif self.path.endswith('/setpublic') and 'public' in payload:
            lid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_entity_meta_setpublic,
                lid,
                payload['public'])
        elif self.path.endswith('/metahelper'):
            if lang is None:
                return self.__send_resp(400, {'error': 'X-Language must be specified for metahelper functions'})
            epId, authToken = self.__get_epid_headers()
            lid = self.__path_arg(2)
            code, resp = RDFHelper.set_meta_entity(self.__qapiManager, epId, authToken, lid, payload, lang)
            return self.__send_resp(code, resp)
        #
        else:
            return self.__send_resp(400, {'error': 'malformed'})

    def __do_PUT_point(self, payload, lang):
        foc = self.__str_to_foc()
        lid = self.__path_arg(3)
        pid = self.__path_arg(4)
        if self.path.endswith('/rename'):
            return self._qapi_call(
                self.__qapiManager.request_point_rename,
                foc,
                lid,
                pid,
                payload['newpid'] if 'newpid' in payload else '')
        elif self.path.endswith('/meta'):
            fmt = self.__path_arg(5)
            return self._qapi_call(
                self.__qapiManager.request_point_meta_set,
                foc,
                lid,
                pid,
                payload['meta'] if 'meta' in payload else '',
                fmt)
        elif self.path.endswith('/metahelper'):
            if lang is None:
                return self.__send_resp(400, {'error': 'X-Language must be specified for metahelper functions'})
            epId, authToken = self.__get_epid_headers()
            code, resp = RDFHelper.set_meta_point(self.__qapiManager, epId, authToken, foc, lid, pid, payload, lang)
            return self.__send_resp(code, resp)
        #
        else:
            return self.__send_resp(400, {'error': 'malformed'})

    def do_DELETE(self):  # noqa (complexity) # pylint: disable=too-many-branches
        payload = self._read_body()
        self.__log('DELETE', self.path, self.headers, payload)
        #
        if self.path.startswith('/entity'):
            return self.__do_DELETE_entity(payload)
        elif self.path.startswith('/point'):
            return self.__do_DELETE_point(payload)
        elif self.path.startswith('/value'):
            foc = self.__str_to_foc()
            lid = self.__path_arg(3)
            pid = self.__path_arg(4)
            label = self.__path_arg(5)
            return self._qapi_call(
                self.__qapiManager.request_point_value_delete,
                lid,
                pid,
                foc,
                label)
        elif self.path.startswith('/sub'):
            subid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_sub_delete,
                subid)
        else:
            return self.__send_resp(405, {'error': 'invalid resource'})

    def __do_DELETE_entity(self, payload):
        if self.path.endswith('/tag'):
            lid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_entity_tag_update,
                lid,
                payload['tags'] if 'tags' in payload else [],
                delete=True)
        elif self.path.endswith('tag/metahelper'):
            epId, authToken = self.__get_epid_headers()
            lid = self.__path_arg(2)
            code, resp = RDFHelper.del_meta_entity_tags(self.__qapiManager,
                                                        epId,
                                                        authToken,
                                                        lid,
                                                        payload['tags'] if 'tags' in payload else [])
            return self.__send_resp(code, resp)
        #
        else:
            lid = self.__path_arg(2)
            return self._qapi_call(
                self.__qapiManager.request_entity_delete,
                lid)

    def __do_DELETE_point(self, payload):
        foc = self.__str_to_foc()
        lid = self.__path_arg(3)
        pid = self.__path_arg(4)
        if self.path.endswith('/tag'):
            if payload is not None:
                return self._qapi_call(
                    self.__qapiManager.request_point_tag_update,
                    foc,
                    lid,
                    pid,
                    payload['tags'] if 'tags' in payload else '',
                    delete=True)
            else:
                return self.__send_resp(400, {'error': 'malformed'})
        elif self.path.endswith('tag/metahelper'):
            epId, authToken = self.__get_epid_headers()
            code, resp = RDFHelper.del_meta_point_tags(self.__qapiManager,
                                                       epId,
                                                       authToken,
                                                       foc,
                                                       lid,
                                                       pid,
                                                       payload['tags'] if 'tags' in payload else [])
            return self.__send_resp(code, resp)
        #
        else:
            return self._qapi_call(
                self.__qapiManager.request_point_delete,
                foc,
                lid,
                pid)


def getSSLContext(capath, crtpath, keypath, keypass=None):
    ctx = SSLContext(PROTOCOL_TLSv1_2)
    ctx.set_ciphers('HIGH:!SSLv3:!TLSv1:!aNULL:@STRENGTH')
    # client certificate is required
    ctx.verify_mode = CERT_REQUIRED
    ctx.options |= OP_NO_COMPRESSION
    ctx.load_verify_locations(capath)
    ctx.load_cert_chain(crtpath, keypath, password=keypass)
    return ctx


def setupServer(hostaddr, capath, crtpath, keypath, keypass, qapiManager, insecure_mode=False, custom_handler=None):
    if not insecure_mode:
        Handler.setSSLContext(getSSLContext(capath, crtpath, keypath, keypass))
    else:
        Handler.setSecureMode(False)
        logger.warning("*" * 50)
        logger.warning("*")
        logger.warning("* WARNING: SERVER RUNNING IN INSECURE MODE !!")
        logger.warning("*")
        logger.warning("*" * 50)
    Handler.setQapiManager(qapiManager)
    # server = ForkingHTTPServer(hostaddr, Handler)
    server = ThreadingHTTPServer(hostaddr, (Handler if custom_handler is None else _load_handler(custom_handler)))
    thread = Thread(target=server.serve_forever, kwargs={'poll_interval': 0.2})
    thread.start()
    logger.info('Started on %s:%s', server.server_name, server.server_port)
    return server, thread


def _load_handler(name):
    module, cls_name = name.rsplit('.', maxsplit=1)
    cls = getattr(import_module(module), cls_name)
    if not issubclass(cls, Handler):
        raise TypeError('custom_handler not subclass of Handler')
    return cls


def stopServer(server, thread):
    server.shutdown()
    thread.join()
    server.server_close()
    logger.info('Stopped')
