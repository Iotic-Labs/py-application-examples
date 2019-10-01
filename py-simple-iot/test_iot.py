# test_iot.py  11/12/2016  D.J.Whale
#
# A simple smoke test for iot. Expect it to go up in flames.

import iot
import time

# We don't use unittest.TestCase because we can't guarantee completely
# resetting the state of all modules.
# So, pass in the test name/number to run one test in a sandbox

# You can pass space=DB on sys.argv and it will make iot.py use a different space
# but put a 'end' to mark the end of the test names so that it does not
# get executed as a test (and fail!)
# e.g.
#   python test_iot.py test1 test2 test3 end space=DB


#------------------------------------------------------------------------------
#EXAMPLE 1: Simplest Iotic script
#
# Behaviour
#   1. auto connects and authenticates to IoticSpace
#   2. Will create a default thing, a default feed, and a default control.
#   3. The thing will be public.
#   4. any follows done elsewhere will cause default routing to a default update handler
#   5. any attaches done elsewhere will cause default routing to a default update handler
#   6. default update handler will print the data on the console
#   7. CTRL-C stops the script, and auto-stops with iot.stop() before exit

def example1():
    ##import iot
    print("press CTRL-C to stop, or will run for 5 seconds")
    iot.run(for_time=5) #run for 5 seconds while testing


#------------------------------------------------------------------------------
#EXAMPLE 1b: tests feed follow and unfollow

def example1b():
    ##import iot
    lhs_thing = iot.create_thing("lhs_thing")
    rhs_thing = iot.create_thing("rhs_thing")

    lhs_feed = lhs_thing.create_feed("lhs_feed")

    @lhs_feed.when_new_follower
    def new_follower(follower):
        print("lhs_feed.when_new_follower: %s" % follower.__repr__())

    @lhs_feed.when_unfollowed
    def unfollowed(follower):
        print("lhs_feed.when_unfollowed: %s" % follower.__repr__())

    #Make UUT follow some external feed: should instigate routing to default handler
    rhs_follower = rhs_thing.find("lhs_thing", "lhs_feed")

    @rhs_follower.when_have_followed
    def have_followed(feed):
        print("rhs_follower.when_have_followed: %s" % feed.__repr__())

    @rhs_follower.when_have_unfollowed
    def have_unfollowed(feed):
        print("rhs_follower.when_have_unfollowed: %s" % feed.__repr__())

    rhs_follower.follow()

    @rhs_follower.when_updated
    def updated(sender, data):
        print("rhs_follower.when_updated: %s %s" % (sender.__repr__(), str(data)))

    #Test script shares some data: UUT should handle the incoming data with default handler
    lhs_feed.share("FROM FEED, AFTER FOLLOW")

    iot.run(for_time=4)

    rhs_follower.unfollow()

    # sending data after unfollow should reflect back to feed handler
    @lhs_feed.when_updated
    def update(sender, data):
        print("lhs_feed.when_updated: %s %s" % (sender.__repr__(), str(data)))

    lhs_feed.share("FROM FEED, AFTER UNFOLLOW")

    iot.run(for_time=2)



#------------------------------------------------------------------------------
#EXAMPLE 1c

def example1c():
    ##import iot
    lhs_thing = iot.create_thing("lhs_thing")
    rhs_thing = iot.create_thing("rhs_thing")

    rhs_control = rhs_thing.create_control("rhs_control")

    @rhs_control.when_new_attacher
    def new_attacher(attacher):
        print("rhs_control.new_attacher: %s" % attacher.__repr__())

    @rhs_control.when_detached
    def detached(attacher):
        print("rhs_control.detached: %s" % attacher.__repr__())

    @rhs_control.when_updated
    def updated(sender, data):
        print("rhs_control.updated: %s %s" % (sender.__repr__(), str(data)))

    #Attach test script to UUT default control
    lhs_attached = lhs_thing.find("rhs_thing", "rhs_control")

    @lhs_attached.when_have_attached
    def attached(control):
        print("lhs_attached.attached: %s" % control.__repr__())

    @lhs_attached.when_have_detached
    def detached(control):
        print("lhs_attached.detached: %s" % control.__repr__())

    @lhs_attached.when_updated
    def update(sender, data):
        print("lhs_attached.updated: %s %s" % (sender.__repr__(), str(data)))

    lhs_attached.attach()
    ##lhs_thing.dump()
    ##rhs_thing.dump()
    #Actuate the control with an ask()
    print("app: ASK")
    lhs_attached.ask("ASK")

    iot.run(for_time=2)

    #Actuate the control with a tell()
    lhs_attached.tell("TELL")
    iot.run(for_time=2)

    #Detach the control
    lhs_attached.detach()

    # Sending data to an unbound control should reflect back to own default handler
    lhs_attached.ask("DATA SENT AFTER DETACH")
    iot.run(for_time=2)

