/**
 * Iotic Labs Agent API C Library for HTTP(S) REST & MQTT
 * Copyright (c) 2016 Iotic Labs Ltd. All rights reserved
 * ------------------------------------------------------
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <math.h>

#include "agent.h"


/** ioticagent_entity_list */
IoticAgentCode ioticagent_entity_list(IOTICAGENT *agent, iotic_agent_payload *payload) {
    return ClientRequest(agent, IOTICCRUD_LIST, "/entity", NULL, 0, 0, 0, payload);
}

/* ioticagent_entity_create */
IoticAgentCode ioticagent_entity_create(IOTICAGENT *agent, char *lid, char *epId, iotic_agent_payload *payload) {
    if(lid == NULL) {
        return IOTICE_ERROR;
    }

    int8_t *post;
    size_t post_len = 0;
    post_len = strlen("{\"lid\":\ \"\"}") + strlen(lid) + 1;
    if(epId != NULL) {
        post_len += strlen(",\ \"epId\":\ \"\"") + strlen(epId);
    }

    post = (int8_t*)calloc(post_len, sizeof(int8_t));
    if(post == NULL) {
        return IOTICE_ERROR;
    }

    if(epId == NULL) {
        sprintf((char*)post, "{\"lid\":\"%s\"}", lid);
    }
    else {
        sprintf((char*)post, "{\"lid\":\"%s\",\ \"epId\":\"%s\"}", lid, epId);
    }

    IoticAgentCode res = ClientRequest(agent, IOTICCRUD_CREATE, "/entity", post, post_len-1, 0, 0, payload);
    free(post);
    return res;
}

/* ioticagent_entity_delete */
IoticAgentCode ioticagent_entity_delete(IOTICAGENT *agent, char *lid, iotic_agent_payload *payload) {
    if(lid == NULL) {
        return IOTICE_ERROR;
    }
    char *url = calloc(strlen("/entity/") + strlen(lid) + 1, sizeof(char));
    if(url == NULL) {
        return IOTICE_ERROR;
    }
    sprintf(url, "/entity/%s", lid);

    IoticAgentCode res = ClientRequest(agent, IOTICCRUD_DELETE, url, NULL, 0, 0, 0, payload);
    free(url);
    return res;
}

/* ioticagent_point_create */
IoticAgentCode ioticagent_point_create(IOTICAGENT *agent, IoticAgentFeedOrControl foc, char *lid, char *pid, iotic_agent_payload *payload) {
    if(foc != IOTICFOC_FEED && foc != IOTICFOC_CONTROL) {
        return IOTICE_ERROR;
    }
    if(lid == NULL || pid == NULL) {
        return IOTICE_ERROR;
    }

    size_t post_len = strlen("{\"lid\":\"\",\"pid\":\"\"}") + strlen(lid) + strlen(pid) + 1;
    int8_t *post = calloc(post_len, sizeof(int8_t));
    if(post == NULL) {
        return IOTICE_ERROR;
    }
    sprintf((char*)post, "{\"lid\":\"%s\",\"pid\":\"%s\"}", lid, pid);

    IoticAgentCode res;
    if(foc == IOTICFOC_FEED) {
        res = ClientRequest(agent, IOTICCRUD_CREATE, "/point/feed", post, post_len-1, 0, 0, payload);
    }
    else {
        res = ClientRequest(agent, IOTICCRUD_CREATE, "/point/control", post, post_len-1, 0, 0, payload);
    }

    free(post);
    return res;
}

/** ioticagent_entity_setpublic */
IoticAgentCode ioticagent_entity_setpublic(IOTICAGENT *agent, char *lid, int is_public, iotic_agent_payload *payload) {
    return IOTICE_ERROR;
}

/** ioticagent_point_share */
IoticAgentCode ioticagent_point_share(IOTICAGENT *agent, char *lid, char *pid, int8_t *share, size_t share_len, iotic_agent_payload *payload) {
    if(lid == NULL || pid == NULL || share == NULL) {
        return IOTICE_ERROR;
    }

    size_t path_len = strlen("/point///share") + strlen(lid) + strlen(pid) + 1;
    char *path = calloc(path_len, sizeof(char));
    if(path == NULL) {
        return IOTICE_ERROR;
    }
    sprintf(path, "/point/%s/%s/share", lid, pid);

    IoticAgentCode res = ClientRequest(agent, IOTICCRUD_UPDATE, path, share, share_len, 0, 0, payload);
    free(path);
    return res;
}

/** ioticagent_feeddata */
IoticAgentCode ioticagent_feeddata(IOTICAGENT *agent, iotic_agent_payload *payload) {
    return ClientRequest(agent, IOTICCRUD_LIST, "/feeddata", NULL, 0, 0, 0, payload);
}
