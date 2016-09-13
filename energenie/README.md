# Energenie
Use @whaleygeek's OO pyenergenie code to talk to motion sensors, open sensors and monitoring plugs without a need for an interim csv file.


## Why?
Originally for FWIC16 Innovation Showcase, but now available for public use

Can be modified and adapted for other uses with any of the sensors controlled by @whaleygeek's stuff

## What?
Iotic/Energenies come in two flavours:

1. [mihome_iotic.py](./mihome_iotic.py) - Old-school version based on @whaleygeek's example: mihome_energy_monitor.py

2. [discovery.py](./discovery.py) - New-school version using Iotic ThingRunner and values - more properly OO

## How?
### 1) Download
The pyenergenie library from [@whaleygeek's github](https://github.com/whaleygeek/pyenergenie) and install on your pi as per his instructions.
*Note:* his stuff runs best on python2 at the time of writing.


### 2) Install
Python2 install of iotic agent and its dependencies on your pi
```bash
sudo pip install py-IoticAgent rdflib
```

### 3) Energenie Device Registration
Delete the contents of the `registry.kvs` file and then either run

#### For `mihome_iotic.py`

```
sudo python setup_tool.py
```
chose `mihome discovery mode` - you might need to press the pairing buttons on some devices (open sensor and motion sensor for example)

Edit the registry.kvs file rename your devices as to your own wishes.  You'll have to change the names in the code

#### For `discovery.py`
There's nothing to do, as the discovery is done for you


### 4) Save the Iotic example code and Iotic credentials
Put either of the mihome_iotic.py/discovery.py and your iotic agent's credentials  (.ini file) in
the src directory of @whaleygeek's code

*Either* edit the mihome_iotic.py to use your credential in the line

`with IOT.Client(config="your_credentials.ini") as client:`

or, in the discovery.py case:

`socket_runner = EnergenieSocketRunner(config='m2_fan.ini')`

### 5) Run
using `sudo` as the energenie radio needs access to the GPIOs
```
sudo python mihome_iotic.py
# - or -
sudo python discovery.py
```