#------------------------------------------------------------------------------
#EXAMPLE 1d: Simplest Iotic script with auto tick

def example1d():
    ##import iot
    iot.start()
    iot.share(10) # should auto tick, and if no followers, will loopback
    iot.stop()


#------------------------------------------------------------------------------
#EXAMPLE 2: Simplest single feed share then exit

def example2():
    ##import iot
    #no looper started, so first interaction auto-starts the looper

    ##iot.start()
    ##iot.tick()
    iot.share(10)
    ##iot.tick()
    ##iot.stop()

    #no explicit iot.stop, so atexit will do it for us
    #END


#------------------------------------------------------------------------------
#EXAMPLE 2b: Simplest single feed share with a follower

#TESTED:
#If you use two feed followers on the same thing (as we do below)
#you'll get twice the data coming in, as the iot library cannot
#differentiate where to send them at the moment, so it sends them
#to all. Because DBSpace and MemorySpace do the fanout at the
#sending end, this multiplies the actual shares. It's a know problem
#we might just ignore for now as it will go away in IoticSpace.

def example2b():
    print("TEST DISABLED")
    ##import iot

    ##real_feed = iot.create_feed("f")

    ##followed_feed1 = iot.find("f").follow()
    ##followed_feed2 = iot.find("f").follow()

    ##@followed_feed1.when_updated
    ##def update(sender, data):
    ##    print("feed1 update from:%s data:%s" % (sender.__repr__(), str(data)))

    ##@followed_feed2.when_updated
    ##def update(sender, data):
    ##    print("feed2 update from:%s data:%s" % (sender.__repr__(), str(data)))

    ##real_feed.share(10)

    #END

#------------------------------------------------------------------------------
#EXAMPLE 3: Simplest single control actuate then exit

#OUTPUT
#control received:DO IT
#iot:stopping...
#iot:stopped.
#/OUTPUT

def example3():
    ##import iot

    control1234 = iot.create_control("control1234")

    @control1234.when_updated
    def update(sender, data):
        print("control1234.when_updated: %s %s" % (sender.__repr__(), str(data)))
        #return False # NACK
        #return True # ACK
        #return None # TIMEOUT
        #return "no way" # ARBITRARY ERROR

    yourcontrol = iot.find("control1234")
    yourcontrol.attach()

    yourcontrol.tell("DO IT") # auto run_background()
    #END # atexit calls stop()

#------------------------------------------------------------------------------
#EXAMPLE 4: Simplest single feed create
#NOTE, this looks identical to an earlier test.

def example4():
    ##import iot

    # thing.feed is created by default if you don't create a feed yourself.
    # iot.run() done automatically on first iotic interaction
    iot.share("hello")
    #END
    # atexit(iot.stop()) done automatically, scheduled by auto-start behaviour


#------------------------------------------------------------------------------
#EXAMPLE 5: Simplest single control actuate with no ref in code

def example5():
    ##import iot

    control5678 = iot.create_control("control5678")

    yourcontrol = iot.find("control5678")
    yourcontrol.attach()
    yourcontrol.tell("do it") # auto run_background()


#------------------------------------------------------------------------------
#EXAMPLE 5b: find a point that is already bound, does not re-wrap it
#and bind on a bound point does not rebind

def example5b():
    ##import iot

    feed = iot.find("feed")
    print(feed.__repr__()) #unbound

    feed.follow()
    print(feed.__repr__()) #bound

    ##feed2 = iot.find("feed") # already locally bound
    ##print(feed2.__repr__()) #bound

    ##feed2.follow()
    ##print(feed2.__repr__()) #bound

#END


#------------------------------------------------------------------------------
#EXAMPLE 6: simplest possible wait for 1 feed update then exit

#NOT TESTED - JUST AN IDEA IN DEVELOPMENT

def example6():
    print("TEST DISABLED")
    return

    ##import iot

    ##myfeed = iot.create_feed("feed_1234")

    ##yourfeed = iot.find("feed_1234").follow()

    ##value = yourfeed.wait()
    ##print(value)

    #END # atexit calls iot.stop()


