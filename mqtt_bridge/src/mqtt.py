#!/usr/bin/env python3
# Copyright (c) 2016 Iotic Labs Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/Iotic-Labs/py-IoticAgent/blob/master/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""mqtt: IoticAgent MQTT bridge
"""

from __future__ import unicode_literals, print_function

from functools import partial
from os import getcwd
from os.path import exists, join
from sys import exit
from json import dumps, loads
import argparse
from socket import error as ConnectionRefusedError
from IoticAgent import IOT
from IoticAgent import Core as IoticAgentCore
from IoticAgent.Core.Const import R_FEED, R_CONTROL
from IoticAgent.IOT.Exceptions import LinkException
import paho.mqtt.client as mqtt

import logging
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# MQTT Settings
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 1883

# How long to wait on IoticAgent Events
TIMEOUT = 10


def on_connect(mqttclient, userdata, flags, rcode):
    logger.info("Connected with result code: " + str(rcode))
    logger.debug("%s,%s", str(userdata), str(flags))
    mqttclient.subscribe("ioticlabs/req/#")


def _get_arg(line, arg):
    try:
        return line.split('/')[arg]
    except:
        pass


def _get_payload(payload):
    try:
        return loads(payload.decode('utf8'))
    except:
        pass


def _get_limit_offset(payload):
    limit = offset = None
    if payload is not None:
        if 'limit' in payload:
            limit = payload['limit']
            if 'offset' in payload:
                offset = payload['offset']
    return limit, offset


def _get_payload_or_none(payload, key):
    if payload is not None:
        if key in payload:
            return payload[key]
    return None


def _qapi_call(device_id, request_id, mqttclient, func, *args, **kwargs):
    # pylint: disable=too-many-nested-blocks
    try:
        evt = func(*args, **kwargs)
        try:
            evt.wait(timeout=TIMEOUT)
            if evt.is_set():
                mtype = IoticAgentCore.Const.E_FAILED
                if evt.success:
                    mtype = IoticAgentCore.Const.E_COMPLETE
                payload = evt.payload
                if evt.is_crud:
                    for msg in evt._messages:
                        crud = [IoticAgentCore.Const.E_CREATED,
                                IoticAgentCore.Const.E_DUPLICATED,
                                IoticAgentCore.Const.E_RENAMED,
                                IoticAgentCore.Const.E_DELETED,
                                IoticAgentCore.Const.E_REASSIGNED]
                        if msg[IoticAgentCore.Const.M_TYPE] in crud:
                            mtype = msg[IoticAgentCore.Const.M_TYPE]
                            payload = msg[IoticAgentCore.Const.M_PAYLOAD]
                            break
                code = 200  # sync' request OK
                if mtype == IoticAgentCore.Const.E_CREATED:
                    code = 201
                elif mtype == IoticAgentCore.Const.E_DELETED:
                    code = 204
                return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                                 {'code': code,
                                  IoticAgentCore.Const.M_PAYLOAD: payload,
                                  IoticAgentCore.Const.M_TYPE: mtype})
            else:
                logger.warning("IoticAgent request timeout! %s/%s", device_id, request_id)
                return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                                 {'code': 500,
                                  'error': 'timeout',
                                  'message': 'IoticAgent request timeout'})
        except AttributeError:
            # Note: work around for mixing IOT.Client functions with Core.Client functions !!
            # e.g: IOT.Client_request_entity_list returned empty entities
            return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                             {'code': 200,
                              IoticAgentCore.Const.M_PAYLOAD: evt,
                              IoticAgentCore.Const.M_TYPE: IoticAgentCore.Const.E_COMPLETE})
    except ValueError as exc:
        return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                         {'code': 400, 'error': 'malformed', 'message': str(exc)})
    except LinkException as exc:
        logger.exception("IoticAgent linkerror")
        return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                         {'code': 500, 'error': 'linkerror', 'message': str(exc)})
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("IoticAgent Exception")
        return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                         {'code': 500, 'error': 'internal error', 'message': str(exc)})


def _mqtt_pub(mqttclient, topic, payload):
    if payload is not None:
        payload = dumps(payload)
    logger.info("_mqtt_pub: %s / %s", 'ioticlabs/' + topic, str(payload))
    return mqttclient.publish('ioticlabs/' + topic, payload)


def _do_create_entity(client, mqttclient, userdata, msg, device_id, request_id, payload):
    # pylint: disable=unused-argument
    lang = _get_payload_or_none(payload, 'lang')
    if _get_arg(msg.topic, 6) is None:
        if 'lid' in payload:
            return _qapi_call(device_id, request_id, mqttclient, client._request_entity_create, payload['lid'])
        else:
            return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                             {'code': 400,
                              'error': 'malformed',
                              'message': 'lid required in payload'})
    elif _get_arg(msg.topic, 7) == 'tag':
        if 'tags' in payload:
            lid = _get_arg(msg.topic, 6)
            return _qapi_call(device_id, request_id, mqttclient, client._request_entity_tag_create,
                              lid, payload['tags'], lang=lang)
        else:
            return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                             {'code': 400,
                              'error': 'malformed',
                              'message': 'tags list required in payload'})
    else:
        return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                         {'code': 400, 'error': 'malformed', 'message': ' '})


def _do_create_point(client, mqttclient, userdata, msg, device_id, request_id, payload):
    # pylint: disable=unused-argument
    foc = None
    if _get_arg(msg.topic, 6) == "feed":
        foc = R_FEED
    elif _get_arg(msg.topic, 6) == "control":
        foc = R_CONTROL
    if foc is not None and 'lid' in payload and 'pid' in payload:
        return _qapi_call(device_id, request_id, mqttclient, client._request_point_create,
                          R_FEED, payload['lid'], payload['pid'])
    else:
        return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                         {'code': 400,
                          'error': 'malformed',
                          'message': 'lid and pid required in payload'})


def _do_list_entity(client, mqttclient, userdata, msg, device_id, request_id, payload):
    # pylint: disable=unused-argument
    limit, offset = _get_limit_offset(payload)
    if _get_arg(msg.topic, 6) is None:
        return _qapi_call(device_id, request_id, mqttclient, client.list)
    elif _get_arg(msg.topic, 6) == 'all' and _get_arg(msg.topic, 7) is None:
        return _qapi_call(device_id, request_id, mqttclient, client.list, all_my_agents=True)
    elif _get_arg(msg.topic, 8) is None and _get_arg(msg.topic, 7) == 'tag':
        lid = _get_arg(msg.topic, 6)
        return _qapi_call(device_id, request_id, mqttclient, client._request_entity_tag_list,
                          lid, limit, offset)
    elif _get_arg(msg.topic, 8) == 'meta':
        lid = _get_arg(msg.topic, 6)
        fmt = _get_arg(msg.topic, 7)
        return _qapi_call(device_id, request_id, mqttclient, client._request_entity_meta_get, lid, fmt)


def _do_update_entity(client, mqttclient, userdata, msg, device_id, request_id, payload):
    # pylint: disable=unused-argument
    lid = _get_arg(msg.topic, 6)
    if lid is not None:
        if _get_arg(msg.topic, 8) == 'meta':
            fmt = _get_arg(msg.topic, 7)
            return _qapi_call(device_id, request_id, mqttclient, client._request_entity_meta_set,
                              lid, payload['meta'], fmt)
        elif _get_arg(msg.topic, 7) == 'rename':
            return _qapi_call(device_id, request_id, mqttclient, client._request_entity_rename,
                              lid, payload['newlid'])
        elif _get_arg(msg.topic, 7) == 'reassign':
            return _qapi_call(device_id, request_id, mqttclient, client._request_entity_reassign,
                              lid, payload['epId'])
        elif _get_arg(msg.topic, 7) == 'setpublic':
            return _qapi_call(device_id, request_id, mqttclient, client._request_entity_meta_setpublic,
                              lid, public=payload['public'])
    else:
        return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                         {'code': 400,
                          'error': 'malformed',
                          'message': 'lid required on topic'})


def _do_update_point(client, mqttclient, userdata, msg, device_id, request_id, payload):
    # pylint: disable=unused-argument
    """Note: Payload can be dictionary or dict or {'data': dict or bytes, 'mime': optional, 'time': optional}"""
    if _get_arg(msg.topic, 8) == 'share':
        lid = _get_arg(msg.topic, 6)
        pid = _get_arg(msg.topic, 7)
        mime = None
        time = None
        data = payload
        if 'data' in payload:
            data = payload['data']
        if 'mime' in payload:
            mime = payload['mime']
        if 'time' in payload:
            time = payload['time']
        return _qapi_call(device_id, request_id, mqttclient, client._request_point_share,
                          lid, pid, data, mime, time)


def _do_delete_entity(client, mqttclient, userdata, msg, device_id, request_id, payload):
    # pylint: disable=unused-argument
    lang = _get_payload_or_none(payload, 'lang')
    lid = _get_arg(msg.topic, 6)
    if lid is not None:
        if _get_arg(msg.topic, 8) is None and _get_arg(msg.topic, 7) == 'tag':
            if 'tags' in payload:
                return _qapi_call(device_id, request_id, mqttclient, client._request_entity_tag_delete,
                                  lid, payload['tags'], lang)
            else:
                return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                                 {'code': 400,
                                  'error': 'malformed',
                                  'message': 'tags list required in payload'})
        else:
            return _qapi_call(device_id, request_id, mqttclient, client._request_entity_delete, lid)
    else:
        return _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                         {'code': 400,
                          'error': 'malformed',
                          'message': 'lid required on topic'})


def on_message(client, mqttclient, userdata, msg):  # pylint: disable=too-many-branches
    """on_message: Topics follow the qapi proxy api
    ioticlabs/req/  prefix
    device id free text for device
    request id free text unique ID of this request
    create or update or delete or list (maps to POST, PUT, DELETE, GET)
    url same as qapiproxy
    payload same as qapoproxy

    EG ioticlabs/req/bbq/11/create/entity {'lid': 'fish'}
    EG ioticlabs/req/bbq/12/update/entity/<lid>/rename {'newlid': 'chips'}

    The request id must be unique (or atleast not currently in use)

    Responses get the prefix ioticlabs/rsp/ <device id> / <request id> {payload}

    Unsolicited messages
    ioticlabs/feeddata or controlreq or subscription
    feedid or controlid or subsciption id

    EG ioticlabs/feeddata/feedid {payload}
    EG ioticlabs/controlreq/lib/pid {payload}

    All response payloads contain {'code': same as qapiproxy
    if 2** then 'p' and 't' will be set
    if not 2** then 'error' and 'message' will be set
    """
    logger.info("on_message: %s / %s", msg.topic, msg.payload)
    if msg.topic.startswith("ioticlabs/req/"):
        device_id = _get_arg(msg.topic, 2)
        request_id = _get_arg(msg.topic, 3)
        if device_id is not None and request_id is not None:
            payload = _get_payload(msg.payload)
            if _get_arg(msg.topic, 4) == "create":
                if _get_arg(msg.topic, 5) == "entity":
                    return _do_create_entity(client, mqttclient, userdata, msg, device_id, request_id, payload)
                elif _get_arg(msg.topic, 5) == "point":
                    return _do_create_point(client, mqttclient, userdata, msg, device_id, request_id, payload)
            elif _get_arg(msg.topic, 4) == "list":
                if _get_arg(msg.topic, 5) == "entity":
                    return _do_list_entity(client, mqttclient, userdata, msg, device_id, request_id, payload)
            elif _get_arg(msg.topic, 4) == "update":
                if _get_arg(msg.topic, 5) == "entity":
                    return _do_update_entity(client, mqttclient, userdata, msg, device_id, request_id, payload)
                elif _get_arg(msg.topic, 5) == 'point':
                    return _do_update_point(client, mqttclient, userdata, msg, device_id, request_id, payload)
            elif _get_arg(msg.topic, 4) == "delete":
                if _get_arg(msg.topic, 5) == "entity":
                    return _do_delete_entity(client, mqttclient, userdata, msg, device_id, request_id, payload)
            else:
                logger.warning("Unrecognised topic: %s", msg.topic)
                _mqtt_pub(mqttclient, 'rsp/%s/%s' % (device_id, request_id),
                          {'code': 400,
                           'error': 'malformed',
                           'message': 'unknown topic'})
        else:
            logger.warning("Unrecognised topic: %s", msg.topic)


def catchall_feeddata(mqttclient, data):
    try:
        # print(data)
        _mqtt_pub(mqttclient, "feeddata/" + data['pid'], data)
    except:
        logger.exception("catchall_feeddata caught exception")


def catchall_controlreq(mqttclient, data):
    try:
        _mqtt_pub(mqttclient, "controlreq/%s/%s" % (data['entityLid'], data['lid']), data)
    except:
        logger.exception("catchall_controlreq caught exception")


def catchall_subscription(mqttclient, data):
    # pylint: disable=unused-argument
    pass


def main():
    # Get command args
    parser = argparse.ArgumentParser()
    parser.add_argument("cfg", nargs="?")
    args = parser.parse_args()
    cfg = args.cfg
    if cfg is not None and not exists(cfg):
        print("Config file not found: %s" % cfg)
        return 1
    elif exists(join(getcwd(), "mqtt.ini")):
        cfg = join(getcwd(), "mqtt.ini")
    if cfg is None:
        print("Usage: mqtt.py config.ini (else ./mqtt.ini will be used)")
        return 1

    # Load config from file
    host = DEFAULT_HOST
    port = DEFAULT_PORT

    config = IOT.Config.Config(fn=cfg)
    if config.get('mqtt', 'host') is not None:
        host = config.get('mqtt', 'host')
    if config.get('mqtt', 'port') is not None:
        try:
            port = int(config.get('mqtt', 'port'))
        except:
            logger.error("Unable to parse config [mqtt] port, using default.")

    # Connect agent and mqtt and loop forever
    try:
        client = IOT.Client(config=cfg)
        mqttclient = mqtt.Client()
        mqttclient.on_connect = on_connect
        mqttclient.on_message = partial(on_message, client)
        client.register_catchall_feeddata(partial(catchall_feeddata, mqttclient))
        client.register_catchall_controlreq(partial(catchall_controlreq, mqttclient))
        client.register_callback_subscription(partial(catchall_subscription, mqttclient))
        with client:
            logger.info("Agent connected: %s", client.agent_id)
            try:
                mqttclient.connect(host, port)
                logger.info("MQTT connected.  Press ctrl+c to quit.")
                mqttclient.loop_forever()
            except ConnectionRefusedError:
                logger.error("MQTT Connection Refused.  Give up.")
            except KeyboardInterrupt:
                pass
            except:
                logger.exception("todo: unhandled mqtt exception?")
    except LinkException:
        print("Failed to connect")
        return 1
    except KeyboardInterrupt:
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
