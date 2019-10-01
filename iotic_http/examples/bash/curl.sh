#!/usr/bin/env bash
# Copyright (c) 2016 Iotic Labs Ltd. All rights reserved.

# QAPI proxy command examples
# To get paste-able list of commands with comments, run this script as follows:
# bash -x ./curl.sh 2>&1 | sed -e 's/^\+ //' | grep -E "^(curl|sleep|#|$)"

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
LIDB="proxyentityb"
echo -e "\n\n# === proxy - rename entity [${LIDA} -> ${LIDB}]"
${PROXY_CALL} -X PUT "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"newlid":"'"${LIDB}"'"}' ${PROXY_URL}/entity/${LIDA}/rename
${WAIT}
echo -e "\n\n# === proxy - reassign entity [${LIDB} -> null/this epId]"
${PROXY_CALL} -X PUT "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"epId":null}' ${PROXY_URL}/entity/${LIDB}/reassign
${WAIT}
echo -e "\n\n# === proxy - delete entity [${LIDB}]"
${PROXY_CALL} -X DELETE -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/entity/${LIDB}
${WAIT}
echo -e "\n\n# === proxy - list of entities in this epId"
${PROXY_CALL} -H "X-Range: 0/5" -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/entity
${WAIT}
echo -e "\n\n# === proxy - list of entities in all my epIds on this container"
${PROXY_CALL} -H "X-Range: 0/5" -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/entity/all
${WAIT}
echo -e "\n\n# === proxy - re-create entity [${LIDA}]"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"lid":"'"${LIDA}"'"}' ${PROXY_URL}/entity
${WAIT}

echo -e "\n\n# === proxy - get entity meta xml"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/entity/${LIDA}/xml/meta
${WAIT}
echo -e "\n\n# === proxy - set entity meta xml"
${PROXY_CALL} -X PUT "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"meta": "blah invalid meta"}' ${PROXY_URL}/entity/${LIDA}/xml/meta
${WAIT}
echo -e "\n\n# === proxy - set entity public"
${PROXY_CALL} -X PUT "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"public": true}' ${PROXY_URL}/entity/${LIDA}/setpublic
${WAIT}

echo -e "\n\n# === proxy - create entity tag [${LIDA} -> ['hello', 'fish']]"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"tags": ["hello", "fish"], "lang": "en"}' ${PROXY_URL}/entity/${LIDA}/tag
${WAIT}
echo -e "\n\n# === proxy - delete entity tag [${LIDA} -> ['hello']"
${PROXY_CALL} -X DELETE "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"tags": ["hello"], "lang": "en"}' ${PROXY_URL}/entity/${LIDA}/tag
${WAIT}
echo -e "\n\n# === proxy - list entity tag"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/entity/${LIDA}/tag
${WAIT}

echo -e "\n\n# === proxy - create point feed [${LIDA} -> 'data'"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"lid":"'"${LIDA}"'", "pid": "data", "saveRecent": 2}' ${PROXY_URL}/point/feed
${WAIT}
echo -e "\n\n# === proxy - create point control [${LIDA} -> 'button'"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"lid":"'"${LIDA}"'", "pid": "button", "saveRecent": 2}' ${PROXY_URL}/point/control
${WAIT}
echo -e "\n\n# === proxy - rename point feed [${LIDA} data -> atad"
${PROXY_CALL} -X PUT "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"newpid": "atad"}' ${PROXY_URL}/point/feed/${LIDA}/data/rename
${WAIT}
echo -e "\n\n# === proxy - list point feed ${LIDA}"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/point/feed/${LIDA}
${WAIT}
echo -e "\n\n# === proxy - list point control ${LIDA}"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/point/control/${LIDA}
${WAIT}
echo -e "\n\n# === proxy - list point detailed feed ${LIDA} atad"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/point/feed/${LIDA}/atad
${WAIT}

