# test_share.py  13/12/2016  D.J.Whale
#
# An example two-pronged script that does a share and a feed update
# This is useful for testing multi-process setups.

import iot
import sys
import time

CONFIG_VARS = sys.argv[1:]

# SETUP THINGS
if 'producer' in CONFIG_VARS:
    left_thing = iot.create_thing("left_thing")

if 'consumer' in CONFIG_VARS:
    right_thing = iot.create_thing("right_thing")
    right_thing2 = iot.create_thing("right_thing2")

# SETUP ACTUAL POINTS
if 'producer' in CONFIG_VARS:
    #FEED PRODUCER
    f = left_thing.create_feed("interesting_feed")

if 'consumer' in CONFIG_VARS:
    #CONTROL
    c = right_thing.create_control("interesting_control")
    ##@c.when_new_attacher # not moved into Point() yet
    ##def attached(point):
    ##    print(point)

# SETUP BINDINGS
if 'producer' in CONFIG_VARS:
    # CONTROL PRODUCER
    if 'control' in CONFIG_VARS:
        ac = left_thing.find("right_thing", "interesting_control")
        print("app: control found")
        ac.attach()
        print("app: control attached")

if 'consumer' in CONFIG_VARS:
    #FEED FOLLOW
    if 'feed' in CONFIG_VARS:
        ff = right_thing.find("left_thing", "interesting_feed")
        print("app: feed found")
        ff.follow() # must be a Point for this to work
        print("app: feed bound")

        @ff.when_updated
        def update(sender, data):
            print("app: ff from:%s data:%s" % (str(sender), str(data)))

        ff2 = right_thing2.find("left_thing", "interesting_feed")
        print("app: feed2 found")
        ff2.follow()
        print("app: feed2 bound")

        @ff2.when_updated
        def update(sender, data):
            print("app: ff2 from:%s data:%s" % (str(sender), str(data)))

    #CONTROL ATTACH
    if 'control' in CONFIG_VARS:
        @c.when_updated
        def updated(sender, data):
            print("app: from:%s CONTROL DATA RECEIVED:%s" % (str(sender), str(data)))


# RUN
for i in range(3):
    if 'producer' in CONFIG_VARS:
        #FEED SEND
        if 'feed' in CONFIG_VARS:
            print("app: sharing data")
            f.share("SHARE DATA %d" % i)
            time.sleep(1)

        #CONTROL SEND
        if 'control' in CONFIG_VARS:
            print("app: actuating data %d" % i)
            ac.ask("ASK DATA %d" % i)
            time.sleep(1)

    if 'consumer' in CONFIG_VARS:
        iot.tick(rate=iot.FASTEST)

# END