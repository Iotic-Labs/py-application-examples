# Iotic Labs MQTT bridge for QAPI
Copyright (c) 2016 Iotic Labs Ltd. All rights reserved.
-------------------------------------------------------

The MQTT bridge provides a set of topics to interface to the Iotic Labs Queue API.

MQTT broker host and port can be configured in the agent.ini or default localhost 1883
will be used.


### Limitations.
1. MQTT bridge represents exactly One agent

## Requires
- paho-mqtt https://eclipse.org/paho/clients/python/
- py-IoticAgent https://github.com/Iotic-Labs/py-IoticAgent


## Config Options
If not specified localhost & 1883 will be used.

```ini
[mqtt]
host = localhost
port = 1883

; [agent] contents of ini
[agent]
```

## MQTT Topics
See wiki and example.sh.
