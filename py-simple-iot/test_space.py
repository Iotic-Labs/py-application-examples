# test_space.py  10/12/2016  D.J.Whale
#
# A tester to test any arbitrary 'space' implementation

#----- TEST HARNESS -----------------------------------------------------------

##import iot
##Space = iot.MemorySpace

#import iot
#space = iot.real_module.default_space

#import os
#if os.path.exists("iotic.db"):
#    os.unlink("iotic.db")

##import iotic
##Space = iotic.IoticSpace

# Not much use now, have to import iot to get the Space() class,
# but importing iot auto starts loads of stuff. Grr.

import iotic
#create_IoticSpace(Space, agent_id="testing.ini")
space = iotic.IoticSpace('testing.ini')



#----- GET IN
#space = Space()
##space.identify("me")
##space.authenticate("secret")
space.connect()

#----- get agent_id
print("agent_id=%s" % str(space.agent_id))


#---- CREATE
# CREATE THING
thing_id = space.create_thing("utilitypole")
print("thing_id:%s" % str(thing_id))

#CREATE CONTROL
# TODO: IoticAgent.IOT requires callback for controls
# control_id = space.create_control(thing_id, "control")
# print(control_id)

# CREATE FEED
feed_id = space.create_feed(thing_id, "tc_feed")
print("feed_id:%s" % str(feed_id))


space.disconnect()

#STOP
import sys
sys.exit(0)


#----- RAW DATA TRANSFER
# put data in the data table


class Receiver():
    def __init__(self, id):
        self.id = id

    def receive_data(self, from_addr, to_addr, data):
        print("%s received from:%s to:%s data:%s" % (str(self.id), str(from_addr), str(to_addr), str(data)))

ff = Receiver("feed_follower")
c  = Receiver("control")

# Currently feed followers must have a real binding for the DBSpace fanout to work
# print("feed binding in place")
# space._remote_bind(thing_id, feed_id[1], thing_id)


# data sent from a feed to a feed follower
#TODO: Note, could use the broadcast pattern here later.
#This is the point to point pattern, as currently DBSpace
#has a fanout for feed send that makes it point to point
#so there will be one record in the table for each consumer.
#The new agent_id scheme means we don't have to work that way any more

#DEPRECATED space.register_for(ff, space.DATA, from_addr=feed_id, to_addr=(thing_id, None))
# New, simpler, broadcast method
space.register_for(ff, space.DATA, from_addr=feed_id)

# data sent from a control attacher to a control
#Note this ignores any binding record, but that's fine.
space.register_for(c, space.DATA, from_addr=(thing_id, None), to_addr=control_id)

# send data from a feed
# Note, fanout is done inside DBSpace.send_from at the moment
# But eventually we can try the broadcast pattern

for i in range(4):
    data = "F" + str(i)
    print("feed send:%s" % data)
    space.send_from(point_addr=feed_id, data=data)

# send data to a control
for i in range(4):
    data = "C" + str(i)
    print("send to control:%s" % data)
    space.send_to(from_thing_id=thing_id, to_point_addr=control_id, data=data)

# Make it all happen, until there are no records left to process
space.tick()
##print("STOPPED")



# get data out from the data table using the current horizon
# and leaving existing records intact

#while True:
#    res = space._receive_next(space.DATA)
#    if res is None: break
#    rowid, from_thing_id, from_point_id, to_thing_id, to_point_id, data = res
#    from_addr = (from_thing_id, from_point_id)
#    to_addr = (to_thing_id, to_point_id)
#
#    print("%s receive from:%s to:%s %s" % (str(rowid), str(from_addr), str(to_addr), str(data)))
#
#    ##break # crash before ack
#
#    # Finally, mark the rowid as used
#    space._used_rowid(space.DATA, rowid)






#----- RAW META TRANSFER



# HIDE/SHOW THING
##space.hide_thing(thing_id)
##space.show_thing(thing_id)

#HIDE/SHOW FEED
##space.unadvertise_feed(feed_id)
##space.advertise_feed(feed_id)

