# first_contact_template.py - 19/12/16

#questions -
#Do we need to run iot in background thread?

# Next steps:
# remake as default only script

## NOTE: I'm using the SenseHAT in testing as it has a good range of functionality,
## ...including fast-polling sensors and its own module (both common areas it's easy
## ...to run into difficulty ioticizing). The first template will not be SenseHAT dependant,
## ...but it will be the first extension (that isn't bare GPIO). If we can take these next steps with
## ...the SenseHAT, the same techniques are likely to work in many other similar circumstances.
## ...test by uncommenting SenseHAT specific functionality. It is the GENERIC functionality that is critical.
## ...I am using SenseHAT to test in real use to save time.

#DEFER:
#DEFER Toggle single Feed throttle on/off (affects basic demo interoperability, will sometimes prevent)
#DEFER Toggle single Control throttle on/off (affects basic demo interoperability, will sometimes prevent)
#DEFER Toggle single Value throttle on/off (DANGER affects basic demo interoperability, will sometimes prevent. #Limits use for building physical demos - will only be interoperable with known Things at data level. Cannot #interact with non-owned Things in the same way as owned. Does not represent Iotic best-practice. No workaround in #UI.)
#DEFER Set minimal metadata for Thing, Feed, Control (can set in UI for now)
#DEFER Set Values metadata (DANGER affects basic demo interoperability, will sometimes prevent. Limits use for #building physical demos - will only be interoperable with known Things at data level. Cannot interact with non-#owned Things in the same way as owned. Does not represent Iotic best-practice. No workaround in UI.)
#DEFER Get metadata from remote Thing, Feed, Control (limits development)
#DEFER Get Values metadata (DANGER affects basic demo interoperability, will sometimes prevent. Limits use for #building physical demos - will only be interoperable with known Things at data level. Cannot interact with non-#owned Things in the same way as owned. Does not represent Iotic best-practice. No workaround in UI.)
#DEFER Tag (not listed as PRI-A)
#DEFER Public/unlisted as no metadata yet
#DEFER run in foreground/background (DANGER may limit ability to quick-create physical demos)

##TODO Minimal ability to configure default Thing/Feed/Point outside script - config .ini (prevents automatic Thing creation on reboot)
## ...limits non-coding "just_start" activity, cannot turn on and connect out of box) #DW can make work with .ini
##TODO Equivalent to "control-all" (prevents demo interoperability) #DW needs further discussion with MW, LT  -> DW to put into iot api functionality below
##TODO Confirm that this is the best-practice "first-contact" template when possible.

#TODO NOTE: Terminology - value / values may be a confusion

#TODO: "private" on dev portal change to "unlisted"

# NON-IOTIC SETUP --------------------------------------------------------------

import time
import random
from sense_hat import SenseHat
sense = SenseHat()

# CONNECT TO IOTIC SPACE -------------------------------------------------------

# Import IOT library and auto-connect to IoticSpace
import iot

# CREATE AND ADVERTISE THING -----------------------------------------------------------------

# CREATE THING ---
#TODO Naming outside script (configuration ini) and best-practice use - DW to make work with configuration ini

mw_thing = iot.create_thing("mw") #yep

# MAKE MY THING SEARCHABLE BY OTHERS ---

mw_thing.show() # public #yep
#thing.hide() # unlisted

# TODO Set minimal metadata when available (can do in UI to start with)

# SET DEMO MODE ---

# TODO Toggle single Feed throttle on/off when available
# TODO Toggle single Control throttle on/off when available
# TODO Toggle single Value throttle on/off when available
## ..(default any numerical data converted to int or float, whichever is best-practice for most basic interoperability)

#TODO Configure Feed and control if needed as separate section (may not be needed when .ini working) #DW to send notes when done
## ...avoid need for feed/control based stuff outside their tempate section if at all possible, or changes template useage

# ADVERTISING A FEED AND SHARING DATA ------------------------------------------

# CREATE A FEED ---

#TODO Naming outside script (configuration ini) and best-practice use #DW can make work with .ini

mw_feed = mw_thing.create_feed("mw_feed") #DW - name in ini #yep

#ADVERTISE FEED ---

#TODO Set minimal metadata when available (can do in UI to start with)

# DEFINE HANDLERS FOR BIND AND UNBIND ---
# Default Thing accepts all Followers

#NOTE just auto follow accepted - rejecting not yet supported in infra

@mw_feed.when_new_follower #yep
def new_follower(follower): #DW: probably this
    print ("New follower:") #TODO follower data

@mw_feed.when_lost_follower #yep
def unfollowed(follower): #DW: probably this
    print ("Unfollowed:") #TODO follower data?)

# GENERATE DATA ---

#TODO Best-practice way to generate data to be able to share timed OR on command. #DW will send notes - proposed changes to simplify