#------------------------------------------------------------------------------
#EXAMPLE 7: simplest possible wait for 1 control actuate then exit

#THIS EXAMPLE DELETED.
#it makes no sense to do this, without some form of threading,
#when using a single process with no real IoticAgent.

def example7():
    print("test deleted")


#------------------------------------------------------------------------------
#EXAMPLE 8: simplest repeating feed share

# auto connects
# shares value 10 every half a second

def example8():
    ##import iot
    iot.start() # creates defaults
    iot.feed.set_mode(iot.TIMED)
    iot.feed.rate = 4
    iot.feed.value = 42
    ##print("CTRL-C to stop")
    iot.run(for_time=5) # only exits on error/CTRL-C, then does stop()
    #END


#------------------------------------------------------------------------------
#EXAMPLE 9: simplest repeating control actuate

def example9():
    #auto connects
    # shares value 10 every half second

    ##import iot
    iot.start() # creates defaults
    iot.control.set_mode(iot.TIMED)
    iot.control.rate = 1
    iot.control.value = 99
    ##print("CTRL-C to stop")
    iot.run(for_time=5) # only exits on error/CTRL-C, then does iot.stop()


#------------------------------------------------------------------------------
#EXAMPLE 10: simplest feed update with user action

# auto connects
# auto follows feeds
# auto routes feed updates to your update
# shows feed data on console with user message

def example10():
    ##import iot
    iot.start() # creates thing
    #TODO: if we refer to thing via a property
    #it could create it on demand? But that would auto-start?
    lhs_thing = iot.create_thing("lhs_thing")
    lhs_feed = lhs_thing.create_feed("lhs_feed")
    rhs_thing = iot.create_thing("rhs_thing")

    rhs_follower = rhs_thing.find("lhs_thing", "lhs_feed").follow()

    @rhs_follower.when_updated
    def update(sender, data):
        print("rhs_follower.when_updated: %s %s" % (sender.__repr__(), str(data)))

    # Now send it some data
    lhs_feed.share("hello")
    iot.run(for_time=2)
    #END


#------------------------------------------------------------------------------
#EXAMPLE 11: simplest control update with user action

# auto connects
# auto attaches
# auto routes control updates to your update
# shows control data on console with user message

def example11():
    ##import iot
    iot.start() # create default thing/control/feed
    lhs_thing = iot.create_thing("lhs_thing")
    rhs_thing = iot.thing

    # Find and bind to the control
    lhs_attacher = lhs_thing.find("thing", "control").attach()

    @iot.control.when_updated
    def update(sender, data):
        print("control.when_updated: %s %s" % (sender.__repr__(), str(data)))
        return True # ACK

    # Send it some data
    lhs_attacher.ask("ask")
    lhs_attacher.tell("tell")
    iot.run(for_time=2)
    #END


#------------------------------------------------------------------------------
#EXAMPLE 12: something a bit like a cloud-var, publish only with a feed share

def example12():
    ##import iot

    iot.start() # starts explicitly so thing is 'online', registers atexit(iot.stop)
    var = iot.feed # feed not available until started

    ##print("CTRL-C to stop")
    ##while True:
    for i in range(5):
        time.sleep(0.5)
        if iot.tester.something_happened():
            var.value = "TICK" # does iot.share() which does iot.thing.feed.share()
            #NOTE: There are no followers, so it loops back to self and initiates default console print

    #END # error/CTRL-C will atexit iot.stop()


#------------------------------------------------------------------------------
#EXAMPLE 13: something a bit like a cloud-var, publish only with a control attachment

def example13():
    ##import iot
    new_control = iot.create_control("new_control")
    i_attach = iot.find("new_control").attach()
    var = i_attach

    @new_control.when_updated
    def update(sender, data):
        print("control update %s %s" % (sender.__repr__(), str(data)))
        return True # ACK

    ##print("CTRL-C to stop")
    ##while True:
    for i in range(5):
        time.sleep(0.5)
        if iot.tester.something_happened():
            var.value = "VALUE" # causes control actuate

    #END # error/CTRL-C will atexit iot.stop()

#------------------------------------------------------------------------------
#EXAMPLE 14: something a bit like a cloud-var, update only with a feed update

