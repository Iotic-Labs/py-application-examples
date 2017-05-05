# Iotic-Labs ExtMon2: Simple External Feed Monitor
Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.
=======================================================

#### Table of contents
1. [What it does](#what-it-does)
2. [How it works](#how-it-works)
2. [Installing](#installation)
2. [Running](#running)

## Why?

Iotic Space can integrate data from many different sources.  The IoT being what it is, there is no guarantee that
these sources will be reliable.  The External Feed Monitor (version 2) or ExtMon2 shows a simple Red/Amber/Green (RAG)
webpage with the current status of sources in which you are interested.

It's called **External** Monitor because it runs outside of Iotic Space and therefore will keep monitoring
in the unlikely event of any part of Iotic Space failing.

## What?

### What it does

ExtMon allows you to choose some feeds in Iotic Space and to assign rules to them about how often you expect to see
them update.  For example if you expect a carpark feed to update every 5 minutes, you can set the maximum age to 300
seconds.  The system will then check to see if that feed has been received in the last 5 minutes and set its icon
to green.  If there's a problem and the feed hasn't been received, then (by default) the system will wait until two
times the max age until it goes amber and then three times before it goes red.  You can override these defaults
(obviously).


```
----------------                       ----------------   ----------------
|              |                       |              |   |              |
| Feed Source  | ---->IOTIC SPACE----> | Feed Monitor |   | Web Page     |
|              |                       |              |   |              |
----------------                       ----------------   ----------------
```

## How?

### How it works

There's a config file (extmon2.ini)[cfg/extmon2.ini] file for the monitor.  Fill in the basic config...

```ini
[extmon2]
wwwpath = ../www
template = templates/default.html
agent = ../cfg/agent.ini
```

|parameter|type|optional|comment|
|---|---|---|---|
|`wwwpath`|path|no|Path to web files directory|
|`template`|path|no|Path to your template HTML. Change this to change the layout, look and feel of the webpage|
|`agent`|path|no|Path to your agent credentials so the monitor can log into Iotic Space|


...and then add the feeds you want to monitor

```ini
feeds =
    testfeeds
    tfl_bikes

;   ...etc...

```

A feed definition can be as simple as this

```ini
[testfeeds]
guid = 798c20f92d005c12f2d7116999092520
max_age = 60

```
|parameter|type|optional|comment|
|---|---|---|---|
|`guid`|hex string|no|GUID of the feed you want to monitor|
|`max_age`|integer|no|Maximum time (in seconds) to wait before you expect your feed to publish|
|`warn_age`|integer|yes|Time before your feed shows amber (default max_age * 2)|
|`error_age`|integer|yes|Time before your feed shows amber (default max_age * 3)|
|`name`|string|yes|Override the feed you're monitoring's label (default actual feed label)|


### Installation

Download or clone the code from the repo.

#### Dependencies

To run the Monitor you'll need these dependencies

2. [IoticAgent](https://pypi.python.org/pypi/py-IoticAgent/0.4.1)
1. [rdflib](https://pypi.python.org/pypi/rdflib)

It's up to you how you install these and set your PYTHONPATH to access them.  I did from the root of this repo by
using the requirements.txt file to install the dependencies in the 3rd directory...
```bash
pip3 install -t 3rd -r requirements.txt
```
You can see how to [run your code](#running-your-source) later.


### Running your source
There's a [run script](src/run.sh) to run the Monitor.
Change the line to make sure PYTHONPATH includes all your dependencies and point the monitor at your `.ini` file
```bash
#!/bin/bash
PYTHONPATH=../3rd python3 -m ExtMon2 ../cfg/extmon2.ini
```