#Use for testing if no SenseHAT
# my_feed_data = random.randint(0,10)

#TODO Set values when available

# CONFIGURE FEED --- ####NOPE

#TODO Best-practice way to do this in this template to achieve required behaviour  #DW will send notes - proposed changes to simplify

#1 this is the default if you do nothing else
my_feed.set_mode(iot.IMMEDIATE) # in new template,

#2 this will share only every 2 seconds
# my_feed.set_mode(iot.TIMED)
# my_feed.rate = 2

#3 this will share only when you call trigger()
# my_feed.set_mode(iot.TRIGGERED)

# To trigger sending of a cached feed value
# feed.trigger() # note, need brackets
# or
# sense_hat.some_event = feed.trigger # note, no brackets

# ACTION TO SHARE DATA ---

#TODO Best-practice way to do this in this template to achieve required behaviour #DW will send notes - proposed changes to simplify

# share on trigger
#def feed_share_on_trigger():
#  iot.feed.send_on_change = True
#  sense.stick.direction_up = feed.trigger
sense.stick.direction_down = control_ask_on_trigger

# timed share with adjustable rate
# def feed_share_timed():
## may not be needed?

# FOLLOWING A FEED AND USING THE DATA ------------------------------------------
## Default Thing automatically reacts to all Feeds arranged inside or outside the script, eg in Space UI
#TODO Best-practice way to do this in this script. Currently it by omission to use defaults. #DW will send notes - proposed changes to simplify

# AQUIRE AND FOLLOW A FEED ---
## You can also follow specific Feeds inside the script and create handlers for those.

#TODO when available DW to send notes #DW will send notes - proposed changes to simplify
# feed_follow = auto

# Test by following your own Feed
feed_follow = iot.find("mw", "mw_feed").follow() # follow mw_feed on thing mw
# feed_follow = iot.find("mw_feed").follow() # follow mw_feed on my Thing
#if no mw_feed, it will fail.
#if no mw will look for mw_feed on "thing"

#Find and Follow by GPID
# feed_follow = iot.find("GPID").follow()

#Find and Follow by searching
# feed_follow = iot.search("cambridge", "temperature", "ambient" 1).follow() # when implemented
#DW: we haven't really specified how search will work yet.

# Find and Follow Feeds from Things you own by Local Point ID (in same Container only)
# feed_follow = iot.find("THING NAME", "LOCAL POINT ID").follow()

# DEFINE HANDLERS FOR INCOMING DATA ---
#TODO Best-practice way to handle "followall" #DW will send notes - proposed changes to simplify

# test using your own feed
@feed_follow.when_updated #DW yep
def update(sender, data): #DW says sender will at least be unique
    print("own feed data:%s" % str(data))
    try:
        num = int(data)
    except:
        num = 0
    sense.show_letter("F", text_colour = [0, 0, 255])
    time.sleep(0.3)
    sense.clear()

#TODO QUESTION: Does time.sleep here cause problems? If so, is this the point where we start to need to run iot
## ...in background thread?

# incoming data from anything you follow that doesn't have a specific handler
# NOTE currently needed to handle followall as separate from other acquired feeds -
## ..this is a workaround
@iot.when_feed_updated
#it changes the default handler for any feed that does not have a handler.
#the default if you don't have this, is it prints on console

def update(sender, data):
    print("feed data received:%s" % str(data))
    sense.show_letter("F", text_colour = [0, 0, 255])
    time.sleep(0.3)
    sense.clear()

#TODO: Basic remote metadata - display / use eg Label/Description
#TODO: Values (essential for interoperability)

#TODO: Generic operation on incoming numerical data using Values when available (basic interoperability)
#DW5: see my notes on datatypes below
#0. PRESENT: data has arrived
#1. PRINTABLE: data can be displayed in some fixed human readable form
#2. COMPARABLE: dataA and dataB are same or different
#3. SORTABLE: dataA and dataB are greater or less than each other
#4. MAGNITUDE: dataA and dataB are different by this amount
#
#d = iot.compare(thisData, prevData)
#print(d)
#["comparable", "different", "bigger", "longer", "shorter"]
#
#if "comparable" in d: ...
#if "different" in d: ...
#if "bigger" in d: ...
#if "longer" in d: ...
#if "shorter" in d: ...
#
#s = iot.size(thisData)
#print(s)
#20 (size of number, length of string, number of pixels in image, length of sound...)

# OFFERING A CONTROL AND BEING ACTUATED (ASK) ----------------------------------
# Default Thing can be actuated by any controllers attached to it.

# CREATE A CONTROL ---
#TODO Naming outside script (configuration ini) and best-practice use #DW can make work in ini

mw_control = mw_thing.create_control("mw_control") # DW name in .ini instead

# DEFINE HANDLERS FOR INCOMING DATA (ACTION WHEN CONTROLLED)
#CATCHALL