def example14():
    ##import iot
    import time

    producer = iot.create_feed("producer")
    @producer.when_updated
    def updated(sender, data):
        print("OOPS, reflected!!")

    yourfeed = iot.find("producer").follow()

    @yourfeed.when_updated
    def updated(sender, data):
        print("UPDATED!!")
    var = yourfeed # just a reference to a remote feed, looks like a cloud-var

    iot.start() # explicity start, installs atexit(iot.stop)
    ##print("CTRL-C to stop")
    ##while True:
    for i in range(4):
        # produce some test data
        producer.share("VALUE")
        time.sleep(1)

        # consume the test data
        if var.is_updated: # poll
            print(var) # default __str__ binds to str(var.value)
        else:
            print("not updated? was_updated=%s" % var.was_updated)

    #END # error/CTRL-C will atexit iot.stop()


#------------------------------------------------------------------------------
#EXAMPLE 15: something a bit like a cloud-var, update only with a control update, and poll

def example15():
    ##import iot
    import time

    realvar = iot.create_control("var")

    @realvar.when_updated
    def update(sender, data):
        print("realvar update:%s %s" % (sender.__repr__(), str(data)))
        return True # ACK

    var = iot.find("var").attach()

    ##print("CTRL-C to stop")
    ##while True:
    for i in range(4):
        # Produce some test data
        var.value = "VALUE" # remote end produces new data
        time.sleep(1)

        # consume the test data
        if realvar.is_updated: #poll local end
            print("polled realvar is:%s" % realvar) # __str__ works in our favour

    #END # error/CTRL-C wil atexit iot.stop()

#------------------------------------------------------------------------------
#EXAMPLE 15b: turning off default handler

def example15b():
    ##import iot
    import time

    realvar = iot.create_control("var")

    realvar.when_updated(iot.IGNORE)
    var = iot.find("var").attach()

    ##print("CTRL-C to stop")
    ##while True:
    for i in range(4):
        # Produce some test data
        var.value = "VALUE" # remote end produces new data
        time.sleep(1)

        # consume the test data
        if realvar.is_updated: #poll local end
            print("polled realvar is:%s" % realvar) # __str__ works in our favour

    #END # error/CTRL-C wil atexit iot.stop()


#------------------------------------------------------------------------------
#EXAMPLE 15c: remapping to default handler

def example15c():
    ##import iot
    import time

    realvar = iot.create_control("var")

    @realvar.when_updated
    def update(sender, data):
        print("realvar from:%s data:%s" % (str(sender), str(data)))
        return True # ACK

    realvar.when_updated(iot.DEFAULT)

    var = iot.find("var").attach()

    ##print("CTRL-C to stop")
    ##while True:
    for i in range(4):
        # Produce some test data
        var.value = "VALUE" # remote end produces new data
        time.sleep(1)

        # consume the test data
        if realvar.is_updated: #poll local end
            print("polled realvar is:%s" % realvar) # __str__ works in our favour

    #END # error/CTRL-C wil atexit iot.stop()

#------------------------------------------------------------------------------
#EXAMPLE 16 - suppressing creation of default things

def example16():
    ##import iot
    mything = iot.create_thing("my thing")
    #mything2 = iot.create_thing("my other thing")

    iot.start() # trigger default creation process

    print(iot.thing.name) # should be "my thing"

    iot.stop()
    #END


#------------------------------------------------------------------------------
#EXAMPLE 17: suppress creation of default feed

def example17():
    ##import iot

    myfeed = iot.create_feed("myfeed")

    iot.start() # will trigger auto-create semantics
    print(iot.feed.name) # should be myfeed if only one
    iot.stop()

    #END


#------------------------------------------------------------------------------
#EXAMPLE 18: suppress creation of default control

def example18():
    ##import iot
    mycontrol = iot.create_control("mycontrol")
    print(iot.control.name)
    iot.start()
    iot.stop()
    #END


#------------------------------------------------------------------------------
#EXAMPLE 19 - user generates data for feed, share it

def example19():
    ##import iot
    import random, time

    iot.feed.set_mode(iot.TIMED)
    iot.feed.rate = 1 # will share once every 1 seconds
    iot.feed.send_on_change = False # production rate does not equal share rate

    ##print("CTRL-C to stop")
    ##while True:
    for i in range(8):
        iot.share(random.choice(["red", "green", "blue"])) #same as: iot.thing.feed.share()
        time.sleep(0.5)
    #END


#------------------------------------------------------------------------------
#EXAMPLE 20 - user generates data for control, actuate it

