
#include <Ethernet.h>

#include <ioticagent_http_ethernet.h>


#if defined (__arm__) && defined (__SAM3X8E__) // Arduino Due
// should use uinstd.h to define sbrk but on Arduino Due this causes a conflict
extern "C" char* sbrk(int incr);
int getFreeRam(void) {
  char top;
  return &top - reinterpret_cast<char*>(sbrk(0));
}
#else // AVR
int getFreeRam(void)
{
  extern int  __bss_end;
  extern int  *__brkval;
  int free_memory;
  if((int)__brkval == 0) {
    free_memory = ((int)&free_memory) - ((int)&__bss_end);
  }
  else {
    free_memory = ((int)&free_memory) - ((int)__brkval);
  }

  return free_memory;
}
#endif


// assign a MAC address for the ethernet controller. fill in your address here:
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };


void showFreeMem(void) {
  Serial.print("\nFree RAM: "); Serial.println(getFreeRam(), DEC);
}

void setup() {
  Serial.begin(115200);

  // start the Ethernet connection using a fixed IP address and DNS server:
  Ethernet.begin(mac);
}

void loop() {
  Ethernet.maintain();  // Maintain DHCP lease etc

  // print the Ethernet board/shield's IP address:
  Serial.print("My IP address: "); Serial.println(Ethernet.localIP());

  IOTICAGENT *agent = ioticagent_init();
  iotic_agent_payload payload;
  if (agent) {
    showFreeMem();

    ioticagent_setopt(agent, IOTICOPT_VERBOSE, 1);
    ioticagent_setopt(agent, IOTICOPT_HOST, "http://10.0.1.175");
    ioticagent_setopt(agent, IOTICOPT_PORT, 8118);
    ioticagent_setopt(agent, IOTICOPT_HTTP_EPID, "a81ffa72113e29b9f1ff210dd9725249");
    ioticagent_setopt(agent, IOTICOPT_HTTP_AUTHTOKEN, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");

    if(ioticagent_payload_init(&payload) == IOTICE_OK) {
      // entity_list
      IoticAgentCode res = ioticagent_entity_list(agent, &payload);
      if (res == IOTICE_OK) {
        Serial.print("\nentity_list OK: "); Serial.println(payload.payload);
      }
      ioticagent_payload_destroy(&payload);
    }

    if(ioticagent_payload_init(&payload) == IOTICE_OK) {
        // entity create
        IoticAgentCode res = ioticagent_entity_create(agent, "testthing", NULL, &payload);
        if(res == IOTICE_OK) {
            Serial.print("\nentity_create OK: "); Serial.println(payload.payload);
        }
        ioticagent_payload_destroy(&payload);
    }
    showFreeMem();

    if(ioticagent_payload_init(&payload) == IOTICE_OK) {
        // point create
        IoticAgentCode res = ioticagent_point_create(agent, IOTICFOC_FEED, "testthing", "data", &payload);
        if(res == IOTICE_OK) {
            Serial.print("\npoint_create OK: "); Serial.println(payload.payload);
        }
        ioticagent_payload_destroy(&payload);
    }
    showFreeMem();

    if(ioticagent_payload_init(&payload) == IOTICE_OK) {
        // point share
        IoticAgentCode res = ioticagent_point_share(agent, "testthing", "data", "timisafish", 10, &payload);
        if(res == IOTICE_OK) {
            Serial.print("\npoint_share OK: "); Serial.println(payload.payload);
        }
        ioticagent_payload_destroy(&payload);
    }
    showFreeMem();

    if(ioticagent_payload_init(&payload) == IOTICE_OK) {
        // point share
        IoticAgentCode res = ioticagent_feeddata(agent, &payload);
        if(res == IOTICE_OK) {
            Serial.print("\nfeeddata OK: "); Serial.println(payload.payload);
        }
        ioticagent_payload_destroy(&payload);
    }
    showFreeMem();

    if(ioticagent_payload_init(&payload) == IOTICE_OK) {
        // entity delete
        IoticAgentCode res = ioticagent_entity_delete(agent, "testthing", &payload);
        if(res == IOTICE_OK) {
            Serial.print("\nentity_delete OK: "); Serial.println(payload.payload);
        }
        ioticagent_payload_destroy(&payload);
    }
    showFreeMem();

    ioticagent_destroy(agent);
    showFreeMem();
  }

  Serial.println(F("\nSleeping 30s..."));
  int c = 0;
  while(c++ < 30) delay(1000);
}