@iot.when_control_updated # all controls go here - except the explicit one VV
#overrides the built in default handler, which anything without a handler will call
def update(sender, data):
    print("control data:%s" % str(data))
    sense.show_letter("C", text_colour = [255, 0, 0])
    time.sleep(0.3)
    sense.clear()

# DEFINE HANDLERS FOR INCOMING DATA (ACTION WHEN CONTROLLED)
#SPECIFIC

@mw_control.when_updated # my control receives data here.  #yes
def update(sender, data):
    print("control data:%s" % str(data))
    sense.show_letter("C", text_colour = [0, 255, 0])
    time.sleep(0.3)
    sense.clear()

#DEFINE HANDLERS FOR BIND AND UNBIND ---

# TODO NOTE: auto accept only - reject not suported by infra
my_attached = []

@mw_thing.when_have_attached #uses mw_thing.when_have_attached
def attached(other_thing):
    print(other_thing)
    my_attached.append(other_thing)

@mw_thing.when_have_detached # I have just detached from an existing control
def detached(other_thing):
    print(other_thing)
    my_attached.remove(other_thing)

@iot.when_new_attacher
def new_attacher(attaching_control): #DW probably this
    print("New Control attach:") #TODO data about controller?

@iot.when_lost_attacher
def controller_detached(detaching_control):
    print("controller detached:") #TODO data about controller?

# ATTACHING TO A CONTROL AND ACTUATING (ASK) -----------------------------------
#TODO "control-all" - from todays discussion DW, MW, LT Monday #DW needs further input
#TODO Best-practice way of doing this from todays discussion #DW needs further input
#NOTE - fan-out possible

# AQUIRE AND ATTACH TO A CONTROL ---
#TODO Best-practice way of doing this from todays discussion # DW needs further input
## Request to attach to specific Controls within your script, and create handlers to actuate those.

#Test by following your own Control
control_attach = iot.find("mw", "mw_control").attach() # yep, but if in same script, it will use your thing if no thing specified YEP.
my_attached.append(control_attach)

#Find and Attach by GPID
#control_attach = iot.find("GPID").attach()

#Find and Attach by searching
#control_attach = iot.search("cambridge", "gumball", "dispenser", 1).attach() # when implemented

# Find and Attach to Things you own by local Point ID (in same Container only)
#control_attach = iot.find("THING NAME", "LOCAL POINT ID").attach()

#TODO: Basic remote metadata - display / use eg Label/description when available

#GENERATE CONTROL DATA ---
#TODO Best way to actuate control (ask) timed, and on command. #DW needs further input MW,LT

control.send_on_change = False
control.value = my_control_data #DW7 caches value until later triggered
#TODO We need to share a live sensor reading / generate the random number when I trigger a share. Does this do that?
## ...if not please change to the way that does. #DW has worked out how to do this

# CONFIGURE CONTROL ---
#TODO Best-practice way to do this in this template #DW will send notes - proposed changes to simplify

#1 this is the default if you do nothing else #DW will send notes - proposed changes to simplify
def configure_control_ask_immediate():
    control.rate = None
    control.send_on_change = True

#2 this will ask only every 10 seconds
def configure_control_ask_timed():
    control.rate = 10
    control.send_on_change = False

#3 this will share only when you call trigger()
def configure_control_ask_triggered():
    #by default feed.rate is None (off), but you could override it
    #explicitly if switching back and forth between two modes
    #control.rate = None
    control.send_on_change = False

# To trigger sending of a cached feed value
# control.trigger() # note, need brackets
# or
# sense_hat.some_event = control.trigger # note, no brackets

# ACTION TO ACTUATE CONTROL ---
#TODO Best-practice way to do this in this template #DW will send notes - proposed changes to simplify
sense.stick.direction_down = control_all #DW YEP


def control_all():
    my_control_data = random.randint(0,10) # initially suggested booloean - now is int - why?
    for control in my_attached:
        control.ask(my_control_data)

   # so I think we are confusing  behaviour with implementation.
   #the behaviour is fine.
   #i think this should be implemented inside iot.  # fair enough, but this was just explain to LT
   #but yes I agree with how it should work. good. # GOOD

# def control_ask_timed():
#may not be needed? all in comfigure? Clarity needed here.


#-------------------------------------------------------------------------------

#----- LOOPING PROGRAM
# main loop - CTRL-C to exit
##TODO correct loop for above Dependent on DW updates. This is wrong.

configure_control_ask_immediate():

while True:
    try:
        my_feed_data = sense.get_pressure()  # {"pressure": sense.get_pressure()}
        mw_feed.value = my_feed_data # or feed.share(my_feed_data)
        time.sleep(10)
        # FEED SHARE
        # CONTROL ACTUATE
    except KeyboardInterrupt:
        sense.clear()
        break


# END