def example20():
    ##import iot

    other_control = iot.create_control("other_control")

    @other_control.when_updated
    def update(sender, data):
        print("other_control from:%s data:%s" % (str(sender), str(data)))
        return True # ACK

    i_attach = iot.find("other_control").attach()
    #print(i_attach.__repr__())
    i_attach.set_mode(iot.TIMED)
    i_attach.rate = 1 # will share once every 2 seconds

    ##print("CTRL-C to stop")
    ##while True:
    for i in range(4):
        #rate of production does not equal rate of sharing
        i_attach.ask("ASK")
        time.sleep(0.5)

    #END


#------------------------------------------------------------------------------
#EXAMPLE 20b point.attach() morphs point into an attached point

def example20b():
    ##import iot

    other_control = iot.create_control("other_control")

    @other_control.when_updated
    def myupdate(sender, data):
        print("other_control: %s %s" % (sender.__repr__(), str(data)))


    i_attach = iot.find("other_control").attach()

    @i_attach.when_updated
    def update(sender, data):
        #If this is called, it means the attach did not work
        #and therefore it has reflected back to self
        print("ERROR:i_attach receives:%s" % str(data))

    i_attach.ask("ASK")

    #END


#------------------------------------------------------------------------------
#EXAMPLE 21 - clearly separate user code and iotic code

# this is in test_hw.py

#------------------------------------------------------------------------------
#EXAMPLE 22: unspecified value assignment and access

def example22():

    ##import iot

    iot.value = 10 # uses iot.feed.share(10)
    print(iot.value) # uses iot.control.get_last_value()
    iot.run(for_time=2)
    iot.value = 20
    iot.run(for_time=2)

    #END


#------------------------------------------------------------------------------
#example23 moved to ideas/eventing.py - it's a bit like gpiozero
#------------------------------------------------------------------------------
#example24 moved to test_objects.py
#------------------------------------------------------------------------------
#example25 moved to ideas/database.py
#------------------------------------------------------------------------------
#example26 moved ot ideas/test_ioticiser.py
#------------------------------------------------------------------------------
# example27.py - show the __call__ method of Point, Feed and Control
#
# The most common thing you want to do with a Feed or Control is share data,
# so the __call__ meta-method is the same as send() for that type of Point,
# simplifying the syntax in the common case.

def example27():
    import iot
    import time

    my_feed    = iot.create_feed("stuff")
    my_control = iot.create_control("tellme")

    your_feed    = iot.find("stuff").follow()
    your_control = iot.find("tellme").attach()

    ##print("CTRL-C to stop")
    ##while True:
    for i in range(4):
        time.sleep(0.5)
        my_feed(42)
        ##my_feed.share(42)
        your_control(99)
        ##your_control.ask(99)
    # END

#------------------------------------------------------------------------------

def test1():
    # data flow from left to right
    #CREATE
    left_thing    = iot.create_thing("left_thing")
    right_thing   = iot.create_thing("right_thing")
    right_control = right_thing.create_control("right_control")

    #HANDLER FOR BIND
    @right_control.when_new_attacher
    def attachment_request(point):
        print("app: new bind attachment request from:%s" % point.__repr__())
        # no return result means to accept it
        #return False # means reject it

    #FIND AND BIND
    #at the moment control naming seems to be global, this is WRONG
    #this find should fail, because if no thing is provided, it should
    #assume our thing.

    left_attacher = left_thing.find("right_thing", "right_control")
    left_attacher.attach()

    #ROUTE
    @right_control.when_updated
    def update(sender, data):
        print("app: right control update:%s" % str(data))

    #RUN
    for i in range(3):
        left_attacher.ask("ASK")
        time.sleep(1)

    left_attacher.detach()

    for i in range(3):
        left_attacher.ask("ASK") # should loop back, as we are now detached
        time.sleep(1)

#------------------------------------------------------------------------------

def test2():
    # data flow from left to right
    #CREATE
    left_thing    = iot.create_thing("left_thing")
    right_thing   = iot.create_thing("right_thing")
    left_feed     = left_thing.create_feed("left_feed")

    #HANDLER FOR BIND/UNBIND
    @left_feed.when_new_follower
    def new_follower(follower):
        print("app: new follower:%s" % str(follower))

    ##@left_feed.when_unfollowed
    ##def unfollowed(follower):
    ##    print("app: unfollowed:%s" % str(follwer))

    #FIND AND BIND
    right_follower = right_thing.find("left_thing", "left_feed")
    right_follower.follow()

    #ROUTE
    @right_follower.when_updated
    def update(sender, data):
        print("app: right follower update:%s" % str(data))

    #RUN

    for i in range(3):
        left_feed.share("SHARE_A")
        time.sleep(1)

    right_follower.unfollow()

    for i in range(3):
        left_feed.share("SHARE_B")
        time.sleep(1)

