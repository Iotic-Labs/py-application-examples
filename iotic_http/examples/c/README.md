#Iotic Labs Agent API C Library for HTTP(S) REST & MQTT
Copyright (c) 2016 Iotic Labs Ltd. All rights reserved
------------------------------------------------------

##Using the library

First `#include "agent.h"` in your application.

Next add `#define`s to use parts of the library

*For Example:* For HTTP(S) On desktop *or* cc3000 on arduino, using `gcc -D` for example
- `#define IOTICAGENT_USE_LIBCURL`  - or -
- `#define IOTICAGENT_USE_CC3000`

or for MQTT on desktop using libmosquitto
- `#define IOTICAGENT_USE_LIBMOSQUITTO`


###Desktop / Linux

#### Get the tools
`sudo apt-get install build-essential splint doxygen valgrind libcunit1-dev`

2. Desktop Linux HTTP(S) library
`sudo apt-get install libcurl4-openssl-dev`

3. Desktop Linux MQTT Library
`sudo apt-get install libmosquitto-dev`


###Arduino IDE (If using example_code.git)

- Build the library (if using example_code.git)
```
cd ~/example_code/libioticagent/src/arduino
./make_arduino_library.sh
```

- Make a link to the library
```
cd Arduino/libraries
ln -sfv ~/example_code/libioticagent/src/arduino IoticAgent
```

- Include the library in the IDE (Sketch -> Include Library -> IoticAgent)
  - Remove the `#include <agent.h>` line from your Sketch
  - Add the right header EG `#include <ioticagent_http_cc3000.h>` which includes the defines to build http & cc3000

