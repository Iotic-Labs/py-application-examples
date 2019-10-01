/** Iotic Labs Agent API C Library for HTTP(S) REST & MQTT
 * Copyright (c) 2016 Iotic Labs Ltd. All rights reserved
 * ------------------------------------------------------
 *
 */

#ifndef __IOTICAGENT_H
#define __IOTICAGENT_H

#include <stdarg.h>
#include <stdlib.h>
#include <stdint.h>

/* Enable DEBUG logging */
#define DEBUG

/**
 * IOTICAGENT placeholder type
 */
typedef void IOTICAGENT;

/**
 *
 */
typedef enum {
    IOTICOPT_VERBOSE,
    IOTICOPT_IP,
    IOTICOPT_HOST,
    IOTICOPT_PORT,
    IOTICOPT_IDLE_TIMEOUT,
    IOTICOPT_HTTP_EPID,
    IOTICOPT_HTTP_AUTHTOKEN,
#ifdef IOTICAGENT_USE_CC3000
    IOTICOPT_CC3000             /* Pointer to Adafruit_CC3000 class inst' */
#endif
} IoticAgentOptions;

/**
 *
 */
typedef enum {
    IOTICE_OK,
    IOTICE_ERROR,
    IOTICE_ERROR_BADOPT,
    IOTICE_ERROR_NOMEM,
    IOTICE_ERROR_MALFORMED      /* Malformed arguments */
} IoticAgentCode;

/**
 *
 */
typedef enum {
    IOTICFOC_FEED,
    IOTICFOC_CONTROL,
} IoticAgentFeedOrControl;

/**
 *
 */
typedef enum {
    IOTICCRUD_CREATE,
    IOTICCRUD_LIST,
    IOTICCRUD_UPDATE,
    IOTICCRUD_DELETE
} IoticAgentCrud;

/**
 *
 */
typedef struct {
    char *host;              /* Host string */
    uint32_t ip;             /* IP int */
    int port;                /* Port */
} iotic_agent_host;

/**
 *
 */
typedef struct {
    iotic_agent_host *host;     /* Host info */
    IoticAgentOptions conn;     /* IOTICOPT_CONN_* */
    char *http_epid;
    char *http_authtoken;
    int idle_timeout;
    char *errbuf;
    int verbose;
#ifdef IOTICAGENT_USE_CC3000
    void *cc3000;
#endif
} iotic_agent;
/* */

/**
 * iotic_agent_payload:
 */
typedef struct {
    char *payload;          /* Payload */
    size_t payload_len;     /* Length of payload */
    int code;               /* Result code from API (200 OK, 201 Created, 204 Deleted, etc) */
} iotic_agent_payload;

/**
 * ioticagent_init: Create a new IOTICAGENT instance.
 * If this function returns NULL something went wrong.
 * IOTICAGENT instances must be freed using ioticagent_destroy;
 */
IOTICAGENT *ioticagent_init(void);

/**
 * ioticagent_destroy: Free a IOTICAGENT instance.
 * No return value.  NULL will be ignored.
 */
void ioticagent_destroy(IOTICAGENT *agent);

/**
 * ioticagent_setopt: set options on the IOTICAGENT struct.
 */
IoticAgentCode ioticagent_setopt(IOTICAGENT *agent, IoticAgentOptions option, ...);
IoticAgentCode ioticagent_setopt_va(IOTICAGENT *agent, IoticAgentOptions option, va_list arg);

/**
 * ioticagent_get_err: Write error response to errbuf.
 * Return code.
 */
IoticAgentCode ioticagent_geterr(IOTICAGENT *agent, char *errbuf, size_t errbuf_len);

/**
 * ClientRequest function sig'
 */
IoticAgentCode ClientRequest(IOTICAGENT *agent, IoticAgentCrud crud, char *path, int8_t *postdata, size_t postdata_len, int limit, int offset, iotic_agent_payload *payload);

/**
 * ioticagent_entity_list: Get list of entities in this agent
 * If payload is not NULL then realloc will be used until payload->payload contains the entire response payload
 * return int code from enum IoticAgentCode
 */
IoticAgentCode ioticagent_entity_list(IOTICAGENT *agent, iotic_agent_payload *payload);

/**
 * ioticagent_entity_create: Create a new entity/Thing
 * char* lid is required, the local name for the Thing
 * char* epId is optional, if null this agent will be used
 */
IoticAgentCode ioticagent_entity_create(IOTICAGENT *agent, char *lid, char *epId, iotic_agent_payload *payload);

/**
 * ioticagent_entity_delete: Delete an entity/Thing
 * char* lid is required.
 */
IoticAgentCode ioticagent_entity_delete(IOTICAGENT *agent, char *lid, iotic_agent_payload *payload);

/**
 * ioticagent_feed_create: Create a Feed on an entity/Thing
 * char* lid is required
 * char* pid is required, local name of the point
 */
IoticAgentCode ioticagent_feed_create(IOTICAGENT *agent, char *lid, char *pid, iotic_agent_payload *payload);

/**
 * ioticagent_feed_create: Create a Control on an entity/Thing
 * char* lid is required
 * char* pid is required, local name of the point
 */
IoticAgentCode ioticagent_control_create(IOTICAGENT *agent, char *lid, char *pid, iotic_agent_payload *payload);

/**
 * ioticagent_point_create: Create a Feed or Control on an entity/Thing
 * IoticAgentFeedOrControl foc is required
 * char* lid is required
 * char* pid is required, local name of the point
 */
IoticAgentCode ioticagent_point_create(IOTICAGENT *agent, IoticAgentFeedOrControl foc, char *lid, char *pid, iotic_agent_payload *payload);

/**
 * ioticagent_set_public: Toggle whether Thing is public
 * char* lid is required
 * int is_public (0 for false else true) is required
 */
IoticAgentCode ioticagent_entity_setpublic(IOTICAGENT *agent, char *lid, int is_public, iotic_agent_payload *payload);

/**
 * ioticagent_point_share: Share feed data
 * char* lid,
 * char* pid,
 * int8_t* payload,
 * size_t payload_len
 */
IoticAgentCode ioticagent_point_share(IOTICAGENT *agent, char *lid, char *pid, int8_t *share, size_t share_len, iotic_agent_payload *payload);

/** ioticagent_feeddata: Download any feeddata queued for this Agent */
IoticAgentCode ioticagent_feeddata(IOTICAGENT *agent, iotic_agent_payload *payload);

/**
 *
 */
IoticAgentCode ioticagent_payload_init(iotic_agent_payload *payload);

/**
 *
 */
void ioticagent_payload_destroy(iotic_agent_payload *payload);

#endif /* __IOTICAGENT_H */