#------------------------------------------------------------------------------

def test3():
    # data flow from left to right
    #CREATE
    left_thing    = iot.create_thing("left_thing")
    right_thing   = iot.create_thing("right_thing")
    right_thing2  = iot.create_thing("right_thing2")
    left_feed     = left_thing.create_feed("left_feed")

    #HANDLER FOR BIND/UNBIND
    @left_feed.when_new_follower
    def new_follower(follower):
        print("app: new follower:%s" % str(follower))

    ##@left_feed.when_unfollowed
    ##def unfollowed(follower):
    ##    print("app: unfollowed:%s" % str(follwer))

    #FIND AND BIND
    right_follower = right_thing.find("left_thing", "left_feed")
    right_follower.follow()

    right_follower2 = right_thing2.find("left_thing", "left_feed")
    right_follower2.follow()

    # Note, a right thing follows twice - quite challenging
    #right_follower2 = right_thing.find("left_thing", "left_feed")
    #right_follower2.follow()

    #ROUTE
    @right_follower.when_updated
    def update(sender, data):
        print("app: right follower update:%s" % str(data))

    @right_follower2.when_updated
    def update(sender, data):
        print("app: right follower2 update:%s" % str(data))

    #RUN

    for i in range(3):
        left_feed.share("SHARE_A")
        time.sleep(1)

    right_follower.unfollow()

    for i in range(3):
        left_feed.share("SHARE_B")
        time.sleep(1)


#------------------------------------------------------------------------------
# Test Point.set_mode(iot.TRIGGERED) with iot.feed

def test4():
    iot.feed.set_mode(iot.TRIGGERED)
    iot.feed.value = 42
    for i in range(4):
        time.sleep(1)
        print("app:trigger")
        iot.feed.trigger()


#------------------------------------------------------------------------------
# Test Point.set_mode(iot.TRIGGERED) with iot.unassigned_attacher

##TODO NOT YET WORKING, UNDERLYING WORK TO BE DONE
#trigger only works with a feed at moment

def test4b():
    print("test DISABLED temporarily")
    #iot.start()
    #iot.unassigned_attacher.set_mode(iot.TRIGGERED)
    #iot.unassigned_attacher.value = 42
    #for i in range(4):
    #    time.sleep(1)
    #    print("app:trigger")
    #    iot.unassigned_attacher.trigger()


#------------------------------------------------------------------------------
# Test Point.set_mode(iot.TRIGGERED) with iot.
# Should send to both iot.feed and iot.unassigned_attacher

def test4c():
    iot.set_mode(iot.TRIGGERED)
    iot.value = 42
    for i in range(4):
        time.sleep(1)
        print("app:trigger")
        iot.trigger()

#------------------------------------------------------------------------------
# Test that Point() can get data on demand

last_data = 1
def test5():
    def get_data():
        global last_data
        v = last_data
        last_data += 1
        return v

    #@iot.when_control_updated
    #def update(sender, data):
    #    print("iot.when_control_updated: %s %s" % (sender.__repr__(), str(data)))

    #NOTE: If no followers, data will loopback to here
    @iot.when_feed_updated
    def update(sender, data):
        print("iot.when_feed_updated: %s %s" % (sender.__repr__(), str(data)))

    #TODO: This uses iot.receiver.when_updated
    #The iot.receiver architecture is still WIP
    #it might not be completed by V3 anyway as it is still to be defined
    ##@iot.when_updated
    ##def update(sender, data):
    ##    print("iot.when_updated: %s %s" % (sender.__repr__(), str(data)))


    print("app: share with return value")
    iot.share(get_data()) # 1
    print("app: share with ref")
    iot.share(get_data) # 2

    #IMMEDIATE

    print("app: share with ref")
    iot.share(get_data) # 3

    #TRIGGERED
    iot.set_mode(iot.TRIGGERED)
    print("app: ref trigger")
    iot.trigger() # 4
    print("app: ref trigger")
    iot.trigger() # 5

    #TIMED
    iot.set_mode(iot.TIMED)
    iot.rate = 1
    print("app: ref timed for 5")
    iot.run(for_time=5) # 6,7,8,9


