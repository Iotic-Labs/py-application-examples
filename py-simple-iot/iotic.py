# iotic.py  10/01/2017 D.J.Whale and T.Churchard

from __future__ import unicode_literals, print_function

import sys
if sys.version_info[0] < 3:
    print("error:iotic.py not yet working in V2, use python3 to run it")
    sys.exit()

import logging
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
level=logging.CRITICAL)

from functools import partial

from ubjson import dumpb as ubjdumpb, loadb as ubjloadb

from IoticAgent import IOT
from IoticAgent.IOT import Thing, Point
from IoticAgent.Core import Validation
from IoticAgent.Core.compat import string_types
from IoticAgent.Core.Const import R_FEED, R_CONTROL, R_SUB, P_RESOURCE, R_ENTITY

# The docs for IoticAgent are here:
#   https://pythonhosted.org/py-IoticAgent

def info(msg):
    print(str(msg))

def trace(msg):
    print(str(msg))

def warning(msg):
    print("warning:%s" % str(msg))

def assert_is_str(o, location=None):
    if not isinstance(o, str):
        print('*' * 80)
        print("at location:%s" % str(location))
        print("not a string:%s got %s" % (str(o), str(type(o))))
        print('*' * 80)
        raise ValueError("Expected a string address")

# This is a class factory.
# It is here so that we don't have to 'import iot' as that is bad,
# because it creates a circular module dependency.
# This class factory means the necessary parts of 'upstairs' are passed
# in at runtime rather than resolved at import time.

