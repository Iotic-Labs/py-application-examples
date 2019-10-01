/**
 * Iotic Labs Agent API C Library for HTTP(S) REST & MQTT
 * Copyright (c) 2016 Iotic Labs Ltd. All rights reserved
 * ------------------------------------------------------
 *
 */

#ifdef IOTICAGENT_USE_ETHERNET

#include <Ethernet.h>

#include "agent.h"


int find_response_length(EthernetClient &client) {
    // search for "Content-Length: " in response_header
    char res_header[20];
    char *res_length;
    char *look_for = "Content-Length: ";
    char searching[17];
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


/** read_http_request */
IoticAgentCode read_http_response(EthernetClient &client, int idle_timeout, iotic_agent_payload *payload) {
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


/** send_http_request */
IoticAgentCode send_http_request(EthernetClient &client, int8_t *request_msg) {
    if (client.connected()) {
        if (request_msg) {
            client.println("Content-Type: application/json; charset=utf-8");
            client.print("Content-Length:");
            client.println(strlen((char*)request_msg));
            client.println();
            client.println((char*)request_msg);
        }
    } else {
#ifdef DEBUG
        Serial.println(F("Connection failed"));
#endif
        return IOTICE_ERROR;
    }
    return IOTICE_OK;
}


/** send_close_request */
void send_close_request(EthernetClient &client) {
    client.println("Connection: close");
    client.println();
}


/** send_http_headers */
IoticAgentCode send_http_headers(EthernetClient &client, char *request_type, char *host, char *path, char *epid, char *auth, char *lang, int limit, int offset, int content) {
    if (client.connected()) {
        client.print(request_type);
        client.print(path);
        client.println(F(" HTTP/1.1\r"));
        client.print(F("Host: ")); client.println(host);
        client.print(F("epId: ")); client.println(epid);
        client.print(F("authToken: ")); client.println(auth);
        if(lang != NULL) {
            client.print("X-Language: "); client.print(lang);
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

/** Arduino Ethernet shield ClientRequest */
IoticAgentCode ClientRequest(IOTICAGENT *agent, IoticAgentCrud crud, char *path, int8_t *postdata, size_t postdata_len, int limit, int offset, iotic_agent_payload *payload) {
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

    IoticAgentCode ret = IOTICE_ERROR;
    if(agent != NULL) {
        iotic_agent *age = (iotic_agent*)agent;
        if(age->host == NULL) {
            return IOTICE_ERROR;
        }

        EthernetClient client;
        byte ip[] = { 10, 0, 1, 175 };
        if(!client.connect(ip, age->host->port)) {
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
            }
            else {
                goto bail;
            }
        }
        else if(crud == IOTICCRUD_LIST) {
            /* make GET request */
            if (send_http_headers(client, "GET ", age->host->host, path, age->http_epid, age->http_authtoken, NULL, limit, offset, 0) == IOTICE_ERROR) return IOTICE_ERROR;
        }
        else if(crud == IOTICCRUD_UPDATE) {
            if(postdata != NULL) {
                /* make PUT request */
                if (send_http_headers(client, "PUT ", age->host->host, path, age->http_epid, age->http_authtoken, NULL, limit, offset, 1) == IOTICE_ERROR) return IOTICE_ERROR;
                if (send_http_request(client, postdata) == IOTICE_ERROR) return IOTICE_ERROR;
            }
            else {
                goto bail;
            }
        }
        else if(crud == IOTICCRUD_DELETE) {
            /* make DELETE request */
            if (send_http_headers(client, "DELETE ", age->host->host, path, age->http_epid, age->http_authtoken, NULL, limit, offset, 0) == IOTICE_ERROR) return IOTICE_ERROR;
        }
        else {
            return IOTICE_ERROR;
        }

        while(!client.available()) delay(250);
        if(read_http_response(client, age->idle_timeout, payload) == IOTICE_ERROR) return IOTICE_ERROR;
        else ret = IOTICE_OK;

        send_close_request(client);

/* An error occured, free memory and bail! */
bail:
        client.stop();
    }
    return ret;
}

#endif /* IOTICAGENT_USE_ETHERNET */
