/* This example shows a simple followall for arduino
   Initialization
   Optional: SSID scan
   AP connection
   DHCP printout
   Optional: DNS lookup

   agent poll feeddata
   - if found number flash LED n times

   Disconnect
*/

#define TINYDUINO
// #define UNO

#define WLAN_SSID       "wifi"           // cannot be longer than 32 characters!
#define WLAN_PASS       "password"
// Security can be WLAN_SEC_UNSEC, WLAN_SEC_WEP, WLAN_SEC_WPA or WLAN_SEC_WPA2
#define WLAN_SECURITY   WLAN_SEC_WPA2


#include <Adafruit_CC3000.h>
#include <ccspi.h>
#include <SPI.h>
#include <string.h>
#include "utility/debug.h"

// Include the IoticAgent HTTP & CC3000
#include <ioticagent_http_cc3000.h>


#ifdef TINYDUINO
#define ADAFRUIT_CC3000_IRQ   2
#define ADAFRUIT_CC3000_VBAT  A3
#define ADAFRUIT_CC3000_CS    8
#endif

#ifdef UNO
#define ADAFRUIT_CC3000_IRQ   3
#define ADAFRUIT_CC3000_VBAT  5
#define ADAFRUIT_CC3000_CS    10
#endif

// Use hardware SPI for the remaining pins
// On an UNO, SCK = 13, MISO = 12, and MOSI = 11
Adafruit_CC3000 cc3000 = Adafruit_CC3000(ADAFRUIT_CC3000_CS, ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT,
                                         SPI_CLOCK_DIVIDER); // you can change this clock speed

#define IDLE_TIMEOUT_MS  3000


void showFreeMem(void) {
  Serial.print("\nFree RAM: "); Serial.println(getFreeRam(), DEC);
}

/**************************************************************************/
/*!
    @brief  Sets up the HW and the CC3000 module (called automatically
            on startup)
*/
/**************************************************************************/
uint32_t ip;

void setup(void)
{
  Serial.begin(115200);

  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);

  cc3000.disconnect();
}

void setup_wifi(void) {
  Serial.println(F("\nHello, CC3000!"));
  cc3000 = Adafruit_CC3000(ADAFRUIT_CC3000_CS, ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT,
                           SPI_CLOCK_DIVIDER); // you can change this clock speed

  showFreeMem();

  /* Initialise the module */
  Serial.println(F("\nInitializing CC3000..."));
  if (!cc3000.begin()) {
    Serial.println(F("Couldn't begin()! Check your wiring?"));
    while (1);
  }

  // Optional SSID scan
  // listSSIDResults();

  Serial.print(F("\nAttempting to connect to ")); Serial.println(WLAN_SSID);
  if (!cc3000.connectToAP(WLAN_SSID, WLAN_PASS, WLAN_SECURITY)) {
    Serial.println(F("Failed!"));
    while (1);
  }

  Serial.println(F("Connected!"));

  /* Wait for DHCP to complete */
  Serial.println(F("Request DHCP"));
  while (!cc3000.checkDHCP()) {
    delay(100); // ToDo: Insert a DHCP timeout!
  }

  /* Display the IP address DNS, Gateway, etc. */
  while (! displayConnectionDetails()) {
    delay(1000);
  }
}