def create_IoticSpace(Space, *args, **kwargs):
    ##trace("called create_IoticSpace with:%s %s" % (str(args), str(kwargs)))

    class IoticSpace(Space):

        #----- INITIALISATION, CONFIGURATON, CONNECTION ---------------------------

        def __init__(self, agent_id=None): #IoticSpace.__init__
            Space.__init__(self)
            agent_ini = agent_id

            ##trace("Initialising IoticSpace from:%s" % str(agent_ini))

            ##HERE## refactor all these data structures into an IoticAgentFixer class
            # Create cache of Thing & Point instances (restore)
            self.__cache = None  # dict of {'lid': {'thing': inst,
                                 #                  'points': {'pid': inst }}}

            #DEPRECATED  self.__attachments = {} # dict of {pid: RemoteControl}
            #DEPRECATED  self.__pid_to_point = {} # dict of {pid: IOT.Point}

            # There has to be two tables, because if you follow your own feed
            # there will be both ends in the same table and you'll get the wrong
            # object end back sometimes
            self.__id_to_real_object    = {} # real things, feeds, controls
            self.__id_to_virtual_object = {} # remote things, feeds, controls

            # IoticAgent.IOT.Client instance
            self.__agent = IOT.Client(config=agent_ini)
            warning("created/duplicate/deleted require an updated IOT.Client")
            #TODO: note, we are testing with a Tim-hacked version of the IoticAgent at the moment,
            #not the one taken from pipy
            self.__agent.register_callback_created(self.__cb_created)
            self.__agent.register_callback_duplicate(self.__cb_duplicated)
            self.__agent.register_callback_deleted(self.__cb_deleted)

        @property # readonly
        def agent_id(self):
            return self.__agent.agent_id

        def is_thing_addr(self, addr): #IoticSpace.is_thing_addr
            """Is this a Thing address??"""
            if addr is None:
                return False # not a thing_addr if None - valid use case!

            assert_is_str(addr, "is_thing_addr")

            if addr in self.__cache:
                # it's a thing_name of one of our local things, so it is a thing_addr
                ##trace("local thing address is a thing")
                return True

            try:
                addr_object = self.__id_to_real_object[addr]
                # it's one of our local objects, so is that object a Thing?
                ##trace("local thing address is one of our real things")
                return isinstance(addr_object, IOT.Thing.Thing)
            except:
                addr_object = self.__id_to_virtual_object[addr]
                # will throw KeyError if not found
                # it's one of our remote objects, so is that remote object a Thing?
                #TODO: Should this be RemoteThing??
                ##trace("thing address is one of our remote things")
                return isinstance(addr_object, IOT.Thing.Thing)

        def connect(self): #IoticSpace.connect
            info("connecting to IoticSpace...")
            self.__agent.start()
            info("restoring your Things and Points...")
            self.restore()

        def disconnect(self): #IoticSpace.disconnect
            info("disconnecting from IoticSpace...")
            self.__agent.stop()
            info("disconnected from IoticSpace. Bye for now!")

        def get_thing_addr(self, thing_name): # IoticSpace.get_thing_addr
            """Turn a thing_name into a thing_addr"""
            # Returns IOT.Thing instance.  https://pythonhosted.org/py-IoticAgent/IOT/Thing.m.html
            assert_is_str(thing_name, "get_thing_addr")
            if thing_name in self.__cache:
                t = self.__cache[thing_name]['thing']
            else:
                raise ValueError("thing %s not found" % str(thing_name))
            ta = t.guid
            assert_is_str(ta, "get_thing_addr2")
            return ta
            # could be like a create_thing that doesn't actually create,
            # i.e. it returns same opaque object, or exception if does not exist?
            # returns: some opaque object that can be used as a thing_id to future calls
            # exception: if not found
            # exception: connection error etc etc

        # ---- IOTIC HOUSE KEEPING ------------------------------------------------

        def __cb_created(self, data):
            """Called when any resource is created"""
            ##trace("CREATED: %s" % str(data))
            r_type = data[P_RESOURCE]

            if r_type == R_ENTITY:
                ##trace("  THING CREATED")
                #thing created - send upstairs to Thing.when_new_thing??
                #this was not part of the spec'd delivery, defer until next phase
                pass

            elif r_type in [R_FEED, R_CONTROL]:
                ##trace("  POINT CREATED")
                #control created - send upstairs to Thing.when_new_control??
                # feed created - send upstairs to Thing.when_new_feed??
                #this was not part of the spec'd delivery, defer until next phase
                pass

            elif r_type == R_SUB:
                ##trace("##  BOUND - new follower/new attacher")
                ##trace(str(data))
                from_addr = data['entityLid'] #TODO: should really be the guid of that lid

                # use case is: something follows me/attaches to me,
                # so ask it what feeds and controls it has
                # so I could bind back to those if I want to.
                pid = data['pointId'] # pid of receiver
                to_addr = pid

                ##trace("Trying process_meta with a BOUND")
                assert_is_str(from_addr, "cb_created")
                assert_is_str(to_addr, "cb_created2")

                c = self.process_meta(Space.NOTIFY_BOUND, from_addr, to_addr) # virtual end
                ##c = self.process_meta(Space.NOTIFY_BOUND, to_addr, from_addr) # real end
                ##if c == 0:
                ##    trace("Nothing handleld BOUND message")
                ##else:
                ##    trace("There were %d handles of BOUND message" % str(c))

        def __cb_duplicated(self, data):
            """Called when any resource is created but already exists"""
            # duplicated is called when this Resource already exists in Iotic Space
            # We'll treat it as Created for simplicity
            self.__cb_created(data)

        def __cb_deleted(self, data):
            """Called when any resource is deleted"""
            ##trace("DELETED: %s" % str(data))
            r_type = data[P_RESOURCE]

            if r_type == R_ENTITY:
                ##trace("  THING DELETED")
                # thing created - send upstairs to thing.when_deleted?? point.when_lost??
                #this was not part of the spec'd delivery, defer until next phase
                pass

            elif r_type in [R_FEED, R_CONTROL]:
                ##trace("  POINT DELETED")
                # control created - send upstairs to point.when_deleted?? point.when_lost??
                #this was not part of the spec'd delivery, defer until next phase
                pass

            elif r_type == R_SUB:
                ##trace("##  UNBOUND - lost_follower/lost_attacher")
                ##trace(str(data))
                from_addr = data['entityLid'] #TODO: should really be the guid of that lid?
                # use case is: something follows me/attaches to me,
                # so ask it what feeds and controls it has
                # so I could bind back to those if I want to.
                pid = data['pointId'] # pid of receiver
                ##DEPRECATED to_addr = self.__pid_to_point[pid]
                to_addr = pid
                ##trace("Trying process_meta with a UNBOUND")
                assert_is_str(from_addr, "cb_deleted")
                assert_is_str(to_addr, "cb_deleted2")
                c = self.process_meta(Space.NOTIFY_UNBOUND, from_addr, to_addr)
                ##if c == 0:
                ##    warning("Nothing handled UNBOUND message")
                ##else:
                ##    trace("There wre %d handles of UNBOUND" % str(c))

        def __data_encode(self, data):
            """Wrap primitives into dict for IoticAgent"""
            mime = None
            if not isinstance(data, dict) and not isinstance(data, bytes):
                data = ubjdumpb({'v': data})
                mime = "simple-iot/primitive"
            return data, mime

        def __data_decode(self, data, mime=None):
            """Unwrap primitives from a dict from IoticAgent"""
            if mime is None:
                return data
            if mime == "simple-iot/primitive":
                return ubjloadb(data)['v']
            raise ValueError("Unable to decode data with mime %s", mime)

        def __unbind_by_remote_point_guid(self, lid, guid):
            """unbind_by_remote_point_guid: Unsubscribe local thing "lid" from remote point "guid"
            """
            assert_is_str(lid, "unbind_by_remote_point_guid")
            assert_is_str(guid, "unbind_by_remote_point_guid2")

            # List subscriptions for local Thing by lid
            sub_list_evt = self.__agent._request_sub_list(lid, limit=500, offset=0)
            sub_list_evt.wait(self.__agent.sync_timeout)
            self.__agent._except_if_failed(sub_list_evt)
            sub_list = sub_list_evt.payload['subs']

            # For each sub compare guid
            guid = Validation.guid_check_convert(guid)
            for subid, sub in sub_list.items():
                if sub['id'] == guid:
                    sub_delete_evt = self.__agent._request_sub_delete(subid)
                    sub_delete_evt.wait()
                    self.__agent._except_if_failed(sub_delete_evt)
                    return
            raise ValueError("guid %s not found in thing %s connections", guid, lid)


        # ---- CREATION -----------------------------------------------------------

        def create_thing(self, thing_name): #IoticSpace.create_thing
            """Create or reuse an existing thing from a friendly thing_name"""
            assert_is_str(thing_name, "create_thing")
            thing_name = Validation.lid_check_convert(thing_name)
            if thing_name in self.__cache:
                t = self.__cache[thing_name]['thing']
            else:
                t = self.__agent.create_thing(thing_name)
                self.__cache[thing_name] = {'thing': t, 'points': {}}

            thing_addr = t.guid
            assert_is_str(thing_addr, "create_thing2")
            self.__id_to_real_object[thing_addr] = t
            return thing_addr

        def create_feed(self, thing_id, feed_name): #IoticSpace.create_feed
            """Create or reuse an existing feed on this thing_id object"""
            assert_is_str(thing_id, "create_feed")
            assert_is_str(feed_name, "create_feed2")
            # return https://pythonhosted.org/py-IoticAgent/IOT/Point.m.html#IoticAgent.IOT.Point.Feed
            # returns: an opaque object that can be used to pass in as a point_id later
            # exception if cannot be created
            # exception: connection error etc etc

            thing_object = self.__id_to_real_object[thing_id]
            if not isinstance(thing_object, IOT.Thing.Thing):
                raise ValueError("thing_object must be IoticAgent.IOT.Thing instance, got:%s" % str(type(thing_object)))
            feed_name = Validation.pid_check_convert(feed_name)
            point = thing_object.create_feed(feed_name)
            self.__cache[thing_object.lid]['points'][feed_name] = point
            ##DEPRECATEDself.__pid_to_point[point.guid] = point
            self.__id_to_real_object[point.guid] = point
            addr = point.guid
            assert_is_str(addr, "create_feed3")
            return addr

        def create_control(self, thing_id, control_name): #IoticSpace.create_control
            """Create or reuse an existing control on this thing_id object"""
            assert_is_str(thing_id, "create_control")
            assert_is_str(control_name, "create_control2")

            thing_object = self.__id_to_real_object[thing_id]
            if not isinstance(thing_object, IOT.Thing.Thing):
                raise ValueError("thing_object must be IoticAgent.IOT.Thing instance, got:%s" % str(type(thing_object)))

            control_name = Validation.pid_check_convert(control_name)

            def control_data_cb(payload):
                ##trace("control data received:%s" % str(payload))
                # thing_id and control_name are closure variables
                data = payload['data']
                mime = payload['mime']
                entityLid = payload['entityLid']
                lid       = payload['lid']

                # The callback receives a single dict argument, with keys of:
                #   'data' # (decoded or raw bytes)
                #   'mime' # (None, unless payload was not decoded and has a mime type)
                #   'subId'
                #   'lid'
                #   'entityLid'
                #   'confirm'
                #   'time' # (datetime representing UTC timestamp of share)
                #   'requestId'##
                data = self.__data_decode(data, mime)

                ##trace("entityLid:%s lid:%s" % (str(entityLid), str(lid)))
                ##if not entityLid in self.__cache:
                ##    warning("entityLid not in cache:%s" % str(entityLid))
                ##points = self.__cache[entityLid]['points']
                ##if not lid in points:
                ##    warning("lid not in cache for entity, lid:%s" % str(lid))

                ##to_addr = point.guid ##HERE: is this correct for the upstairs routing tables?
                point = self.__cache[entityLid]['points'][lid]
                point_guid = point.guid
                ##trace("point guid is:%s" % str(point_guid))

                assert_is_str(point_guid, "create_control3")
                self.process(Space.DATA, data, to_addr=point_guid)

            point = thing_object.create_control(control_name, control_data_cb)
            self.__cache[thing_object.lid]['points'][control_name] = point
            ##DEPRECATED self.__pid_to_point[point.pid] = point
            self.__id_to_real_object[point.pid] = point
            addr = point.guid
            assert_is_str(addr, "create_control4")
            return addr


        #----- VISIBILITY ---------------------------------------------------------

        def show_thing(self, thing_id): #IoticSpace.show_thing
            """Make this thing visible"""
            assert_is_str(thing_id, "show_thing")
            thing_object = self.__id_to_real_object[thing_id]
            if not isinstance(thing_object, IOT.Thing.Thing):
                raise ValueError("thing_object must be IoticAgent.IOT.Thing instance, got:%s" % str(type(thing_object)))
            thing_object.set_public(True)
            # returns: nothing
            # exception: any

        def hide_thing(self, thing_id): #IoticSpace.hide_thing
            """Make this thing invisible"""
            assert_is_str(thing_id, "hide_thing")
            thing_object = self.__id_to_real_object[thing_id]
            if not isinstance(thing_object, IOT.Thing.Thing):
                raise ValueError("thing_object must be IoticAgent.IOT.Thing instance, got:%s" % str(type(thing_object)))
            thing_object.set_public(False)
            # returns: nothing
            # exception: any

        #----- FIND REFERENCES ----------------------------------------------------

        def find(self, thing_id, point_id=None): #IoticSpace.find
            """Find a thing_id or a point_id and return it's validated GUID"""
            assert_is_str(thing_id, "find")
            if point_id is not None:
                assert_is_str(point_id, "find2")
            # thing_id is a reference to the other thing you are trying to find
            # (which of course could even be your thing that has the point!)
            # and point_id is an optional point reference on that thing.
            #
            # Think of this like DNS, turning names into addresses
            # so when we later say bind_point(from_addr, to_addr)
            # it can be passed in and turned into a subscribed point
            #
            # Also it can, and will, be used to validate that an address exists
            # so that it can be bound to with confidence later.
            # So, passing in a GUID should return the same GUID to imply
            # that it has been checked and can be bound to later.
            #
            # Can find Things or Points with this.
            # e.g. iot.py exposes it in two ways:
            #   iot.find_thing("utilitypole")     -> Space.find(thing_id="utility_pole", point_id=None)
            #   iot.find("utilitypole", "camera") -> Space.find(thing_id="utility_pole", point_id="camera")
            #
            # Returns a GUID (a reference to a thing/point that can be bound to)

            # Check parameter types first
            if not isinstance(thing_id, string_types):
               ##and not isinstance(thing_id, IOT.Thing.Thing):
                raise ValueError("thing_id must be str, got:%s" % str(type(thing_id)))

            if point_id is not None:
                if not isinstance(point_id, string_types):
                   ##and not isinstance(point_id, IOT.Point.Point):
                    raise ValueError("point_id must be str, got:%s" % str(type(point_id)))

            # find(thing_inst, point_inst) or find(thing_inst, None) return GUID
            ##if isinstance(thing_id, IOT.Thing.Thing):
            ##    if point_id is None:
            ##        return thing_id.guid # GUID of thing
            ##    elif isinstance(point_id, IOT.Point.Point):
            ##        return point_id.guid # GUID of point
            ##    # if point-id is a string, it will be handled further down in this function

            # find("thing_str", "point_str") or find("thing_str", None)
            # convert thing_str to an IOT.Thing.Thing instance
            if thing_id in self.__id_to_real_object or thing_id in self.__id_to_virtual_object:
                ##HERE## not sure this is safe for all scenarios
                if thing_id in self.__id_to_real_object:
                    thing_object = self.__id_to_real_object[thing_id]
                else:
                    thing_object = self.__id_to_virtual_object[thing_id]
            else:
                thing_guid = None
                try:
                    thing_guid = Validation.guid_check_convert(thing_id)
                except ValueError:
                    pass

                thing_list = self.__agent.list(all_my_agents=True, limit=500)  # NOTE: default limit=500
                if len(thing_list) == 500:
                    warning("thing_list is truncated at 500")

                if thing_guid is not None:
                    ##trace("checking thing_guid is in thing_list...")
                    found = False
                    for lid in thing_list:
                        if thing_list[lid]['id'] == thing_guid:
                            thing_object = IOT.Thing.Thing(self.__agent, lid, thing_list[lid]['id'], thing_list[lid]['epId'])
                            found = True
                            break

                    if not found:
                        raise ValueError("thing not found:%s" % str(thing_id))

                else:
                    ##trace("checking if thing_id is a lid...")
                    if not thing_id in thing_list:
                        raise ValueError("thing not found:%s" % str(thing_id))

                    # Found a local thing so change thing_id into IOT.Thing instance
                    thing_object = IOT.Thing.Thing(self.__agent, thing_id, thing_list[thing_id]['id'], thing_list[thing_id]['epId'])

            # thing_id is now guaranteed to be IOT.Thing.Thing
            # work out if this is a thing or point search
            if point_id is None:
                return thing_object.guid # GUID of thing

            # find(thing_inst, "guid_or_point_str")
            ##trace("checking if point_id is a guid...")
            try:
                point_id = Validation.guid_check_convert(point_id)
            except ValueError:
                pass # it's not a GUID
            else:
                # It is a GUID
                # TODO: If Thing containing Point GUID is not public then can't get any info about it
                # TODO: if guid is non existent, this incorrectly returns it as valid.
                return point_id # GUID of point

            # find(thing_inst, local_point_id)
            ##trace("checking local point id...")
            feed_list = thing_object.list_feeds()
            if point_id in feed_list:
                return feed_list[point_id]['id'] # GUID of point
            control_list = thing_object.list_controls()
            if point_id in control_list:
                return control_list[point_id]['id'] # GUID of point

            raise ValueError("point not found:%s" % str(point_id))

        #----- RESTORE INTERNAL STATE ON SCRIPT RESTART ---------------------------

        def restore(self): #IoticSpace.restore
            """Restore things, controls, feeds, control attaches and feed follows"""
            #Called once when the space reboots
            self.__cache = {}

            # build the cache, and restore 'upstairs'
            things = self.__agent.list(limit=100) #TODO: Manifest constant
            if len(things) == 100:
                warning("thing_list is truncated at 100")

            for thing_name in things: # thing_name is the lid
                assert_is_str(thing_name, "restore")
                info("  restore thing:%s" % thing_name)
                # ask upstairs to create a Thing, it will call our self.create_thing in the process
                # which updates the cache, so we can get the downstairs object from that.

                #this will trigger a call-down to our self.create_thing
                iot_thing = self._upper_create_thing(thing_name)
                #which means that the cache should now be filled by the time we get back here
                iotic_thing = self.__cache[thing_name]['thing']

                # restore real feeds
                for feed_name in iotic_thing.list_feeds(): # feed_name is the lid
                    assert_is_str(feed_name, "restore2")
                    info("    restore feed:%s" % feed_name)
                    # call upstairs create_feed, and it will call self.create_feed
                    # which updates the cache with the downstairs feed object
                    iot_thing.create_feed(feed_name)

                # restore real controls
                for control_name in iotic_thing.list_controls(): # control_name is the lid
                    assert_is_str(control_name, "restore3")
                    info("    restore control:%s" % control_name)
                    iot_thing.create_control(control_name)

                # process all bindings for Thing(t) - i.e. the non-owning end
                # for feeds followers, this ensures that incoming data callbacks are knitted
                # for control attachers, this ensures there is an upper object that can be used with ask() or tell()

                info(" restore bindings for %s" % str(thing_name))
                for subid, sub in iotic_thing.list_connections().items():
                    # note: sub contains type, 'id' = remote point guid, 'entityId' = remote thing id containing point
                    if sub['type'] == R_FEED:
                        point_addr = sub['id']
                        ##HERE this is a subid, need the pointid
                        ##trace("    refollow:%s -> %s" % (thing_name, sub.__repr__()))
                        assert_is_str(point_addr, "restore4")
                        p = self._upper_rebind_point(parent_thing=iot_thing, point_name="refollow(%s)" % str(point_addr), point_addr=point_addr)

                    elif sub['type'] == R_CONTROL:
                        point_addr = sub['id']
                        ##HERE this is a subid, need the pointid
                        ##trace("    reattach:%s -> %s" % (thing_name, sub.__repr__()))
                        assert_is_str(point_addr, "restore5")
                        p = self._upper_rebind_point(parent_thing=iot_thing, point_name="reattach(%s)" % str(point_addr), point_addr=point_addr)

        #---- BIND AND UNBIND -----------------------------------------------------

        def bind_point(self, from_addr, to_addr): #IoticSpace.bind_point
            """Create a binding between from_addr and to_addr"""
            assert_is_str(from_addr, "bind_point")
            assert_is_str(to_addr, "bind_point2")
            # Initiates a follow or an attach

            # check parameter types
            ##if not isinstance(from_addr, IOT.Thing.Thing):
            if not isinstance(from_addr, string_types):
                raise ValueError("from_addr must be an instance of str, got:%s" % str(type(from_addr)))

            if not isinstance(to_addr, str): ##TODO: string_types??
                raise ValueError("to_addr must be an instance of str, got:%s" % str(type(to_addr)))

            try: # IS IT A FEED FOLLOW?
                # from_addr will be the Thing that wants to follow
                def feed_receive_data_cb(payload):
                    ##trace("feed receives data:%s" % str(payload))
                    # The callback receives a single dict argument, with keys of:
                    #   'data' # (decoded or raw bytes)
                    #   'mime' # (None, unless payload was not decoded and has a mime type)
                    #   'pid'  # (the global id of the feed from which the data originates)
                    #   'time' # (datetime representing UTC timestamp of share)
                    data = payload['data']
                    mime = payload['mime']
                    data = self.__data_decode(data, mime)
                    from_addr  = payload['pid']
                    #NOTE: to_addr and pid are the same, could use either. Safer to use pid.
                    assert_is_str(from_addr, "bind_point3")
                    self.process(Space.DATA, data, from_addr=from_addr)

                from_object = self.__id_to_real_object[from_addr]
                rf = from_object.follow(to_addr, callback=feed_receive_data_cb)
                self.__id_to_virtual_object[to_addr] = rf
                rfa = rf.guid
                assert_is_str(rfa, "bind_point4")
                # Because we are synthesising BOUND locally, we have to swap the addresses
                self.bind_ok(to_addr, from_addr)
                return rfa # will be a RemoteFeed object guid address
                #NOTE: return result not used by upstairs (yet?)

            except ValueError:
                try: # IS IT A CONTROL ATTACH?
                    # from_addr will be the Thing that wants to attach
                    from_object = self.__id_to_real_object[from_addr]
                    rc = from_object.attach(to_addr)
                    self.__id_to_virtual_object[to_addr] = rc
                    rca = rc.guid
                    # Because we are synthesising BOUND locally, we have to swap the addresses
                    # Note, these addresses will be guid's, which is what will be handled upstairs
                    assert_is_str(rca, "bind_point5")
                    self.bind_ok(to_addr, from_addr)
                    # Cache it, so that later we can turn to_addr into a RemoteControl object
                    # This is because upstairs cannot support address mutation through the bind process
                    # due to the guid having already been entered in it's internal routing tables.
                    ##DEPRECATED self.__attachments[to_addr] = rc

                    return rca # will be a RemoteControl object
                    #NOTE: return result not used by upstairs (yet?)

                except Exception as e:
                    self.bind_failed(from_addr, to_addr)
                    raise e

        def unbind_point(self, from_addr, to_addr): #IoticSpace.unbind_point
            """remove the binding that is between from_addr and to_addr"""
            assert_is_str(from_addr, "unbind_point")
            assert_is_str(to_addr, "unbind_point2")
            # Initiate an unfollow or a detach
            # If you need to know if it is a feed or a control,
            # we have that state upstairs and could pass it in as a bind type
            # from_addr would be the thing that is doing the binding
            # mainly so that upstairs can associate this subscription
            # with the thing that owns it. It routes the NOTIFY_UNBOUND
            # to that upstairs object.
            # return: nothing
            # exception: any
            # NOTE: must at least send up callback Space.NOTIFY_UNBOUND
            # but could come back later
            #
            # Perhaps a cache of subs between from_addr to to_addr
            # Thing.unfollow can be used for any subscription id (feed or control)
            # https://pythonhosted.org/py-IoticAgent/IOT/Thing.m.html#IoticAgent.IOT.Thing.Thing.unfollow
            #
            # Alternatively a RemoteFeed or RemoteControl could be passed here?
            # thing.unfollow( remote_feed.subid )
            # Need to check what object types we are getting as addresses.

            ##trace("unbind_point: FROM %s TO:%s" % (str(from_addr), str(to_addr)))
            ##trace("unbind_point: FROM %s TO:%s" % (str(type(from_addr)), str(type(to_addr))))

            # check parameter types
            #if not isinstance(from_addr, IOT.Thing.Thing):
            if not isinstance(from_addr, string_types):
                raise ValueError("from_addr must be an instance of str, got:%s" % str(type(from_addr)))

            if not isinstance(to_addr, str):
                raise ValueError("to_addr must be an instance of str, got:%s" % str(type(to_addr)))

            #PROBLEM: Not possible to unfollow from a guid, even though we acquired the point using that guid??
            #Note: Might need the subsid here rather than the pid (guid) of the point.
            # from_addr.unfollow(to_addr)

            # Helper function to find subscription id given thing lid and remote point guid
            obj = self.__id_to_real_object[from_addr]
            from_addr_lid = obj.lid
            assert_is_str(from_addr_lid, "unbind_point3")
            self.__unbind_by_remote_point_guid(from_addr_lid, to_addr)

            # Because we are synthesising UNBOUND locally, we have to swap the addresses
            self.unbind_ok(to_addr, from_addr)


        def count_bindings_for(self, point_addr): #IoticSpace.count_bindings_for
            assert_is_str(point_addr, "count_bindings_for")
            # point_addr is the opaque object that you want to count bindings for
            # It could be just [0,1] as we only check for if it is zero upstairs.
            # return: number
            # exception: any
            #if not isinstance(point_addr, IOT.Point.Point):
            if not isinstance(point_addr, string_types):
                raise ValueError("point_addr must be an instance of str, got:%s" % str(type(point_addr)))
            point_obj = self.__id_to_real_object[point_addr]
            return len(point_obj.list_followers())

        ##def search_point(self):
        ### https://pythonhosted.org/py-IoticAgent/IOT/Client.m.html#IoticAgent.IOT.Client.Client.search

        ##def delete_point()
        ### https://pythonhosted.org/py-IoticAgent/IOT/Thing.m.html#IoticAgent.IOT.Thing.Thing.delete_feed
        ### https://pythonhosted.org/py-IoticAgent/IOT/Thing.m.html#IoticAgent.IOT.Thing.Thing.delete_control

        ##def delete_thing()
        ### https://pythonhosted.org/py-IoticAgent/IOT/Client.m.html#IoticAgent.IOT.Client.Client.delete_thing

        #----- DATA TRANSFER INTERFACE

        def send_to(self, from_thing_id, to_point_addr, data, confirmed=False): #IoticSpace.send_to
            """Send a message to a control"""
            assert_is_str(from_thing_id, "send_to")
            assert_is_str(to_point_addr, "send_to2")
            # cause a data payload to be sent (this is attacher_send->control)
            # could be blocking or non blocking. Prefer non blocking if possible
            # thing_id will be the thing_id opaque returned by create_thing
            # to_point_addr will be the addr returned by find() or search()
            # return: nothing
            # exception: any

            # https://pythonhosted.org/py-IoticAgent/IOT/RemotePoint.m.html
            #
            # For the control to confirm tell you call confirm_tell on the client instance
            # passing the control_cb args and success=True/False
            # https://pythonhosted.org/py-IoticAgent/IOT/Client.m.html#IoticAgent.IOT.Client.Client.confirm_tell

            # unhelpfully, to_point_addr is a pid guid
            # hard to fix, because upstairs does not support address mutating,
            # by the time it has asked to bind() the guid is already in it's registration
            # table and that's how it routes to handlers. So we use a local cache here
            # to resolve.
            ##DEPRECATED rc = self.__attachments[to_point_addr] # will fail if not found
            rc = self.__id_to_virtual_object[to_point_addr] # will fail if not found
            if not isinstance(rc, IOT.RemotePoint.RemoteControl):
                raise ValueError("remote_control must be instance of IOT.RemotePoint.RemoteControl, got:%s" % str(type(rc)))

            data, mime = self.__data_encode(data)

            if not confirmed:
                ##trace("ask:%s %s %s" % (str(from_thing_id), str(to_point_addr), str(data)))
                rc.ask(data, mime=mime)
            else:
                rc.tell(data, mime=mime, timeout=5) #TODO: Manifest constant

        def send_from(self, point_addr, data): #IoticSpace.send_from
            """Send a message from a feed"""
            assert_is_str(point_addr, "send_from")
            # cause a data payload to be sent (this is feed_send->follower)
            # could be blocking or non blocking. Prefer non blocking if possible
            # point_addr will be the opaque object that identifies this producing point
            # return: nothing
            # exception: any
            #
            # Point.share https://pythonhosted.org/py-IoticAgent/IOT/Point.m.html#IoticAgent.IOT.Point.Feed.share

            # usefully, point_addr is a IOT.Point.Feed object
            point_object = self.__id_to_real_object[point_addr]
            if not isinstance(point_object, IOT.Point.Feed):
                raise ValueError("point_object must be instance of IOT.Point.Feed instance, got:%s" % str(type(point_addr)))

            data, mime = self.__data_encode(data)
            point_object.share(data, mime=mime)



    i = IoticSpace(*args, **kwargs)
    return i

# END
