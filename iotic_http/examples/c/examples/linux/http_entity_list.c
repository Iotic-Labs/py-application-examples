/**
 * Iotic Labs Agent API C Library for HTTP(S) REST & MQTT
 * Copyright (c) 2016 Iotic Labs Ltd. All rights reserved
 * ------------------------------------------------------
 *
 */

#include <stdio.h>
#include <stdlib.h>

#include "agent.h"


int main(void) {
    IOTICAGENT *agent = ioticagent_init();
    if(agent) {
        ioticagent_setopt(agent, IOTICOPT_VERBOSE, 1);
        ioticagent_setopt(agent, IOTICOPT_HOST, "http://localhost");
        ioticagent_setopt(agent, IOTICOPT_PORT, 8118);
        ioticagent_setopt(agent, IOTICOPT_HTTP_EPID, "a81ffa72113e29b9f1ff210dd9725249");
        ioticagent_setopt(agent, IOTICOPT_HTTP_AUTHTOKEN, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");

        iotic_agent_payload payload;
        if(ioticagent_payload_init(&payload) == IOTICE_OK) {
            /* entity_list */
            IoticAgentCode res = ioticagent_entity_list(agent, &payload);
            if(res == IOTICE_OK) {
                printf("\nentity_list OK: %s\n", payload.payload);
            }
            else {
                /*if(ioticagent_geterr(agent, payloadbuf, 1024) == IOTICE_OK) {
                //    printf("got error: %s", payloadbuf);
                }*/
            }
            ioticagent_payload_destroy(&payload);
        }

        if(ioticagent_payload_init(&payload) == IOTICE_OK) {
            /* entity create */
            IoticAgentCode res = ioticagent_entity_create(agent, "testthing", NULL, &payload);
            if(res == IOTICE_OK) {
                printf("\nentity_create OK: %s\n", payload.payload);
            }
            ioticagent_payload_destroy(&payload);
        }

        if(ioticagent_payload_init(&payload) == IOTICE_OK) {
            /* point create */
            IoticAgentCode res = ioticagent_point_create(agent, IOTICFOC_FEED, "testthing", "data", &payload);
            if(res == IOTICE_OK) {
                printf("\npoint_create OK: %s\n", payload.payload);
            }
            ioticagent_payload_destroy(&payload);
        }

        if(ioticagent_payload_init(&payload) == IOTICE_OK) {
            /* point share */
            IoticAgentCode res = ioticagent_point_share(agent, "testthing", "data", "timisafish", 10, &payload);
            if(res == IOTICE_OK) {
                printf("\npoint_share OK: %s\n", payload.payload);
            }
            ioticagent_payload_destroy(&payload);
        }

        if(ioticagent_payload_init(&payload) == IOTICE_OK) {
            /* point share */
            IoticAgentCode res = ioticagent_feeddata(agent, &payload);
            if(res == IOTICE_OK) {
                printf("\nfeeddata OK: %s\n", payload.payload);
            }
            ioticagent_payload_destroy(&payload);
        }

        if(ioticagent_payload_init(&payload) == IOTICE_OK) {
            /* point share */
            IoticAgentCode res = ioticagent_feeddata(agent, &payload);
            if(res == IOTICE_OK) {
                printf("OK: %s\n", payload.payload);
            }
            ioticagent_payload_destroy(&payload);
        }

        if(ioticagent_payload_init(&payload) == IOTICE_OK) {
            /* entity delete */
            IoticAgentCode res = ioticagent_entity_delete(agent, "testthing", &payload);
            if(res == IOTICE_OK) {
                printf("\nentity_delete OK: %s\n", payload.payload);
            }
            ioticagent_payload_destroy(&payload);
        }
        ioticagent_destroy(agent);
    }
    return 0;
}