#------------------------------------------------------------------------------
# test6 - test that double bind and double unbind work as expected

def test6():
    iot.create_feed("feed")
    iot.create_control("control")

    print("app: first follow")
    f = iot.find("feed").follow()
    print("app: second follow")
    f.follow() # should get warning
    print("app: first unfollow")
    f.unfollow() # should work
    print("app: second unfollow")
    f.unfollow() # should get warning

    print("app: first attach")
    c = iot.find("control").attach()
    print("app: second attach")
    c.attach() # should get warning
    print("app: first detach")
    c.detach() # should work
    print("app: second detach")
    c.detach() # should get warning


#------------------------------------------------------------------------------
# test7 - test we can find a Thing address

def test7():
    iot.start()
    t = iot.find_thing("thing")
    print(t.__repr__())


#------------------------------------------------------------------------------
# test8 - a double sided attach
# i.e. handlers at both ends, with confirmations

def test8():
    lhs = iot.create_thing("lhs")
    rhs = iot.create_thing("rhs")
    mcr = rhs.create_control("rhs_control")

    @mcr.when_new_attacher
    def attached(attacher):
        print("mcr: new attacher:%s" % str(attacher))

    ycr = lhs.find("rhs", "rhs_control")

    @ycr.when_have_attached
    def attached(control):
        print("ycr: have attached to:%s" % control.__repr__())

    # now actually attach and see which handlers fire
    ycr.attach()

#------------------------------------------------------------------------------
# test9 - create_thing twice uses existing thing

def test9():
    # duplicate thing
    lhs_thing = iot.create_thing("lhs_thing")
    lhs_thing2 = iot.create_thing("lhs_thing") # should get same as before

    print(lhs_thing)
    print(lhs_thing2)

    # duplicate feed
    lhs_feed = lhs_thing.create_feed("lhs_feed")
    lhs_feed2 = lhs_thing.create_feed("lhs_feed")

    print(lhs_feed.__repr__())
    print(lhs_feed2.__repr__())

    # duplicate control

    lhs_control = lhs_thing.create_control("lhs_control")
    lhs_control2 = lhs_thing.create_control("lhs_control")

    print(lhs_control.__repr__())
    print(lhs_control2.__repr__())


#------------------------------------------------------------------------------
# test10 third party attachment initiation

def test10():
    lhs_thing    = iot.create_thing("lhs_thing")
    rhs1_thing   = iot.create_thing("rhs1_thing")
    rhs2_thing   = iot.create_thing("rhs2_thing")
    third_party  = iot.create_thing("third_party")
    rhs1_control = rhs1_thing.create_control("rhs1_control")
    rhs2_control = rhs2_thing.create_control("rhs2_control")

    @rhs1_control.when_new_attacher
    def attached(attacher):
        print("rhs1_control.when_new_attacher %s" % attacher.__repr__())

    @rhs1_control.when_detached
    def detached(control):
        print("rhs1_control.when_detached %s" % control.__repr__())

    @rhs1_control.when_updated
    def updated(sender, data):
        print("rhs1_control.when_updated %s %s" % (sender.__repr__(), str(data)))

    @rhs2_control.when_new_attacher
    def attached(attacher):
        print("rhs2_control.when_new_attacher %s" % attacher.__repr__())

    @rhs2_control.when_detached
    def detached(control):
        print("rhs2_control.when_detached %s" % control.__repr__())

    @rhs2_control.when_updated
    def updated(sender, data):
        print("rhs2_control.when_updated %s %s" % (sender.__repr__(), str(data)))

    # initiate a third party binding from lhs to rhs/control
    t = third_party.find_thing("lhs_thing")
    c = third_party.find("rhs1_thing", "rhs1_control")

    #iot.attach(iot.find_thing("lhs_thing"), iot.find("rhs_thing", "rhs_control"))
    #iot.attach(t, c)
    t.attach(c)
    iot.run(for_time=1) #TODO WIP, the above is non-blocking at moment

    # The only way this will 'fanout'
    # initiate a second third party binding from lhs to rhs/control
    #t = third_party.find_thing("lhs_thing")
    #c = third_party.find("rhs2_thing", "rhs2_control")
    #iot.attach(iot.find_thing("lhs_thing"), iot.find("rhs2_thing", "rhs2_control"))
    #iot.attach(t, c)
    #t.attach(c)
    #iot.run(for_time=1) #TODO WIP, the above is non-blocking at moment

    ## If using iot.ask here, it uses unassigned_attacher, we hope.
    print(lhs_thing.unassigned_attacher)
    print(lhs_thing.unassigned_attacher.instances)

    #print("app: should send data")

    #c.ask(20) # must ask the correct control to send?
    #iot.run(for_time=2)

    # check the state of the thing that owns the unassigned_attacher
    #lhs_thing.dump()

    # third party detach of one of the attachers, the last one
    #t.detach(c)
    #iot.run(for_time=1) #TODO WIP, the above is non-blocking at the moment

    #print("app: should send data")
    #c.ask(30)
    #iot.run(for_time=2)


