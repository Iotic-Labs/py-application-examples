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

import IoticAgent.Core
from IoticAgent.IOT.ThingMeta import ThingMeta
from IoticAgent.IOT.PointMeta import PointMeta

from rdflib.plugins.parsers.notation3 import BadSyntax


def __exception_response(code, message):
    ret = {}
    ret['t'] = IoticAgent.Core.Const.E_FAILED
    ret['p'] = {'m': message}
    return code, ret


def __good_response_null(code, resp_type):
    ret = {}
    ret['t'] = resp_type
    ret['p'] = None

    return code, ret


def __good_response_tag(code, resp_type, taglist):
    ret = {}
    ret['t'] = resp_type
    ret['p'] = {}

    #  taglist is an OrderedDict([('tags', ['fish', 'hello'])])
    try:
        ret['p']['tags'] = taglist['tags']
    except KeyError:
        ret['p']['tags'] = []

    return code, ret


def __good_response_metaobj(code, resp_type, metaobj, lang):
    ret = {}
    ret['t'] = resp_type
    ret['p'] = {}

    ret['p']['label'] = None
    labels = metaobj.get_labels_rdf()
    for label in labels:
        if label.language == lang:
            ret['p']['label'] = label.value

    ret['p']['description'] = None
    descriptions = metaobj.get_descriptions_rdf()
    for description in descriptions:
        if description.language == lang:
            ret['p']['description'] = description.value

    if isinstance(metaobj, ThingMeta):
        ret['p']['lat'], ret['p']['lon'] = metaobj.get_location()

    return code, ret


def get_meta_entity(qapimanager, epid, authtoken, lid, lang):
    logger.info("get_meta_entity: lid = %s", lid)
    if lang is None:
        lang = qapimanager.default_lang(epid, authtoken)
    evt = qapimanager.request_entity_meta_get(epid, authtoken, lid, fmt='n3')
    evt.wait(timeout=20)
    if evt.success:
        try:
            meta = ThingMeta(None, evt.payload["meta"], lang)
        except BadSyntax as exc:
            return __exception_response(500, exc)
        return __good_response_metaobj(200, IoticAgent.Core.Const.E_COMPLETE, meta, lang)
    else:
        return __exception_response(400, "Failed to get metadata for entity {lid}".format(lid=lid))


def get_meta_entity_tags(qapimanager, epid, authtoken, lid, limit=100, offset=0):
    logger.info("get_meta_entity_tags: lid = %s", lid)
    evt = qapimanager.request_entity_tag_list(epid, authtoken, lid, limit=limit, offset=offset)
    evt.wait(timeout=20)
    if evt.success:
        return __good_response_tag(200, IoticAgent.Core.Const.E_COMPLETE, evt.payload)
    else:
        return __exception_response(400, "Failed to get tags for entity {lid}".format(lid=lid))


def get_meta_point(qapimanager, epid, authtoken, foc, lid, pid, lang):
    logger.info("get_meta_point: lid = %s, pid = %s, foc = %s", lid, pid, foc)
    if lang is None:
        lang = qapimanager.default_lang(epid, authtoken)
    evt = qapimanager.request_point_meta_get(epid, authtoken, foc, lid, pid, fmt='n3')
    evt.wait(timeout=20)
    if evt.success:
        try:
            meta = PointMeta(None, evt.payload["meta"], lang)
        except BadSyntax as exc:
            return __exception_response(500, exc)
        return __good_response_metaobj(200, IoticAgent.Core.Const.E_COMPLETE, meta, lang)
    else:
        return __exception_response(400, "Failed to get meta for {foc} {lid}/{pid}".format(foc=foc, lid=lid, pid=pid))


def get_meta_point_tags(qapimanager, epid, authtoken, foc, lid, pid, limit=100, offset=0):
    logger.info("get_meta_point_tags: lid = %s pid = %s, foc = %s", lid, pid, foc)
    evt = qapimanager.request_point_tag_list(epid, authtoken, foc, lid, pid, limit=limit, offset=offset)
    evt.wait(timeout=20)
    if evt.success:
        return __good_response_tag(200, IoticAgent.Core.Const.E_COMPLETE, evt.payload)
    else:
        return __exception_response(400, "Failed to get tags for point {lid}".format(lid=lid))


