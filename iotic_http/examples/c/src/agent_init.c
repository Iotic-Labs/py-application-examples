/**
 * Iotic Labs Agent API C Library for HTTP(S) REST & MQTT
 * Copyright (c) 2016 Iotic Labs Ltd. All rights reserved
 * ------------------------------------------------------
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>

#include "agent.h"

/**
 * ioticagent_init: alloc / setup / init an IOTICAGENT handle */
IOTICAGENT *ioticagent_init(void) {
    IOTICAGENT *agent = (IOTICAGENT*)calloc(4, sizeof(iotic_agent));
    return agent;
}


/**
 * ioticagent_destroy: free an IOTICAGENT handle */
void ioticagent_destroy(IOTICAGENT *agent) {
    if(agent != NULL) {
        iotic_agent *age = (iotic_agent*)agent;
        if(age->host != NULL) {
            if(age->host->host != NULL) free(age->host->host);
            free(age->host);
        }
        if(age->http_epid != NULL) free(age->http_epid);
        if(age->http_authtoken != NULL) free(age->http_authtoken);
        if(age->errbuf != NULL) free(age->errbuf);
        free(age);
    }
}


/** ioticagent_setopt: helper to pass va_list to ioticagent_setopt_va */
IoticAgentCode ioticagent_setopt(IOTICAGENT *agent, IoticAgentOptions option, ...) {
    va_list arg;
    IoticAgentCode result;

    if(agent == NULL) {
        return IOTICE_ERROR;
    }

    va_start(arg, option);
    result = ioticagent_setopt_va(agent, option, arg);

    va_end(arg);
    return result;
}


/** ioticagent_geterr */
IoticAgentCode ioticagent_geterr(IOTICAGENT *agent, char *errbuf, size_t errbuf_len) {
    iotic_agent *age = (iotic_agent*)agent;
    if(errbuf != NULL && age->errbuf != NULL) {
        size_t maxlen = strlen(age->errbuf) < errbuf_len ? strlen(age->errbuf) : errbuf_len;
        strncpy(errbuf, age->errbuf, maxlen);
        return IOTICE_OK;
    }
    return IOTICE_ERROR;
}


/** ioticagent_payload_init */
IoticAgentCode ioticagent_payload_init(iotic_agent_payload *payload) {
    if(payload != NULL) {
        payload->payload = (void*)malloc(1);
        if(payload->payload == NULL) {
            return IOTICE_ERROR;
        }
        payload->payload_len = 0;
        return IOTICE_OK;
    }
    return IOTICE_ERROR;
}


/** ioticagent_payload_destroy */
void ioticagent_payload_destroy(iotic_agent_payload *payload) {
    if(payload != NULL) {
        free(payload->payload);
    }
}