#------------------------------------------------------------------------------
# TEST11 - test that the first thing created is the default thing

def test11():
    thing1 = iot.create_thing("thing1")
    thing2 = iot.create_thing("thing2")
    print(iot.thing) # should be thing1


#------------------------------------------------------------------------------
# TEST12 - our standard test case at the shell
def test12():
    lt = iot.create_thing("lt")
    lf = lt.create_feed("lf")
    rt = iot.create_thing("rt")
    rc = rt.create_control("rc")
    ff = rt.find("lt", "lf").follow()
    ca = lt.find("rt", "rc").attach()

#------------------------------------------------------------------------------
# TEST unsolicited control attach
# This is where a third script or webui does the binding on your behalf
# there is a LHS a RHS and an initiator.
# Run each of these in a separate script to do the testing.

# not part of standard test suite yet
def uca_lhs():
    #do a timed iot.ask with a counter
    lhs = iot.create_thing("lhs_thing")

    @lhs.unassigned_attacher.when_have_attached
    def attached(control):
        print("lhs: just attached to:%s" % str(control))

    for i in range(5):
        iot.ask(i) # should use the only 'thing'
        time.sleep(1)

# not part of standard test suite yet
def uca_rhs_1():
    # setup one control that prints name and data
    rhs = iot.create_thing("rhs_thing")
    c1  = rhs.create_control("control1")

    @c1.when_new_attacher
    def attached(attacher):
        print("c1: new attacher:%s" % str(attacher))

    @c1.when_updated
    def updated(sender, data):
        print("c1 updated from:%s data:%s" % (str(sender), str(data)))

    iot.run(for_time=10)

# not part of standard test suite yet
def uca_rhs_2():
    # setup two controls that print their name and data
    rhs = iot.create_thing("rhs_thing")
    c1  = rhs.create_control("control1")
    c2  = rhs.create_control("control2")

    @c1.when_new_attacher
    def attached(attacher):
        print("c1: new attacher:%s" % str(attacher))

    @c1.when_updated
    def updated(sender, data):
        print("c1: updated from:%s data:%s" % (str(sender), str(data)))

    @c2.when_new_attacher
    def attached(attacher):
        print("c2: new attacher:%s" % str(attacher))

    @c2.when_updated
    def updated(sender, data):
        print("c2: updated from:%s data:%s" % (str(sender), str(data)))

    iot.run(for_time=10)

# not part of standard test suite yet
def uca_initiator_1():
    # initiate a binding from lhs to rhs/control1
    iot.attach(iot.find(thing_name="lhs_thing"), iot.find("rhs_thing", "control1"))

# not part of standard test suite yet
def uca_initiator_2():
    # initiate two bindings, from lhs to rhs/control1 and rhs/control2
    iot.attach(iot.find(thing_name="lhs_thing"), iot.find("rhs_thing", "control1"))
    iot.attach(iot.find(thing_name="lhs_thing"), iot.find("rhs_thing", "control2"))


#----- MAIN -------------------------------------------------------------------
#
# If you run more than one test in the same run, beware that it might not
# be completely sandboxed from the previous test, and might behave differently.
# This might or might not be what you want.
# you are best to run tests singly using the outer test_all.sh as that will
# ensure everything is sandboxed.
# Also, if database state is important to a test passing, you might have
# to clear the database first. Use test 'rmdby' as an iot.py parameter to do that.
# e.g. python test_iot.py test1 run rmdby

if __name__ == "__main__":
    import sys
    TESTS = sys.argv[1:]
    if len(TESTS) == 0:
        print("no tests run")

    for t in TESTS:
        if t == 'end': # marks end of tests
            break
        print("\n" + ('*' * 80))
        print("TEST: %s" % t)
        eval("%s()" % t) # call the test function
        print("\n")

    iot.stop()


#END