def set_meta_entity(qapimanager, epid, authtoken, lid, payload, lang):  # pylint: disable=too-many-return-statements, too-many-branches
    logger.info("set_meta_entity: payload = %s", str(payload))
    if lang is None:
        lang = qapimanager.default_lang(epid, authtoken)
    evt = qapimanager.request_entity_meta_get(epid, authtoken, lid, fmt='n3')
    evt.wait(timeout=20)
    if evt.success:
        try:
            meta = ThingMeta(None, evt.payload["meta"], lang)
        except BadSyntax as exc:
            return __exception_response(500, exc)

        set_meta = False
        try:
            if 'label' in payload:
                meta.set_label(payload['label'], lang)
                set_meta = True

            if 'description' in payload:
                meta.set_description(payload['description'], lang)
                set_meta = True

            if 'lat' in payload and 'lon' not in payload:
                if 'long' in payload:
                    payload['lon'] = payload['long']

            if 'lat' in payload and 'lon' in payload:
                meta.set_location(float(payload['lat']), float(payload['lon']))
                set_meta = True
        except ValueError as exc:
            return __exception_response(400, exc)

        if set_meta:
            evt = qapimanager.request_entity_meta_set(epid, authtoken, lid, str(meta), fmt='n3')
            evt.wait(timeout=20)
            if evt.success:
                return __good_response_metaobj(200, IoticAgent.Core.Const.E_COMPLETE, meta, lang)
            else:
                return __exception_response(400, evt.message)
        else:
            return __exception_response(400, "Failed to set metadata for entity {lid} no values found".format(lid=lid))
    else:
        return __exception_response(400, "Failed to set metadata for entity {lid}".format(lid=lid))

    return 200, {}


def set_meta_point(qapimanager, epid, authtoken, foc, lid, pid, payload, lang):
    logger.info("get_meta_point: lid = %s, pid = %s, foc = %s", lid, pid, foc)
    if lang is None:
        lang = qapimanager.default_lang(epid, authtoken)
    evt = qapimanager.request_point_meta_get(epid, authtoken, foc, lid, pid, fmt='n3')
    evt.wait(timeout=20)
    if evt.success:
        try:
            meta = PointMeta(None, evt.payload["meta"], lang)
        except BadSyntax as exc:
            return __exception_response(500, exc)

        try:
            if 'label' in payload:
                meta.set_label(payload['label'], lang)

            if 'description' in payload:
                meta.set_description(payload['description'], lang)

        except ValueError as exc:
            return __exception_response(400, exc)

        evt = qapimanager.request_point_meta_set(epid, authtoken, foc, lid, pid, str(meta), fmt='n3')
        evt.wait(timeout=20)
        if evt.success:
            return __good_response_metaobj(200, IoticAgent.Core.Const.E_COMPLETE, meta, lang)
        else:
            return __exception_response(400, evt.message)
    else:
        return __exception_response(400, "Failed to set meta for {foc} {lid}/{pid}".format(foc=foc, lid=lid, pid=pid))

    return 200, {}


def add_meta_entity_tags(qapimanager, epid, authtoken, lid, tags):
    logger.info("add_meta_entity_tags: lid = %s, tags = %s", lid, str(tags))
    evt = qapimanager.request_entity_tag_update(epid, authtoken, lid, tags)
    evt.wait(timeout=20)
    if evt.success:
        return __good_response_null(201, IoticAgent.Core.Const.E_CREATED)
    else:
        return __exception_response(400, evt.message)

    return 201, {}


def add_meta_point_tags(qapimanager, epid, authtoken, foc, lid, pid, tags):
    logger.info("add_meta_point_tags: foc = %s, lid = %s, pid = %s, tags = %s",
                foc, lid, pid, str(tags))
    evt = qapimanager.request_point_tag_update(epid, authtoken, foc, lid, pid, tags)
    evt.wait(timeout=20)
    if evt.success:
        return __good_response_null(201, IoticAgent.Core.Const.E_CREATED)
    else:
        return __exception_response(400, evt.message)

    return 201, {}


def del_meta_entity_tags(qapimanager, epid, authtoken, lid, tags):
    logger.info("del_meta_entity_tags: lid = %s, tags = %s", lid, str(tags))
    evt = qapimanager.request_entity_tag_update(epid, authtoken, lid, tags, delete=True)
    evt.wait(timeout=20)
    if evt.success:
        return __good_response_null(204, IoticAgent.Core.Const.E_DELETED)
    else:
        return __exception_response(400, evt.message)

    return 200, {}


def del_meta_point_tags(qapimanager, epid, authtoken, foc, lid, pid, tags):
    logger.info("del_meta_point_tags: foc = %s, lid = %s, pid = %s, tags = %s",
                foc, lid, pid, str(tags))
    evt = qapimanager.request_point_tag_update(epid, authtoken, foc, lid, pid, tags, delete=True)
    evt.wait(timeout=20)
    if evt.success:
        return __good_response_null(204, IoticAgent.Core.Const.E_DELETED)
    else:
        return __exception_response(400, evt.message)

    return 200, {}
