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


/** ioticagent_setopt */
IoticAgentCode ioticagent_setopt_va(IOTICAGENT *agent, IoticAgentOptions option, va_list args) {
   if(agent != NULL) {
       iotic_agent *age = (iotic_agent*)agent;
        switch(option) {
            case IOTICOPT_VERBOSE:
                age->verbose = va_arg(args, int);
                break;
#ifdef IOTICAGENT_USE_CC3000
            case IOTICOPT_CC3000:
                age->cc3000 = va_arg(args, void*);
                break;
#endif
            case IOTICOPT_IP:
            case IOTICOPT_HOST:
            case IOTICOPT_PORT:
                if(age->host == NULL) {
                    age->host = (iotic_agent_host*)calloc(4, sizeof(iotic_agent_host));
                }
                if(age->host != NULL) {
                    if(option == IOTICOPT_IP) {
                       age->host->ip = va_arg(args, uint32_t);
                    }
                    else if(option == IOTICOPT_HOST) {
                        char *hoststr = va_arg(args, char*);
                        if(hoststr != NULL) {
                            age->host->host = calloc(strlen(hoststr)+1, sizeof(char));
                            if(age->host->host != NULL) {
                                strcpy(age->host->host, hoststr);
                            }
                        }
                    }
                    else if(option == IOTICOPT_PORT) {
                        age->host->port = va_arg(args, int);
                    }
                    break;
                }
                return IOTICE_ERROR;

            case IOTICOPT_HTTP_EPID: {
                if(age->http_epid != NULL) {
                    free(age->http_epid);
                }
                char *epidstr = va_arg(args, char*);
                age->http_epid = calloc(strlen(epidstr)+1, sizeof(char));
                if(age->http_epid != NULL) {
                    strcpy(age->http_epid, epidstr);
                    break;
                }
                return IOTICE_ERROR;
            }
            case IOTICOPT_HTTP_AUTHTOKEN: {
                if(age->http_authtoken != NULL) {
                    free(age->http_authtoken);
                }
                char *authstr = va_arg(args, char*);
                age->http_authtoken = calloc(strlen(authstr)+1, sizeof(char));
                if(age->http_authtoken != NULL) {
                    strcpy(age->http_authtoken, authstr);
                    break;
                }
                return IOTICE_ERROR;
            }
            case IOTICOPT_IDLE_TIMEOUT: {
                if(age->idle_timeout != NULL) {
                    free(age->idle_timeout);
                }
                age->idle_timeout = va_arg(args, int);
            }
            default:
                return IOTICE_ERROR_BADOPT;
        }
        return IOTICE_OK;
   }
   return IOTICE_ERROR;
}


