/**
 * Iotic Labs Agent API C Library for HTTP(S) REST & MQTT
 * Copyright (c) 2016 Iotic Labs Ltd. All rights reserved
 * ------------------------------------------------------
 *
 */

#ifdef IOTICAGENT_USE_CC3000

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdarg.h>
#include <string.h>

#include <Arduino.h>
#include <Adafruit_CC3000.h>
#include <ccspi.h>

#include "agent.h"


/** cc3000_connect_client */  // note: these can live here but exposed to user
IoticAgentCode connect_client(Adafruit_CC3000 *cc3000, iotic_agent_host *host, Adafruit_CC3000_Client &client) {
    uint32_t ip_addr = 0;

    if(host->host == NULL && host->ip != 0) {
#ifdef DEBUG
        Serial.print(F("\nConnecting to "));
#endif
        ip_addr = host->ip;
    }
    else {
#ifdef DEBUG
    Serial.print(host->host); Serial.print(" -> ");
#endif
        int x = 0;
        while (ip_addr == 0 && x < 10)  {
            if (!cc3000->getHostByName(host->host, &ip_addr)) {
#ifdef DEBUG
                Serial.println(F("Couldn't resolve!"));
#endif
            }
            delay(500);
            x++;
        }
    }
#ifdef DEBUG
    cc3000->printIPdotsRev(ip_addr);
    Serial.print(":");
    Serial.println(host->port);
#endif

    client = cc3000->connectTCP(ip_addr, host->port);
    if (!client) {
#ifdef DEBUG
        Serial.println(F("Failed to connect client"));
        Serial.println(client);
#endif
       return IOTICE_ERROR;
    }
    return IOTICE_OK;
}


/** cc3000_disconnect_client */
IoticAgentCode disconnect_client(Adafruit_CC3000_Client &client) {
    client.close();
    if (client) {
        return IOTICE_ERROR; // TODO better error?
    }
    return IOTICE_OK;
}


int find_response_length(Adafruit_CC3000_Client &client) {
    // search for "Content-Length: " in response_header
    char res_header[20];
    char *res_length;
    char *look_for = "Content-Length: ";
    char searching[17];
    searching[16] = 0;
    int p = 0;
    int found = 0;

    char c = client.read();
    while(client.available()) {
        // if new line, start again
        if (c == '\n') {
            c = client.read();
        }

        searching[p++] = c;
        searching[p] = 0;

        if (p == 16) { // if end of array
            if (strcmp(look_for, searching) == 0) {
                found = 1;
                break;
            }
            while(c != '\r') c = client.read();
            p = 0;
        }
        c = client.read();
    }

    if (found) {
        p = 0;
        c = client.read();
        while(client.available() && isdigit(c) && p < 17) {
            searching[p++] = c;
            c = client.read();
        }
        if(p == 17) return -1;  // Error!  Can't be sure we got all the numbers
        searching[p] = 0;
        return atoi(searching);
    }
    return -1;
}


/** cc3000_read_http_request */
IoticAgentCode read_http_response(Adafruit_CC3000_Client &client, int idle_timeout, iotic_agent_payload *payload) {
    iotic_agent_payload *mem = (iotic_agent_payload *)payload;

    /* Read data until either the connection is closed, or the idle timeout is reached. */
    unsigned long lastRead = millis();

    //strcpy(response, "");
    //memset(&response_header[0], 0, sizeof(response_header));

    if (!client.connected()) {
        return IOTICE_ERROR;
    }

    mem->payload_len = find_response_length(client);
#ifdef DEBUG
    Serial.print(F("payload len: "));
    Serial.println(mem->payload_len);
#endif

    // check for timeout
    if (!mem->payload_len && (millis() - lastRead >= idle_timeout)) {
        return IOTICE_ERROR;   // TODO different error?
    }
    lastRead = millis();

    // reallocate memory to the payload according to the response length
    mem->payload = (char*)realloc(mem->payload, sizeof(char) * (mem->payload_len + 1));
    //memset(mem->payload, 0, sizeof (char) * mem->payload_len);

    if(mem->payload == NULL) {
    /* out of memory! */
#ifdef DEBUG
        Serial.println("realloc returned NULL, memory problem or invalid payload");
#endif
        return IOTICE_ERROR;
    }

    // wait for the actual response message to start
    char c = client.read();
    while (client.available() > 0 && c != '{' && c != '[') {
        c = client.read();
    }
    lastRead = millis();

    int i = 0;

    while(client.available() > 0 && i < mem->payload_len) {
        /* populate the payload */
        mem->payload[i++] = c;
        c = client.read();
        lastRead = millis();
    }
    mem->payload[i++] = c; // include last char
    mem->payload[i] = 0;

    // check for timeout
    if (!mem->payload && (millis() - lastRead >= idle_timeout)) {
        Serial.println(F("bad payload error"));
        return IOTICE_ERROR;   // TODO different error?
    }

    return IOTICE_OK;
}


/** cc3000_send_http_request */
IoticAgentCode send_http_request(Adafruit_CC3000_Client &client, int8_t *request_msg) {
    if (client.connected()) {
        if (request_msg) {
            client.fastrprintln("Content-Type: application/json; charset=utf-8");
            client.fastrprint("Content-Length:");
            client.println(strlen((char*)request_msg));
            client.println();
            client.fastrprintln((char*)request_msg);
        }
    } else {
#ifdef DEBUG
        Serial.println(F("Connection failed"));
#endif
        return IOTICE_ERROR;
    }
    return IOTICE_OK;
}