void loop(void)
{
  showFreeMem();
  setup_wifi();

  IOTICAGENT *agent = ioticagent_init();
  iotic_agent_payload payload;
  if (agent) {
    showFreeMem();

    ioticagent_setopt(agent, IOTICOPT_CC3000, (void*)&cc3000);
    ioticagent_setopt(agent, IOTICOPT_VERBOSE, 1);
    //ioticagent_setopt(agent, IOTICOPT_HOST, "http://ux305fa");
    ioticagent_setopt(agent, IOTICOPT_IP, cc3000.IP2U32(10, 0, 1, 175));
    ioticagent_setopt(agent, IOTICOPT_PORT, 8118);
    ioticagent_setopt(agent, IOTICOPT_HTTP_EPID, "a81ffa72113e29b9f1ff210dd9725249");
    ioticagent_setopt(agent, IOTICOPT_HTTP_AUTHTOKEN, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");

    if (ioticagent_payload_init(&payload) == IOTICE_OK) {
      // entity create
      IoticAgentCode res = ioticagent_entity_create(agent, "arduino followall", NULL, &payload);
      if (res == IOTICE_OK) {
        Serial.print("\nentity_create OK: "); Serial.println(payload.payload);
      }
      ioticagent_payload_destroy(&payload);
    }
    showFreeMem();

    int c = 0;
    while (c++ < 6) {
      delay(2000);

      if (ioticagent_payload_init(&payload) == IOTICE_OK) {
        // point share
        IoticAgentCode res = ioticagent_feeddata(agent, &payload);
        if (res == IOTICE_OK) {
          Serial.print("\nfeeddata OK: "); Serial.println(payload.payload);
          if(strlen(payload.payload) > 2) {
            int val = parse_payload_for_value(&payload);
            if(val != -1) {
              Serial.print("\nFound val: "); Serial.println(val, DEC);
              for(int c = 0; c < val; c++) {
                digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
                delay(1000);                       // wait
                digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
                delay(500);                        // wait
              }
            }
          }
        }
        ioticagent_payload_destroy(&payload);
      }
      showFreeMem();

      delay(8000);
    }

    ioticagent_destroy(agent);
    showFreeMem();
  }

  /* You need to make sure to clean up after yourself or the CC3000 can freak out */
  /* the next time your try to connect ... */
  Serial.println(F("\nDisconnecting"));
  cc3000.disconnect();

  Serial.println(F("\nSleeping 30s..."));
  int c = 0;
  while(c++ < 30) delay(1000);
}

/** Parse payload for "value": X and return X as int or -1 */
int parse_payload_for_value(iotic_agent_payload *payload) {
  if (payload != NULL) {
    char value[] = "\"value\": ";
    char *pos = strstr(payload->payload, value);
    if(pos != NULL) pos += strlen(value);
    char result[4];
    for(int c = 0; c < 3; c++) {
      result[c+1] = 0;
      if(isdigit((pos+c)[0])) result[c] = (pos+c)[0];
      else break;
    }
    return atoi(result);
  }
  return -1;
}

/**************************************************************************/
/*! @brief  Begins an SSID scan and prints out all the visible networks
*/
/**************************************************************************/
void listSSIDResults(void) {
  uint32_t index;
  uint8_t valid, rssi, sec;
  char ssidname[33];

  if (!cc3000.startSSIDscan(&index)) {
    Serial.println(F("SSID scan failed!"));
    return;
  }

  Serial.print(F("Networks found: ")); Serial.println(index);
  Serial.println(F("================================================"));

  while (index) {
    index--;

    valid = cc3000.getNextSSID(&rssi, &sec, ssidname);

    Serial.print(F("SSID Name    : ")); Serial.print(ssidname);
    Serial.println();
    Serial.print(F("RSSI         : "));
    Serial.println(rssi);
    Serial.print(F("Security Mode: "));
    Serial.println(sec);
    Serial.println();
  }
  Serial.println(F("================================================"));

  cc3000.stopSSIDscan();
}

/**************************************************************************/
/*! @brief  Tries to read the IP address and other connection details
*/
/**************************************************************************/
bool displayConnectionDetails(void) {
  uint32_t ipAddress, netmask, gateway, dhcpserv, dnsserv;

  if (!cc3000.getIPAddress(&ipAddress, &netmask, &gateway, &dhcpserv, &dnsserv)) {
    Serial.println(F("Unable to retrieve the IP Address!\r\n"));
    return false;
  }
  else {
    Serial.print(F("\nIP Addr: ")); cc3000.printIPdotsRev(ipAddress);
    Serial.print(F("\nNetmask: ")); cc3000.printIPdotsRev(netmask);
    Serial.print(F("\nGateway: ")); cc3000.printIPdotsRev(gateway);
    Serial.print(F("\nDHCPsrv: ")); cc3000.printIPdotsRev(dhcpserv);
    Serial.print(F("\nDNSserv: ")); cc3000.printIPdotsRev(dnsserv);
    Serial.println();
    return true;
  }
}