#CREATE CONTROL
##control_id = space.create_control(thing_id, "control")
##print(control_id)

#HIDE/SHOW CONTROL
##space.unoffer_control(control_id)
##space.offer_control(control_id)

# FIND point by thing_name, point_name
##a = space.find("thing", "feed")
##print("found:%s" % str(a))

# FIND point by thing_id, point_name
##a = space.find(thing_id, "feed")
##print("found:%s" % str(a))

#----- DATA TEST
##print("---- DATA TEST")
##thing1   = space.create_thing("thing1")
##thing2   = space.create_thing("thing2")
##thing3   = space.create_thing("thing3")

##feed1    = space.create_feed(thing1, "feed1")
##space.advertise_feed(feed1)

##control1 = space.create_control(thing1, "control1")
##space.offer_control(control1)

#For DBSpace
##print("# things")
##rows, headings = space._sql("SELECT * FROM thing")
##for r in rows:
##    print(r)
##print("# points")
##rows, headings = space._sql("SELECT * FROM point")
##for r in rows:
##    print(r)


#----- CONTROL
##print("---- CONTROL")
# CONTROL BINDING thing2 attaches to (thing1, control1)
##bound = space.bind_point(thing2, control1)
##print("bound control:%s" % str(bound))

#for DBSpace only
##rows, headings = space._sql("SELECT * FROM notification LIMIT 1")
##print(rows[0])
#for MemorySpace only
##print(space.things.keys())

# SEND CONTROL DATA
#NOTE: send_to: This is used when sending to a control consumer (1:1 or many:1)
##data = "CONTROL DATA"
#space.send_to(from_thing, other_thing, other_point, data)
##print("sending from thing %s to thing/point %s/%s" % (str(thing2), str(thing1), str(control1[1])))
##space.send_to(thing2, control1, data)

# Check it is on the correct receive queue
#for DBSpace only
##rows, headings = space._sql("SELECT * FROM data LIMIT 1")
##print(rows[0])
#for MemorySpace only
##print(space.things[thing1].points["control1"].rxqueue)

# RECEIVE CONTROL DATA (properly)

##print("receiving for thing/point %s/%s" % (str(thing1), str(control1[1])))
##data = space.receive_for(control1)
##if data is None:
##    print("nothing received")
##else:
##    print("data:%s" % str(data))


#----- FEED
##print("----FEED")
# FEED BINDING thing2 attaches to thing1/feed1
#bind_point(from_thing_id, from_point_id, to_thing_id)
##space.bind_point(thing2, feed1)
##msg = space.get_notification(feed1) # pump meta queue manually
##space.bind_point(thing3, feed1)
##msg = space.get_notification(feed1) # pump meta queue manually

# check binding is correct
#for MemorySpace only
##print(space.things[thing1].points)

#for DBSpace only
##rows, headings = space._sql("SELECT * FROM binding")
##print("BINDINGS:")
##for r in rows:
##    print(r)

#----- SEND FEED DATA
#NOTE: send_from This is used when sending from a feed to any followers (1:many)
# will have to fanout at the sending end. Just does one for now
##data = "FEED DATA"
##space.send_from(feed1, data)

# is it on the right rxqueue? For MemorySpace only
##print(space.things[thing2].rxqueues[feed1])

#for DBSpace only
##rows, headings = space._sql("SELECT * FROM data")
##print("DATA TABLE:")
##for r in rows:
##    print(r)

#----- RECEIVE FEED DATA

### From a specific sender
####while True: #thing2 from (thing1 feed1)
####    data = space.receive_for(thing2, feed1)
####    if data is None: break
####    print(data)

##while True: # thing2
##    print("receiving for thing %s" % str(thing2))
##    data = space.receive_for(thing2)
##    if data == None: break
##    print("data %s" % str(data))

##while True: # thing3
##    print("receiving for thing %s" % str(thing3))
##    data = space.receive_for(thing3)
##    if data == None: break
##    print("data %s" % str(data))


#----- UNBIND

#----- FINISHED
space.disconnect()

# END

