#!/usr/bin/env bash
# Copyright (c) 2016 Iotic Labs Ltd. All rights reserved.

# Note: mosquitto src downloaded and built, not installed
# MOSQ_PATH="/home/user/Downloads/mosquitto-1.4.10"
# PUB_CALL="${MOSQ_PATH}/client/mosquitto_pub"
# SUB_CALL="${MOSQ_PATH}/client/mosquitto_sub"
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${MOSQ_PATH}/lib

PUB_CALL="/usr/bin/mosquitto_pub"
SUB_CALL="/usr/bin/mosquitto_sub"

WAIT="sleep .25"

pushd `dirname $0` > /dev/null

echo -e "\n\n# === ioticlabs/req/example/3/create/entity {\"lid\": \"fish\"}"
${PUB_CALL} -t ioticlabs/req/example/3/create/entity -m "{\"lid\": \"fish\"}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/4/create/entity {\"lid\": \"fishfishfishfishfishfishfishfishfishfishfishfishfishfishfishfishfish\"}"
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1 &
# NOTE: Example of client side validation, must sub first since too fast
${PUB_CALL} -t ioticlabs/req/example/4/create/entity -m "{\"lid\": \"fishfishfishfishfishfishfishfishfishfishfishfishfishfishfishfishfish\"}"
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/7/update/entity/fish/rename {\"newlid\": \"chips\"}"
${PUB_CALL} -t ioticlabs/req/example/7/update/entity/fish/rename -m "{\"newlid\": \"chips\"}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

# echo -e "\n\n# === ioticlabs/req/example/7/update/entity/chips/reassign {\"epId\": \"xxx\"}"
# ${PUB_CALL} -t ioticlabs/req/example/7/update/entity/chips/reassign -m "{\"epId\": \"xxx\"}" &
# ${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
# ${WAIT}

echo -e "\n\n# === ioticlabs/req/example/8/delete/entity/chips"
${PUB_CALL} -t ioticlabs/req/example/8/delete/entity/chips -m " " &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/3/create/entity {\"lid\": \"fish\"}"
${PUB_CALL} -t ioticlabs/req/example/3/create/entity -m "{\"lid\": \"fish\"}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/1/list/entity"
${PUB_CALL} -t ioticlabs/req/example/1/list/entity -m " " &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/2/list/entity/all"
${PUB_CALL} -t ioticlabs/req/example/2/list/entity/all -m " " &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/2/list/entity/fish/xml/meta"
${PUB_CALL} -t ioticlabs/req/example/2/list/entity/fish/xml/meta -m " " &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

# echo -e "\n\n# === ioticlabs/req/example/2/update/entity/fish/xml/meta"
# ${PUB_CALL} -t ioticlabs/req/example/2/update/entity/fish/xml/meta -m "{\"meta\": \"<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>\\\n<rdf:RDF\\\n   xmlns:iotic=\\\"http://purl.org/net/iotic-labs#\\\"\\\n   xmlns:j.0=\\\"http://purl.org/dc/terms/\\\"\\\n   xmlns:rdf=\\\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\\\"\\\n>\\\n  <rdf:Description rdf:about=\\\"urn:uuid:69447885-88a8-caf9-3f33-fbaa03f3249b\\\">\\\n    <iotic:ContainedIn rdf:resource=\\\"urn:uuid:f8fd93ed-7328-0432-3edc-3dc9f5202d0d\\\"/>\\\n    <j.0:created rdf:datatype=\\\"http://www.w3.org/2001/XMLSchema#datetime\\\">2016-10-13T14:04:28.981505</j.0:created>\\\n    <rdf:type rdf:resource=\\\"http://purl.org/net/iotic-labs#Entity\\\"/>\\\n  </rdf:Description>\\\n</rdf:RDF>\\\n\"}" &
# ${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
# ${WAIT}

echo -e "\n\n# === ioticlabs/req/example/2/update/entity/fish/setpublic"
${PUB_CALL} -t ioticlabs/req/example/2/update/entity/fish/setpublic -m "{\"public\": true}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/3/create/entity/fish/tag {\"tags\": [\"fish\"]}"
${PUB_CALL} -t ioticlabs/req/example/3/create/entity/fish/tag -m "{\"tags\": [\"fish\"]}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/3/list/entity/fish/tag"
${PUB_CALL} -t ioticlabs/req/example/3/list/entity/fish/tag -m " " &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/3/delete/entity/fish/tag {\"tags\": [\"fish\"]}"
${PUB_CALL} -t ioticlabs/req/example/3/delete/entity/fish/tag -m "{\"tags\": [\"fish\"]}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/5/create/point/feed {\"lid\": \"fish\", \"pid\": \"data\"}"
${PUB_CALL} -t ioticlabs/req/example/5/create/point/feed -m "{\"lid\": \"fish\", \"pid\": \"data\"}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/6/create/point/control {\"lid\": \"fish\", \"pid\": \"button\"}"
${PUB_CALL} -t ioticlabs/req/example/6/create/point/control -m "{\"lid\": \"fish\", \"pid\": \"button\"}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/7/update/point/fish/data/share {\"blah\": 213}"
${PUB_CALL} -t ioticlabs/req/example/7/update/point/fish/data/share -m "{\"blah\": 213}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/8/update/point/fish/data/share {\"data\": 213, \"mime\": \"application/blah\", \"time\": \"2016-11-28T12:00:00.000000Z\"}"
${PUB_CALL} -t ioticlabs/req/example/8/update/point/fish/data/share -m "{\"blah\": 213}" &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

echo -e "\n\n# === ioticlabs/req/example/9/delete/entity/fish"
${PUB_CALL} -t ioticlabs/req/example/9/delete/entity/fish -m " " &
${SUB_CALL} -t ioticlabs/rsp/example/# -C 1
${WAIT}

popd > /dev/null
