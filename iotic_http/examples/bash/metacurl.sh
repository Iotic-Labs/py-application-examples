#!/usr/bin/env bash
# Copyright (c) 2016 Iotic Labs Ltd. All rights reserved.

# QAPI proxy command examples
# To get paste-able list of commands with comments, run this script as follows:
# bash -x ./metacurl.sh 2>&1 | sed -e 's/^\+ //' | grep -E "^(curl|sleep|#|$)"

C_TYPE=(-H "Content-Type: application/json; charset=utf-8")
PROXY_CALL="curl --compress --key ../../cfg/ssl/proxy.key -E ../../cfg/ssl/proxy.crt:1234 --tlsv1.2 -ksi"
PROXY_URL="https://localhost:8118"
WAIT="sleep .25"

EPID="a81ffa72113e29b9f1ff210dd9725249"
AUTH="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

pushd `dirname $0` > /dev/null

LIDA="proxyentitya"
echo -e "\n\n# === proxy - create entity [${LIDA}]"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"lid":"'"${LIDA}"'"}' ${PROXY_URL}/entity
${WAIT}
echo -e "\n\n# === proxy - get entity meta from metahelper"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" ${PROXY_URL}/entity/${LIDA}/metahelper
${WAIT}
echo -e "\n\n# === proxy - set entity meta via metahelper"
${PROXY_CALL} -X PUT "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" --data-binary '{"label": "labelly mc labelface", "description": "describing stuff", "lat": 12, "lon": 34}' ${PROXY_URL}/entity/${LIDA}/metahelper
${WAIT}
echo -e "\n\n# === proxy - get entity metahelper should have label, description, lat, long"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" ${PROXY_URL}/entity/${LIDA}/metahelper
${WAIT}
echo -e "\n\n# === proxy - get entity metahelper in French should not have label, description, should have lat, long"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: fr" ${PROXY_URL}/entity/${LIDA}/metahelper
${WAIT}
echo -e "\n\n# === proxy - get entity metahelper tags, should have nothing"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" ${PROXY_URL}/entity/${LIDA}/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - create entity tag [${LIDA} -> ['hello', 'fish']] in English"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" --data-binary '{"tags": ["hello", "fish"]}' ${PROXY_URL}/entity/${LIDA}/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - get entity metahelper tags, should have hello, fish in English"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" ${PROXY_URL}/entity/${LIDA}/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - get entity metahelper tags, should have nothing in French"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: fr" ${PROXY_URL}/entity/${LIDA}/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - delete entity tag [${LIDA} -> ['fish']] in English"
${PROXY_CALL} -X DELETE "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" --data-binary '{"tags": ["fish"]}' ${PROXY_URL}/entity/${LIDA}/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - get entity metahelper tags, should have hello, in English"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" ${PROXY_URL}/entity/${LIDA}/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - delete entity tag [${LIDA} -> ['fish']] in French - shouldn't fail"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: fr" --data-binary '{"tags": ["fish"]}' ${PROXY_URL}/entity/${LIDA}/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - get entity metahelper tags, should have nothing in French"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: fr" ${PROXY_URL}/entity/${LIDA}/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - set entity public"
${PROXY_CALL} -X PUT "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"public": true}' ${PROXY_URL}/entity/${LIDA}/setpublic
${WAIT}
echo -e "\n\n# === proxy - create point feed [${LIDA} -> 'data'"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"lid":"'"${LIDA}"'", "pid": "data"}' ${PROXY_URL}/point/feed
${WAIT}
echo -e "\n\n# === proxy - get point meta ${LIDA} data from metahelper"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" ${PROXY_URL}/point/feed/${LIDA}/data/metahelper
${WAIT}
echo -e "\n\n# === proxy - set point meta ${LIDA} data via metahelper"
${PROXY_CALL} -X PUT "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" --data-binary '{"label": "pointy mc pointface", "description": "pointless description"}' ${PROXY_URL}/point/feed/${LIDA}/data/metahelper
${WAIT}
echo -e "\n\n# === proxy - get point meta ${LIDA} data from metahelper should have label and descript"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en"  ${PROXY_URL}/point/feed/${LIDA}/data/metahelper
${WAIT}
echo -e "\n\n# === proxy - get point meta ${LIDA} data from metahelper in French should not have label and descript"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: fr"  ${PROXY_URL}/point/feed/${LIDA}/data/metahelper
${WAIT}
echo -e "\n\n# === proxy - get point metahelper tags, should have nothing"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" ${PROXY_URL}/point/feed/${LIDA}/data/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - create point tag [${LIDA} -> ['goodbye', 'cats']] in English"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" --data-binary '{"tags": ["goodbye", "cats"]}' ${PROXY_URL}/point/feed/${LIDA}/data/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - get point metahelper tags, should have goodbye, cats in English"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" ${PROXY_URL}/point/feed/${LIDA}/data/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - get point metahelper tags, should have nothing in French"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: fr" ${PROXY_URL}/point/feed/${LIDA}/data/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - delete point tag [${LIDA} -> ['cats']] in English"
${PROXY_CALL} -X DELETE "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" --data-binary '{"tags": ["cats"]}' ${PROXY_URL}/point/feed/${LIDA}/data/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - get point metahelper tags, should have goodbye, in English"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: en" ${PROXY_URL}/point/feed/${LIDA}/data/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - delete point tag [${LIDA} -> ['cats']] in French - shouldn't fail"
${PROXY_CALL} -X DELETE "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: fr" --data-binary '{"tags": ["cats"]}' ${PROXY_URL}/point/feed/${LIDA}/data/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - get point metahelper tags, should have nothing in French"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" -H "X-Language: fr" ${PROXY_URL}/point/feed/${LIDA}/data/tag/metahelper
${WAIT}
echo -e "\n\n# === proxy - delete point [${LIDA} -> ['data']"
${PROXY_CALL} -X DELETE -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/point/feed/${LIDA}/data
${WAIT}
echo -e "\n\n# === proxy - delete entity [${LIDA}]"
${PROXY_CALL} -X DELETE -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/entity/${LIDA}
${WAIT}


popd > /dev/null