/** cc3000_send_close_request */
void send_close_request(Adafruit_CC3000_Client &client) {
    client.fastrprintln("Connection: close");
    client.println();
}


/** cc3000_send_http_headers */
IoticAgentCode send_http_headers(Adafruit_CC3000_Client &client, char *request_type, char *host, char *path, char *epid, char *auth, char *lang, int limit, int offset, int content) {
    if (client.connected()) {
        client.fastrprint(request_type);
        client.fastrprint(path);
        client.fastrprintln(F(" HTTP/1.1\r"));
        client.fastrprint(F("Host: ")); client.fastrprintln(host);
        client.fastrprint(F("epId: ")); client.fastrprintln(epid);
        client.fastrprint(F("authToken: ")); client.fastrprintln(auth);
        if(lang != NULL) {
            client.fastrprint("X-Language: "); client.fastrprint(lang);
        }
        if(limit != 0) {
            // TODO
        }
        if(content == 0) {
            /* Content flag not set so end headers */
            client.println();
        }
    } else {
#ifdef DEBUG
        Serial.println(F("Connection failed in header"));
#endif
        return IOTICE_ERROR;
    }
    return IOTICE_OK;
}


/** CC3000 ClientRequest */
IoticAgentCode ClientRequest(IOTICAGENT *agent, IoticAgentCrud crud, char *path, int8_t *postdata, size_t postdata_len, int limit, int offset, iotic_agent_payload *payload) {
    // postdata_len never gets used here

#ifdef DEBUG
    Serial.print("ClientRequest ");
    if(crud == IOTICCRUD_CREATE) Serial.print("CREATE ");
    if(crud == IOTICCRUD_LIST) Serial.print("LIST ");
    if(crud == IOTICCRUD_UPDATE) Serial.print("UPDATE ");
    if(crud == IOTICCRUD_DELETE) Serial.print("DELETE ");
    Serial.print(path);
    if(postdata != NULL) {
        Serial.print(" ");
        Serial.print((char*)postdata);
    }
#endif

    // get the cc3000 object from the agent struct
    IoticAgentCode ret = IOTICE_ERROR;
    if(agent != NULL) {
        iotic_agent *age = (iotic_agent*)agent;
        Adafruit_CC3000 *cc3000 = (Adafruit_CC3000*)age->cc3000;

        /* check cc3000 object is still connected */
        if(!cc3000->checkConnected()) {
#ifdef DEBUG
            Serial.println(F("ClientRequest: cc3000 object is not connected"));
#endif
            return IOTICE_ERROR;
        }

        /* connect to client */
        Adafruit_CC3000_Client client;

        if(connect_client(cc3000, age->host, client) == IOTICE_ERROR) {
#ifdef DEBUG
            Serial.println(F("ClientRequest: Client didn't connect"));
#endif
            return IOTICE_ERROR;
        }

        if(age->http_epid == NULL || age->http_authtoken == NULL) {
            return IOTICE_ERROR;
        }

        if(path == NULL) return IOTICE_ERROR;

        /* set the headers */
        if(crud == IOTICCRUD_CREATE) {
            if(postdata != NULL) {
                /* make POST request */
                if (send_http_headers(client, "POST ", age->host->host, path, age->http_epid, age->http_authtoken, NULL, limit, offset, 1) == IOTICE_ERROR) return IOTICE_ERROR;
                if (send_http_request(client, postdata) == IOTICE_ERROR) return IOTICE_ERROR;
                if (read_http_response(client, age->idle_timeout, payload) == IOTICE_ERROR) return IOTICE_ERROR;
            }
            else {
                goto bail;
            }
            return IOTICE_OK;
        }
        else if(crud == IOTICCRUD_LIST) {
            /* make GET request */
            if (send_http_headers(client, "GET ", age->host->host, path, age->http_epid, age->http_authtoken, NULL, limit, offset, 0) == IOTICE_ERROR) return IOTICE_ERROR;
            if (read_http_response(client, age->idle_timeout, payload) == IOTICE_ERROR) return IOTICE_ERROR;
            return IOTICE_OK;
        }
        else if(crud == IOTICCRUD_UPDATE) {
            if(postdata != NULL) {
                /* make PUT request */
                if (send_http_headers(client, "PUT ", age->host->host, path, age->http_epid, age->http_authtoken, NULL, limit, offset, 1) == IOTICE_ERROR) return IOTICE_ERROR;
                if (send_http_request(client, postdata) == IOTICE_ERROR) return IOTICE_ERROR;
                if (read_http_response(client, age->idle_timeout, payload) == IOTICE_ERROR) return IOTICE_ERROR;
            }
            else {
                goto bail;
            }
            return IOTICE_OK;
        }
        else if(crud == IOTICCRUD_DELETE) {
            /* make DELETE request */
            if (send_http_headers(client, "DELETE ", age->host->host, path, age->http_epid, age->http_authtoken, NULL, limit, offset, 0) == IOTICE_ERROR) return IOTICE_ERROR;
            if (read_http_response(client, age->idle_timeout, payload) == IOTICE_ERROR) return IOTICE_ERROR;
            return IOTICE_OK;
        }
        else {
            return IOTICE_ERROR;
        }
        send_close_request(client);

/* An error occured, free memory and bail! */
bail:
        disconnect_client(client);
    }
    return ret;
}

#endif /* IOTICAGENT_USE_CC3000 */
