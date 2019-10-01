/**
 * Iotic Labs Agent API C Library for HTTP(S) REST & MQTT
 * Copyright (c) 2016 Iotic Labs Ltd. All rights reserved
 * ------------------------------------------------------
 *
 */

#ifdef IOTICAGENT_USE_LIBCURL

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>
#include <math.h>

#include "agent.h"

#include <curl/curl.h>


/** WriteMemoryCallback: used by curl to populate iotic_agent_payload struct */
static size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    iotic_agent_payload *mem = (iotic_agent_payload *)userp;

    mem->payload = (char*)realloc(mem->payload, mem->payload_len + realsize + 1);
    if(mem->payload == NULL) {
        /* out of memory! */
        printf("not enough memory (realloc returned NULL)\n");
        return 0;
    }

    memcpy(&(mem->payload[mem->payload_len]), contents, realsize);
    mem->payload_len += realsize;
    mem->payload[mem->payload_len] = 0;
#ifdef DEBUG
    printf("\nagent_http_libcurl WriteMemoryCallback got '%s'", mem->payload);
#endif
    return realsize;
}


/** Curl ClientRequest */
IoticAgentCode ClientRequest(IOTICAGENT *agent, IoticAgentCrud crud, char *path, int8_t *postdata, size_t postdata_len, int limit, int offset, iotic_agent_payload *payload) {
#ifdef DEBUG
    if(postdata == NULL) {
        printf("\nagent_http_libcurl ClientRequest %x, %i, '%s', NULL, %i, %i, %i, %x", agent, crud, path, postdata_len, limit, offset, payload);
    }
    else {
        printf("\nagent_http_libcurl ClientRequest %x, %i, '%s', '%s', %i, %i, %i, %x", agent, crud, path, postdata, postdata_len, limit, offset, payload);
    }
#endif
    IoticAgentCode ret = IOTICE_ERROR;
    if(agent != NULL) {
        iotic_agent *age = (iotic_agent*)agent;
        if(age->http_epid == NULL || age->http_authtoken == NULL) {
            return IOTICE_ERROR;
        }

        if(path == NULL) return IOTICE_ERROR;

        size_t url_len = 0;
        if(age->host != NULL && age->host->host != NULL) url_len = strlen(age->host->host);
        if(age->host != NULL && age->host->port != 0) url_len += floor(log10(abs(age->host->port))) + 1; /* 1 = : */
        if(url_len != 0) {
            url_len += strlen(path);
            char *url = (char*)malloc(url_len);
            if(url != NULL) {
                sprintf(url, "%s:%i%s", age->host->host, age->host->port, path);

                CURL *hnd = curl_easy_init();
                CURLcode res;

                if(crud == IOTICCRUD_CREATE) {
                    curl_easy_setopt(hnd, CURLOPT_CUSTOMREQUEST, "POST");
                    if(postdata != NULL) {
                        curl_easy_setopt(hnd, CURLOPT_POSTFIELDS, postdata);
                        curl_easy_setopt(hnd, CURLOPT_POSTFIELDSIZE, (long)postdata_len);
                    }
                    else {
                        goto bail;
                    }
                }
                else if(crud == IOTICCRUD_LIST) {
                    curl_easy_setopt(hnd, CURLOPT_CUSTOMREQUEST, "GET");
                }
                else if(crud == IOTICCRUD_UPDATE) {
                    curl_easy_setopt(hnd, CURLOPT_CUSTOMREQUEST, "PUT");
                    if(postdata != NULL) {
                        curl_easy_setopt(hnd, CURLOPT_POSTFIELDS, postdata);
                        curl_easy_setopt(hnd, CURLOPT_POSTFIELDSIZE, (long)postdata_len);
                    }
                }
                else if(crud == IOTICCRUD_DELETE) {
                    curl_easy_setopt(hnd, CURLOPT_CUSTOMREQUEST, "DELETE");
                }
                else {
                    return IOTICE_ERROR;
                }

                curl_easy_setopt(hnd, CURLOPT_URL, url);

                char *epid = NULL;
                char *auth = NULL;
                epid = (char*)calloc(strlen("epid: ") + strlen(age->http_epid) + 1, sizeof(char));
                if(epid == NULL) goto bail;
                sprintf(epid, "%s %s", "epid:", age->http_epid);

                auth = (char*)calloc(strlen("authtoken: ") + strlen(age->http_authtoken) + 1, sizeof(char));
                if(auth == NULL) goto bail;
                sprintf(auth, "%s %s", "authtoken:", age->http_authtoken);

                if(payload != NULL) {
                    curl_easy_setopt(hnd, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
                    curl_easy_setopt(hnd, CURLOPT_WRITEDATA, (void *)payload);
                }
                // NOTE: Else curl default is to print the payload

                if(limit != 0 && offset != 0) {
                    // todo
                }

                struct curl_slist *headers = NULL;
                headers = curl_slist_append(headers, auth);
                headers = curl_slist_append(headers, epid);
                if(crud == IOTICCRUD_UPDATE || crud == IOTICCRUD_CREATE) {
                    headers = curl_slist_append(headers, "Content-Type: application/json; charset=utf-8");
                }
                curl_easy_setopt(hnd, CURLOPT_HTTPHEADER, headers);

                if(res = curl_easy_perform(hnd) == CURLE_OK) {
                    ret = IOTICE_OK;
                }
                else {  // todo: stash error string
#ifdef DEBUG
    fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
#endif
                }

/* An error occured, free memory and bail! */
bail:
                free(url);
                free(epid);
                free(auth);
                curl_easy_cleanup(hnd);
            }
        }
    }
    return ret;
}

#endif /* IOTICAGENT_USE_LIBCURL */