echo -e "\n\n# === proxy - get point meta ${LIDA} atad xml"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/point/feed/${LIDA}/atad/xml/meta
${WAIT}
echo -e "\n\n# === proxy - set point meta ${LIDA} atad xml"
${PROXY_CALL} -X PUT "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"meta": "invalid meta"}' ${PROXY_URL}/point/feed/${LIDA}/atad/xml/meta
${WAIT}

echo -e "\n\n# === proxy - create point value control [${LIDA} -> 'button'] col1 int"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"label":"col1", "vtype": "int"}' ${PROXY_URL}/value/control/${LIDA}/button
${WAIT}
echo -e "\n\n# === proxy - list point values ${LIDA} button"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/value/control/${LIDA}/button
${WAIT}
echo -e "\n\n# === proxy - delete point value control [${LIDA} -> ['button'] col1"
${PROXY_CALL} -X DELETE -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/value/control/${LIDA}/button/col1/en
${WAIT}

echo -e "\n\n# === proxy - create point tag control [${LIDA} -> 'button'] hello fish"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"tags":["hello","fish"], "lang": "en"}' ${PROXY_URL}/point/control/${LIDA}/button/tag
${WAIT}
echo -e "\n\n# === proxy - list point tags ${LIDA} button"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/point/control/${LIDA}/button/tag
${WAIT}
echo -e "\n\n# === proxy - delete point tag control [${LIDA} -> ['button'] hello"
${PROXY_CALL} -X DELETE "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"tags":["hello"], "lang": "en"}' ${PROXY_URL}/point/control/${LIDA}/button/tag
${WAIT}

echo -e "\n\n# === proxy - sub create [df167e1c79250d9041cd80f943600542]"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"gpid":"df167e1c79250d9041cd80f943600542"}' ${PROXY_URL}/sub/feed/${LIDA}
${WAIT}
echo -e "\n\n# === proxy - sub create local [tims_energenie.data]"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"slid":"'"${LIDA}"'"}' ${PROXY_URL}/sub/feed/tims_energenie/data
${WAIT}
echo -e "\n\n# === proxy - list subs ${LIDA}"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/sub/${LIDA}
${WAIT}
echo -e "\n\n# === proxy - list sub recent ${LIDA}"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/sub/guid/count/recent
${WAIT}
echo -e "\n\n# === proxy - delete sub [${LIDA} -> guid"
${PROXY_CALL} -X DELETE -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/sub/guid
${WAIT}

echo -e "\n\n# === proxy - point share [${LIDA} atad 'databytes']"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"data":"databytes"}' ${PROXY_URL}/point/${LIDA}/atad/share
${WAIT}

# todo: /sub/subid/ask or /tell {'data': xx, 'mime': yy}

echo -e "\n\n# === proxy - search [energenie]"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"text":"energenie"}' ${PROXY_URL}/search
${WAIT}
echo -e "\n\n# === proxy - describe [df167e1c79250d9041cd80f943600542]"
${PROXY_CALL} -X POST "${C_TYPE[@]}" -H "epId: ${EPID}" -H "authToken: ${AUTH}" --data-binary '{"guid":"df167e1c79250d9041cd80f943600542"}' ${PROXY_URL}/describe
${WAIT}

# Special: The QAPIWorker can collect unsolicited (reassigned, subscription) (feeddata) (controlreq) messages.
echo -e "\n\n# === proxy - get feeddata"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/feeddata
${WAIT}
echo -e "\n\n# === proxy - get controlreq"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/controlreq
${WAIT}
echo -e "\n\n# === proxy - get unsolicited"
${PROXY_CALL} -X GET -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/unsolicited
${WAIT}

echo -e "\n\n# === proxy - delete point [${LIDA} -> ['atad']"
${PROXY_CALL} -X DELETE -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/point/feed/${LIDA}/atad
${WAIT}
echo -e "\n\n# === proxy - delete entity [${LIDA}]"
${PROXY_CALL} -X DELETE -H "epId: ${EPID}" -H "authToken: ${AUTH}" ${PROXY_URL}/entity/${LIDA}
${WAIT}


popd > /dev/null
