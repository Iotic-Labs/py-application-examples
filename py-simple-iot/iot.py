# iot.py  18/11/2016  D.J.Whale

import time
import sys
import os


#===== MODULE CONFIGURATION ===================================================

# auto_boot
#   If True, this will auto boot the iot.py system when the module is imported.
#   If False, you must import iot and then do iot.boot()
#   Turning off auto-boot is useful for certain types of testing,
#   and also if you want the user program to change defaults before booting

class CONFIG(object):
    # Any of these can be overriden on sys.argv[]
    # booleans are True if present, not defined/defaulting if absent
    auto_boot            = True
    confirm_names        = False
    default_thing_name   = "thing"
    default_feed_name    = "feed"
    default_control_name = "control"
    connect_retries      = (5, 10) # 5 retries, retry every 10 seconds
    space                = None

    def keys(self):
        k = dir(self)
        return k

    def __getitem__(self, item):
        return self.keys()[item]

CONFIG = CONFIG()

# Put all argv args into config as strings
for v in sys.argv[1:]:
    # parse key=value or key
    parts = v.split('=')
    key = parts[0]
    if len(parts) == 1:
        value = True
    else:
        value = parts[1]
    setattr(CONFIG, key, value)

def get_main():
    """returns: (module, path_to_dir, basename, ext)"""
    import sys, os
    main_mod = sys.modules["__main__"]

    if not hasattr(main_mod, "__file__"):
        # Must be using the Python shell
        #print("type dir(iot) for a list of commands")
        return None # No main module

    file = main_mod.__file__           # 'start.py'
    abs = os.path.abspath(file)        # 'users/fred/start.py'
    root, ext = os.path.splitext(abs)  # ('users/fred/start', '.py')
    base = os.path.basename(root)      # 'start'
    dir = os.path.dirname(root)        # '/users/fred'
    return main_mod, dir, base, ext    # (main, '/users/fred', 'start', '.py')


main = get_main() # (0:main_mod, 1:dir, 2:base, 3:ext)
if main is None:
    # must be running from interactive shell
    DEFAULT_INI_NAME = "iot.ini"
    FALLBACK_INI_NAME = None
else:
    # There is a main, so it must have a directory and filename
    DEFAULT_INI_NAME = main[1] + '/' + main[2] + '.ini'
    FALLBACK_INI_NAME = main[1] + "/iot.ini"

if sys.version_info[0] > 2:
    def execfile(fname, global_vars=None, local_vars=None):
        with open(fname) as f:
            code = compile(f.read(), fname, 'exec')
            exec(code, global_vars, local_vars)

def configure():
    # OPEN SCRIPT INI FILE
    ##trace("configure:%s" % str(DEFAULT_INI_NAME))

    g = {}

    # Copy all CONFIG attributes into 'config' as dict keys
    # so they are in scope when the .ini file is run
    config = {}
    for k in dir(CONFIG):
        if k.startswith("__") and k.endswith("__"):
            pass # ignore underscored entries
        else:
            config[k] = getattr(CONFIG, k)

    if os.path.exists(DEFAULT_INI_NAME):
        #print("using ini:%s" % DEFAULT_INI_NAME)
        execfile(DEFAULT_INI_NAME, g, config)

    elif FALLBACK_INI_NAME is not None and os.path.exists(FALLBACK_INI_NAME):
        execfile(FALLBACK_INI_NAME, g, config)
        print("using ini:%s" % FALLBACK_INI_NAME)

    else:
        return # There is no external config file

    # turn all keys into attributes inside CONFIG
    for k in config:
        setattr(CONFIG, k, config[k])

# auto configure on loading iot module
configure()


#===== HELPER UTILITIES =======================================================

def log(m): # DECORATOR
    def inner(*args, **kwargs):
        print("calling:%s" % m.__name__)
        return m(*args, **kwargs)

def trace(msg):
    print("iot:%s" % str(msg))

def info(msg):
    print("iot:%s" % str(msg))

def warning(msg):
    print("warning:%s" % str(msg))

#TODO: might also want a fail() that explicitly does sys.exit
def error(msg):
    """Raise an error and stop"""
    # Note, most usages of this do return error()
    # this is so that the code reachability analyser still does useful work.
    print("\n" + ('*' * 80))
    print("ERROR:%s" % str(msg))
    print('*' * 80)
    raise RuntimeError(msg)

def unimplemented(m): # DECORATOR
    def uf(*args):
        print("unimplemented: %s(%s)" % (m.__name__, str(args)))
        return "[return: from unimplemented %s(%s)]" % (m.__name__, str(args))
    return uf

class Timer():
    def __init__(self, ratesec=1):
        self.config(ratesec)

    def config(self, ratesec):
        self.rate = ratesec
        self.sync()

    def sync(self, timenow=None):
        if timenow == None:
            timenow = time.time()
        self.nexttick = timenow + self.rate

    def check(self):
        """Maintain the timer and see if it is time for the next tick"""
        now = time.time()

        if now >= self.nexttick:
            # asynchronous tick, might drift, but won't stack up if late
            self.sync(now)
            return True # timeout occurred

        return False # not timed out yet


#===== RUNNER =================================================================

class Runner(object):

    FASTEST = "fastest"
    TICK_RATE = 1

    def __init__(self): #Runner.__init__ ##2HERE## needs a reference to a single space, not default_space
        self.running = False
        self.next_tick = None
        self.in_tick = False

    def set_parent(self, parent): #Runner.set_parent
        # Due to a dependency race, we have to set the parent later
        self.parent = parent

    def auto_start(self, method): #Runner.auto_start DECORATOR
        """Auto start on entry, auto tick on exit"""
        ##trace("auto_start:%s" % str(method.__name__))
        def wrapped(*args, **kwargs):
            if not self.running:
                ##warning("You forgot to iot.start(), doing it for you now")
                self.start()

            r = method(*args, **kwargs)

            if self.next_tick == None:
                #This could be high bandwidth output
                ##warning("no iot.tick(), doing it for you now")
                self.__tick()
            return r
        return wrapped

    def start(self): #Runner.start
        if self.running:
            #Various methods will auto start, so this can't be an error
            ##warning("start() called when already running - ignoring")
            return
        self.parent.start()

        ##trace("start:will start looper") #TODO
        self.running = True

        import atexit
        atexit.register(self.stop, auto=True)

    def run(self, script=None, for_time=None): #Runner.run
        e = None

        if script is None:
            # Loop until error or time exceeded
            ##trace("run() until stopped")
            self.start() # only do this if not already started
            start_time = time.time()
            if for_time is not None:
                end_time = start_time + for_time
            else:
                end_time = None

            try:
                while self.running: # Any call to iot.stop() will make loop terminate
                    self.tick() # cooperatively ticked, rather than thread ticked
                    if end_time is not None:
                        now = time.time()
                        if now >= end_time:
                            break # max run time reached
            except KeyboardInterrupt:
                info("Stopped by user")
            #except Exception as e: # e.g. might be KeyboardInterrupt
            #    trace("run exception:%s" % str(e))
            ##if self.running: # just rely on the atexit()
            ##    self.stop()

        else:
            # Run the script until it exits
            # NOTE: no way to tick() Repeater aspect of Point?
            ##trace("run() with test script")
            self.start() # only do this if not already started
            try:
                script()
            except KeyboardInterrupt:
                info("Stopped by user")
            #except Exception as e:
            #    trace("script exception:%s" % str(e))

            ##if self.running: # just rely on the atexit()
            ##    self.stop()

        if e is not None:
            #TODO: dump stack trace so user can understand exception!
            raise e # raise any script exception

    # Due to a dependency race, this is wrapped later
    def tick(self, rate=None): #Runner.tick
        """The user app calls this tick when it cooperatively schedules."""

        if rate is None:
            rate = self.TICK_RATE

        #Also if there is a thread started, it will call this tick.

        if rate == self.FASTEST:
            ##trace("tick")
            self.__tick()

        else:
            # Tick cooperative tasks using time horizons
            now = time.time()
            if self.next_tick is None or now >= self.next_tick:
                self.next_tick = now + rate
                trace("tick") ## throttled to every %s seconds" % str(rate))
                self.__tick()

    def __tick(self): #Runner.real_tick
        if not self.in_tick:
            self.in_tick = True
            self.parent.real_tick()
            self.in_tick = False

    def stop(self, auto=False): #Runner.stop
        ##if auto:
        ##    if not self.running:
        ##        ##warning("auto stop, but was not started - ignoring")
        ##        pass
        ##    else:
        ##        pass ##warning("you forgot to iot.stop(), doing it for you now")
        ##else:
        ##    if not self.running:
        ##        return error("iot.stop() called, but was not running")

        info("stopping...")
        # Must disconnect here, otherwise some spaces will leave threads running
        # and the script will never stop properly even on exception.
        default_space.disconnect() ##2HERE## needs a reference to running space, not default_space
        self.running = False
        info("stopped.")

# There is a single runner, at the moment
##Space uses runner, so there is a circular reference here
runner = Runner() ##2HERE## pass in default_space??
auto_start = runner.auto_start # global DECORATOR
runner.tick = auto_start(runner.tick) # self-decorate our tick() method
##2HERE##, probably have one Runner per space.
#can then have multi-space and custom runners in each space.

#===== SPACE base class =======================================================

class Space():

    # Notification message values
    NOTIFY_BIND          = "BIND"
    NOTIFY_BIND_FAILED   = "BIND_FAILED"
    NOTIFY_BOUND         = "BOUND"

    NOTIFY_UNBIND        = "UNBIND"
    NOTIFY_UNBIND_FAILED = "UNBIND_FAILED"
    NOTIFY_UNBOUND       = "UNBOUND"

    # Data types for messaging
    META                         = "META"
    DATA                         = "DATA"

    def __init__(self): #Space.__init__
        self.listeners = {} # key (type, from_addr, to_addr) -> listof [object]
        ##DEPRECATING
        global runner ##2HERE## no!
        self.runner = runner ##2HERE## no! pass it in.
        #Note, self.runner is not used in Space, it will be used by subclasses.
        #so perhaps pass it in in those subclass initialisers instead?

    #OPTIONAL
    def identify(self, identity): #Space.identify
        pass # nothing to do

    #OPTIONAL
    def authenticate(self, credentials): #Space.authenticate
        pass # nothing to do

    #OPTIONAL
    def tick(self, limit=None): # Space.tick
        pass # Nothing to do here

    def bind_ok(self, from_addr, to_addr): #Space.bind_ok
        # default action is to locally ack
        # but a Space implementation can override.
        # DBSpace does, for example, because acks have to go via a messaging layer first
        self.process(Space.META, Space.NOTIFY_BOUND, from_addr, to_addr)

    def bind_failed(self, from_addr, to_addr): #Space.bind_failed
        # default action is to locally nack
        # but a Space implementation can override.
        # DBSpace does, for example, because acks have to go via a messaging layer first
        self.process(Space.META, Space.NOTIFY_BIND_FAILED, from_addr, to_addr)

    def unbind_ok(self, from_addr, to_addr): #Space.unbind_ok
        # default action is to locally ack
        # but a Space implementation can override.
        # DBSpace does, for example, because acks have to go via a messaging layer first
        self.process(Space.META, Space.NOTIFY_UNBOUND, from_addr, to_addr)

    def unbind_failed(self, from_addr, to_addr): #Space.unbind_failed
        # default action is to locally nack
        # but a Space implementation can override.
        # DBSpace does, for example, because acks have to go via a messaging layer first
        self.process(Space.META, Space.NOTIFY_UNBIND_FAILED, from_addr, to_addr)

    #OPTIONAL
    def _meta_in_point(self, from_addr, to_addr, data): #Space._meta_in_point
        # This is a hook where you can update any internal data structures
        # when meta-messages come in from the space.
        # if you are using locally synthesised BOUND and UNBOUND messages,
        # you might not need to process these.
        pass # default action is to do nothing

    def is_thing_addr(self, addr): #Space.is_thing_addr
        """Is this a thing address??"""
        raise RuntimeError("is_thing_addr must be implemented by the child class")
        # This is address space specific, so you must implement it.

    def register_for(self, o, msg_type, from_addr=None, to_addr=None): #Space.register_for

        ##print("register_for")
        ##print("from_addr:%s %s" % (str(from_addr), str(type(from_addr))))
        ##print("to_addr:%s %s" % (str(to_addr), str(type(to_addr))))

        key = (msg_type, from_addr, to_addr)

        if key in self.listeners:
            l = self.listeners[key]
            l.append(o)
        else:
            self.listeners[key] = [o]

    def unregister_for(self, o, msg_type, from_addr=None, to_addr=None): #Space.unregister_for
        key = (msg_type, from_addr, to_addr)

        if not key in self.listeners:
            return error("Attempt to unregister a non existent registration")
        l = self.listeners[key]
        l.remove(o)
        if len(l) == 0:
            del self.listeners[key]

    def _upper_create_thing(self, thing_name): #Space._upper_create_thing
        ##2HERE## use self.runner
        return Thing.create_thing(thing_name, parent=runner, space=self)

    def _upper_rebind_point(self, parent_thing, point_name, point_addr):
        p = Point(parent_thing=parent_thing, name=point_name)
        p._become_ref(self, point_addr, register=True)
        p.rebind()
        return p

    def dump(self, printer=None): #Space.dump
        def default_printer(msg):
            print(msg)
        if printer is None:
            printer = default_printer

        for l in self.listeners:
            printer("%s -> %s" % (str(l), str(self.listeners[l])))

    def process(self, msg_type, data, from_addr=None, to_addr=None): # Space.process
        if msg_type == Space.META:
            return self.process_meta(data, from_addr=from_addr, to_addr=to_addr)
        elif msg_type == Space.DATA:
            return self.process_data(data, from_addr=from_addr, to_addr=to_addr)
        else:
            return error("Unknown type for process:%s" % str(msg_type))

    def process_meta(self, data, from_addr=None, to_addr=None): # Space.process

        ##trace("process_meta")
        ##trace("from_addr:%s %s" % (str(from_addr), str(type(from_addr))))
        ##trace("to_addr:%s %s" % (str(to_addr), str(type(to_addr))))

        # Work out wildcard addresses
        k_from_addr = from_addr
        k_to_addr   = to_addr
        if self.is_thing_addr(from_addr):
            k_from_addr = None # wildcard
        elif self.is_thing_addr(to_addr):
            k_to_addr = None # wildcard

        key = (Space.META, k_from_addr, k_to_addr)
        if not key in self.listeners:
            return 0 # nothing was interested
        interested = self.listeners[key]

        # dispatch to each interested listener
        #TODO: Outstanding query about how to handle exceptions in handlers

        for o in interested:
            ##trace("Space dispatches to %s meta(%s %s)" % (o.__repr__(), str(from_addr), str(data)))

            method_name = "handle_%s" % str(data)
            if not hasattr(o, method_name):
                warning("Object %s does not know how to handle:%s" % (o.__repr__(), str(method_name)))
                result = False
            else:
                m = getattr(o, method_name)
                result = m(self, from_addr)

            # based on the result, we either do or don't do the data structure update
            if result is None or result:
                self._meta_in_point(from_addr, to_addr, data)
            else:
                warning("state not updated with META:%s" % str(data))

        return len(interested) # number of users (possibly not all serviced)

    def process_data(self, data, from_addr=None, to_addr=None): # Space.process

        # Make sure wildcards are set up
        k_from_addr = from_addr
        k_to_addr   = to_addr
        if self.is_thing_addr(from_addr):
            k_from_addr = None # wildcard
        elif self.is_thing_addr(to_addr):
            k_to_addr = None # wildcard

        key = (Space.DATA, k_from_addr, k_to_addr)
        if not key in self.listeners:
            return 0 # nothing was interested
        interested = self.listeners[key]

        # dispatch to each interested listener
        #TODO: Outstanding query about how to handle exceptions in handlers

        # work out which address will be of interest to the receive handler
        if k_from_addr is None:
            addr = to_addr
        else:
            addr = from_addr

        for o in interested:
            if not hasattr(o, "receive_data"):
                return warning("Object %s doesn't have a receive_data method" % o.__repr__())
            o.receive_data(addr, data)

        return len(interested) # number of users (possibly not all serviced)


#===== MEMORY SPACE ===========================================================
#
# MemorySpace is a in-memory iotic like space, used for in-process testing.
# Useful for regression test harnesses that run in a single process.
#
# Control and Feed updates are sent immediately to the receiving handler
# of the follower or attacher

##3HERE needs to be re-integrated with all the changes made to Space
##Use DBSpace as a reference. Mainly its the inverted tick pattern
#and the meta dispatch to named methods that need re-integrating

class MemorySpace(Space):

    def __init__(self, agent_id=None): #MemorySpace.__init__
        Space.__init__(self)
        self.things = {}
        self.prop_agent_id = agent_id
        # for feed producer:
        #   data: things[from_thing_id].points[from_point_id].bindings[]  = list[to_thing_id, ...]
        #   meta: things[to_thing_id]  .points[to_point_id]  .metarxqueue = msg(from_thing_id, None, notification)
        # for feed consumer:
        #   data: things[to_thing_id]  .rxqueues[(from_thing_id, from_point_id)] = data

        # for attached controls
        #   data: things[from_thing_id].bindings[] = list[(to_thing_id, to_point_id), ...]
        # rxqueue:
        #   data: things[to_thing_id].points[to_point_id].rxqueue

    @staticmethod
    def _split_addr(addr): #MemorySpace._split_addr
        """Split a tuple into thing_id, point_id"""
        if addr is None:
            return None, None # thing_id, point_id
        if type(addr) == tuple:
            return addr[0], addr[1] # thing_id, point_id
        return addr, None # thing_id, point_id

    @staticmethod
    def _join_addr(thing_id, point_id): #MemorySpace._join_addr
        """Join thing_id, point_id into a tuple"""
        return (thing_id, point_id)

    def is_thing_addr(self, addr): #MemorySpace.is_thing_addr
        """Is this a thing address??"""
        if addr is None:
            return False
        if addr[1] is None:
            return True
        return False

    @property
    def agent_id(self): # PROPERTY GETTER
        # Don't really care if it is None
        return self.prop_agent_id

    def reset(self): #MemorySpace.reset
        #trace("MemorySpace:RESET")
        self.things = {}
        #Note, this does not reset handlers in Thing and Point.

    def identify(self, identity): #MemorySpace.identify
        pass # nothing to do

    def authenticate(self, credentials): #MemorySpace.authenticate
        pass # nothing to do

    def connect(self): #MemorySpace.connect
        pass # nothing to do

    def disconnect(self): #MemorySpace.disconnect
        pass #nothing to do

    def get_thing_addr(self, thing_name): # MemorySpace.get_thing_addr
        """Turn a thing_name into a thing_addr"""
        if thing_name in self.things:
            return thing_name # for MemorySpace, they are the same
        return error("There is no Thing called '%s'" % thing_name)

    def restore(self): #MemorySpace.restore
        pass # Nothing to do, no persistence.

    def create_thing(self, thing_name): #MemorySpace.create_thing
        if thing_name in self.things:
            return thing_name # thing_id
        else:
            class Thing(): # a simple internal Thing wrapper
                points = {}
                bindings = {}
                rxqueues = {}
                metarxqueue = {}
                def __repr__(self):
                    return "MemorySpace.Thing(%s)" % thing_name
            self.things[thing_name] = Thing()
            return thing_name # thing_id

    def _create_point(self, thing_id, point_name): #MemorySpace._create_point
        # returns point_addr
        point_id = point_name
        thing_rec = self.things[thing_id]
        if not point_id in thing_rec.points:
            class Point(): # A minimal internal Point() wrapper
                bindings = {}
                rxqueue = []
                metarxqueue = []
                def __repr__(self):
                    return "MemorySpace.Point(%s/%s)" % (str(thing_id), str(point_name))
            thing_rec.points[point_id] = Point()
        return self._join_addr(thing_id, point_name)

    def create_feed(self, thing_id, feed_name): #MemorySpace.create_feed
        # returns point_addr
        return self._create_point(thing_id, feed_name) # point_addr

    def create_control(self, thing_id, control_name): #MemorySpace.create_control
        # returns point_addr
        return self._create_point(thing_id, control_name) # point_addr

    def _set_visibility(self, thing_id, flag): #MemorySpace._set_visibility
        #set/clear visible flag, for search results
        pass #TODO

    def show_thing(self, thing_id): #MemorySpace.show_thing
        self._set_visibility(thing_id, True)

    def hide_thing(self, thing_id): #MemorySpace.hide_thing
        self._set_visibility(thing_id, False)

    def _set_advertisement(self, thing_id, point_id, flag): #MemorySpace._set_advertisement
        # set/clear visibility flag, for searching
        pass #TODO

    #TODO: visibility_point passed FOC?
    def advertise_feed(self, point_addr): #MemorySpace.advertise_feed
        thing_id, point_id = self._split_addr(point_addr)
        self._set_advertisement(thing_id, point_id, True)

    def unadvertise_feed(self, point_addr): #MemorySpace.unavertise_feed
        thing_id, point_id = self._split_addr(point_addr)
        self._set_advertisement(thing_id, point_id, False)

    def offer_control(self, point_addr): #MemorySpace.offer_control
        thing_id, point_id = self._split_addr(point_addr)
        self._set_advertisement(thing_id, point_id, True)

    def unoffer_control(self, point_addr): #MemorySpace.unoffer_control
        thing_id, point_id = self._split_addr(point_addr)
        self._set_advertisement(thing_id, point_id, False)

    def find(self, thing_id, point_id=None): #MemorySpace.find
        # thing_id is always the thing_name in MemorySpace
        # point_id is always the point_name in MemorySpace
        # A point_id of None means a thing address (thing_id, None)
        # type(point_id) presumably==int
        return self._join_addr(thing_id, point_id)

    #TODO: This is based on metadata. not done yet.
    ##def search_point(self):
    ##    pass

    def bind_point(self, from_addr, to_addr): #MemorySpace.bind_point
        ##trace("bind_point: from:%s to:%s" % (str(from_addr), str(to_addr)))
        from_thing_id, from_point_id = self._split_addr(from_addr)
        to_thing_id, to_point_id     = self._split_addr(to_addr)

        ##warning("#### TODO: check for already bound in MemorySpace table")
        #TODO if the binding is already in the table, reject it
        #TODO: will need this for bind accept/reject logic
        #TODO: This is asynchronous, we have to wait for response?
        #NOTE: Might have to do this with a when_follow_failed or when_follow_ok
        #when_attach_failed when_attach_ok in the app, so it is naturally async.
        #The service provider end can then just send back an async meta message
        #that is picked up and routed to the user handler to do what they want with it.
        #hmm, hard. For the moment, just assume it works.
        self._notify(from_thing_id, from_point_id, to_thing_id, to_point_id, Space.NOTIFY_BIND)

        # can send us messages, and so we can poll and receive that queue for new data.
        ##trace("BIND: from:%s/%s to:%s/%s" %
        ##      (str(from_thing_id), str(from_point_id), str(to_thing_id), str(to_point_id)))
        # from_point_id will always be None as we are the initiator, not the service provider.
        # So we probably just create a rxdataqueue anyway as we can't differentiate Feed/Control
        # 'we' are from_thing_id
        self.things[from_thing_id].rxqueues[(to_thing_id, to_point_id)] = []
        return to_addr

    def unbind_point(self, from_addr, to_addr): #MemorySpace.unbind_point
        ##trace("unbind_point from:%s to:%s" % (str(from_addr), str(to_addr)))
        #FEED FOLLOW   (from_YOU[feed_thing_id, feed_point_id], to_ME[follower_thing_id, None])
        #CONTROL ATTACH(from_ME[attacher_thing_id, None], to_YOU[control_thing_id, control_point_id])
        #ME is always just a thing.

        ##warning("#### TODO check for already unbound in MemorySpace tabe")
        #TODO: if the binding is not in the table, reject it
        from_thing_id, from_point_id = self._split_addr(from_addr)
        to_thing_id, to_point_id     = self._split_addr(to_addr)

        #TODO: will need this for bind accept/reject logic
        #TODO: This is asynchronous, we have to wait for response?
        #hmm, hard. For the moment, just assume it works.
        self._notify(from_thing_id, from_point_id, to_thing_id, to_point_id, Space.NOTIFY_UNBIND)

        #TODO: should probably really delete the rxdata queue if this is a feed follower
        del self.things[from_thing_id].rxqueues[(to_thing_id, to_point_id)]

    def bind_ok(self, from_addr, to_addr): #MemorySpace.bind_ok
        return error("TODO: bind_ok")

    def bind_failed(self, from_addr, to_addr): #MemorySpace.bind_failed
        return error("TODO: bind_failed")

    def unbind_ok(self, from_addr, to_addr): #MemorySpace.unbind_ok
        return error("TODO: unbind_ok")

    def unbind_failed(self, from_addr, to_addr): #MemorySpace.unbind_failed
        return error("TODO: unbind_failed")


    #def bind_point_respond(self, from_addr, to_addr, success=True): # MemorySpace.bind_point_respond
    #    from_thing_id, from_point_id = self._split_addr(from_addr)
    #    to_thing_id, to_point_id     = self._split_addr(to_addr)
    #
    #    self._notify(from_thing_id, from_point_id, to_thing_id, to_point_id, Space.NOTIFY_BOUND)

    #def unbind_point_respond(self, from_addr, to_addr, success=True): # MemorySpace.unbind_point_respond
    #    ##trace("unbind_point_respond")
    #    from_thing_id, from_point_id = self._split_addr(from_addr)
    #    to_thing_id, to_point_id     = self._split_addr(to_addr)
    #
    #    self._notify(from_thing_id, from_point_id, to_thing_id, to_point_id, Space.NOTIFY_UNBOUND)


    #def delete_point() #TODO: delete from point, for all bindings: delete, _notify(thing_id, point_id)
    #def delete_thing() #TODO: delete from point, for all bindings: delete, _notify(thing_id)

    def count_bindings_for(self, point_addr): #MemorySpace.count_bindings_for
        """Get the number of active bindings for this thing_id/point_id"""
        #This is useful for working out if a feed has any followers
        #We don't really know if the user passed in a feed or a control,
        #but this will still yield the correct number regardless
        thing_id, point_id = point_addr
        f_bindings = self.things[thing_id].points[point_id].bindings
        c_bindings = self.things[thing_id].bindings
        ##trace("f_bindings:%s" % str(f_bindings))
        ##trace("c_bindings:%s" % str(c_bindings))
        return len(f_bindings) + len(c_bindings)

    #----- DATA TRANSFER INTERFACE/SEND

    def send_to(self, from_thing_id, to_point_addr, data, confirmed=False): #MemorySpace.send_to
        #NOTE: This is used when sending to a Control consumer (1:1 or many:1)
        to_thing_id, to_point_id = to_point_addr
        self._send(from_thing_id, None, to_thing_id, to_point_id, data)

    def send_from(self, point_addr, data): #MemorySpace.send_from
        #NOTE: This is used when sending from a Feed to any followers (1:many)
        from_thing_id, from_point_id = point_addr
        #   things[from_thing_id].points[from_point_id].bindings[] = list[to_thing_id, ...]
        bindings =  self.things[from_thing_id].points[from_point_id].bindings
        ##trace("I found %d bindings" % len(bindings))
        for to_thing_id in bindings:
            self._send(from_thing_id, from_point_id, to_thing_id, None, data)

    def _send(self, from_thing_id, from_point_id, to_thing_id, to_point_id, data): #MemorySpace._send
        ##trace("MemorySpace.send from:%s/%s to:%s/%s"%
        ##      (str(from_thing_id), str(from_point_id), str(to_thing_id), str(to_point_id)))
        #sends one message to one destination queue
        #We use queues, so that circular references will still resolve OK.
        if to_point_id is None:
            ##trace("probably to feed follower")
            # to a specific feed follower
            # This is attached to a generic rxqueue for a Thing, and the message
            # contains the sender address, which the other side of MemorySpace
            # will use to route it correctly at the receiving end.
            # for feed consumer: must be set up at bind time
            #   data: things[to_thing_id]  .rxqueues[(from_thing_id, from_point_id)] = data

            #TODO need to key this by right keys
            ##TODO this seems wrong.
            #we need to get a queue for the to_thing_id
            #that is keyed by (from_thing_id, from_point_id)
            #Perhaps we didn't create it in the meta_in_bind yet??
            #or should that be created in the Point??
            queue = self.things[to_thing_id].rxqueues[(from_thing_id, from_point_id)]

        elif from_point_id is None:
            ##trace("probably to attached control")
            # to an attached control
            queue = self.things[to_thing_id].points[to_point_id].rxqueue

        else:
            return error("Invalid send spec")

        queue.append(data)
        ##trace(queue)

    #----- META-INTERACTION INTERFACE SEND/RECEIVE
    # This allows things like remote_bind() requests to be processed

    #meta_out
    def _notify(self, from_thing_id, from_point_id, to_thing_id, to_point_id, notification): #MemorySpace._notify
        #helper function for sending notifications from other methods
        #This ends up polled at _get_notification at the other end.
        ##trace("_notify %s (%s,%s)->(%s,%s)" %
        ##      (str(notification), str(from_thing_id), str(from_point_id), str(to_thing_id), str(to_point_id)))

        msg = (from_thing_id, from_point_id, notification)

        if to_point_id is None:
            # A Thing message
            ##trace("_notify Thing:%s msg:%s" % (str(to_thing_id), str(msg)))
            self.things[to_thing_id].metarxqueue.append(msg)
        else: # A Point message
            ##trace("_notify Point:%s/%s msg:%s" % (str(to_thing_id), str(to_point_id), str(msg)))
            self.things[to_thing_id].points[to_point_id].metarxqueue.append(msg)

    def _meta_in_point(self, from_addr, to_addr, data): #MemorySpace._meta_in_point
        ##trace("meta_in_point:%s %s" % (str(to_addr), str(msg)))
        from_thing_id, from_point_id = self._split_addr(from_addr)
        to_thing_id, to_point_id = self._split_addr(to_addr)

        if data == Space.NOTIFY_BIND:
            if from_point_id is not None:
                ##trace(from_point_id)
                ##trace(type(from_point_id))
                return error("Unexpected not-none point_id %s/%s" % (str(from_thing_id), str(from_point_id)))
            return self._remote_bind(to_thing_id, to_point_id, from_thing_id)

        elif data == Space.NOTIFY_UNBIND:
            if from_point_id is not None:
                return error("Unexpected not-none point_id %s/%s" % (str(from_thing_id), str(from_point_id)))
            return self._remote_unbind(to_thing_id, to_point_id, from_thing_id)

    def _remote_bind(self, to_thing_id, to_point_id, from_thing_id): #MemorySpace._remote_bind
        #to_thing_id, to_point_id is the service provider
        #from_thing_id is the bind requester

        # find the binding table for to_thing_id, to_point_id

        # remember that from_thing_id wants to bind to it
        # for feeds and controls, this allows the service provider to iterate all bindings.
        # for feeds, it gives a list of things that need to be delivered data on a share

        bindings = self.things[to_thing_id].points[to_point_id].bindings
        bindings[from_thing_id] = 1 # now bound
        return True # Done

    def _remote_unbind(self, to_thing_id, to_point_id, from_thing_id): #MemorySpace._remote_unbind
        #to_thing_id, to_point_id is the service provider
        #from_thing_id is the bind requester

        # find the binding table for to_thing_id, to_point_id

        # remember that from_thing_id wants to bind to it
        # for feeds and controls, this allows the service provider to iterate all bindings.
        # for feeds, it gives a list of things that need to be delivered data on a share

        bindings = self.things[to_thing_id].points[to_point_id].bindings
        del bindings[from_thing_id] # now unbound
        return True # Done


#===== DBSPACE ============================================================
#
# The local space is implemented on top of sqlite3 db
# it provides a really simple test harness that is also multi-process
# as long as the processes run on the same computer and can see the .db file
# Note: Don't NFS mount the file, fctl has bugs that stop it working.
# See the notes in the sqlite3 python manual about this fact.

import sqlite3 as sql
import os

class DBSpace(Space):
    DBNAME = "iotic.db"

    @staticmethod
    def ask_delete_db(dbname, force=False): #DBSpace.ask_delete_db
        import os
        if os.path.exists(dbname):
            if force:
                y = "Y"
            else:
                print("There is a left over database:%s" % str(dbname))
                y = raw_input("Do you want to delete it? ").upper()
            if y == "Y":
                print("deleting...")
                os.unlink(dbname)
                print("deleted")
        else:
            print("There is no previous stored database:%s" % str(dbname))

    def __init__(self, agent_id=None): #DBSpace.__init__
        # Confirm uuid dependency exists (<2.5 does not support)
        Space.__init__(self)
        try:
            import uuid
        except:
            return error("uuid module not accessible, can't use DBSpace") # try: space=memory (in CONFIG)

        self.conn = None
        # if agent_id is None, one will be allocated for this session
        self.prop_agent_id = agent_id

    @property
    def agent_id(self): # PROPERTY GETTER
        if self.prop_agent_id is None:
            return error("There is no agent_id currently set")
        return self.prop_agent_id

    def _get_new_agent_id(self): # DBSpace._get_new_agent_id
        with self.conn as conn:
            rows, headings = self._sql("SELECT MAX(rowid) FROM queue WHERE type='META'")
            # There will always be one row, but it might be NULL
            if rows[0][0] is None:
                next_meta_rowid = 0
            else:
                next_meta_rowid = int(rows[0][0])+1

            rows, headings = self._sql("SELECT MAX(rowid) FROM queue WHERE type='DATA'")
            # There will always be one row, but it might be NULL
            if rows[0][0] is None:
                next_data_rowid = 0
            else:
                next_data_rowid = int(rows[0][0])+1

            # A uuid4 (random uuid) is used to create a unique query.
            # this is so that we can easily read back the generated rowid
            # without hitting the mess that is known as last_insert_rowid
            # (as that method is not thread safe, regardless of what the docs say!)
            import uuid # Dependency on this module *only* if using DBSpace
            u = str(uuid.uuid4())
            ##e.g. 16fd2706-8baf-433b-82eb-8c7fada847da 36 chars long
            self._sql("INSERT INTO agent (meta_row_id, data_row_id, uuid) VALUES (?,?,?)", next_meta_rowid, next_data_rowid, u)
            rows, headings = self._sql("SELECT rowid FROM agent WHERE uuid=?", u)
            new_agent_id = rows[0][0]
            return new_agent_id

    def _get_next_rowids(self): # DBSpace._get_next_rowids
        rows, headings = self._sql("SELECT meta_row_id, data_row_id FROM agent WHERE agent_id=?", self.agent_id)
        if len(rows) == 0:
            return error("This agent is not known to the system")
        row = rows[0]
        return (row[0], row[1])

    def _used_rowid(self, table_type, rowid): #DBSpace._used_rowid
        # We can assume the agent already exists, it will fail if not anyway.
        rowid += 1 # the next rowid is this rowid plus one, always. Its a horizon.
        if table_type == Space.META:
            self._sql("UPDATE agent SET meta_row_id=? WHERE agent_id=?", rowid, self.agent_id)
        elif table_type == Space.DATA:
            self._sql("UPDATE agent SET data_row_id=? WHERE agent_id=?", rowid, self.agent_id)
        else:
            return error("Unknown table type:%s" % str(table_type))

    def _sql(self, qs, *args): #DBSpace._sql
        """Select some small number of rows from the database"""
        # Can be used for any type of command
        conn = self.conn

        if qs.startswith("SELECT "):
            c = conn.cursor() # conn created elsewhere
            c.execute(qs, args)
            col_names = [cn[0] for cn in c.description]
            results = c.fetchall()
            c.close() # close the cursor, not the connection
            return results, col_names
        else:
            conn.execute(qs, args)
            conn.commit()

    def create_tables(self): #DBSpace.create_tables
        """Create tables"""
        #TODO: Make this transactional around the whole lot,
        #in case starting lots of processes at the same time

        with self.conn as conn: #NOTE: docs say this makes it transactional for session only?
            # AGENT agent_id is rowid
            self._sql(
            """CREATE TABLE agent (
                agent_id INTEGER PRIMARY KEY,
                uuid VARCHAR(36) NOT NULL UNIQUE,
                meta_row_id INTEGER NOT NULL,
                data_row_id INTEGER_NOT_NULL
            )""")

            # THING
            # Automatically has a 'rowid' column which is the unique thing_id
            self._sql(
            """CREATE TABLE thing (
                agent_id INTEGER NOT NULL,
                name VARCHAR(20),
                visible BOOLEAN,
                PRIMARY KEY(name)
            )""")

            # POINT
            # Automatically has a 'rowid' column which is the unique point_id
            self._sql(
            """CREATE TABLE point (
                thing_id INTEGER NOT NULL,
                type CHAR(1) NOT NULL,
                name VARCHAR(20) NOT NULL,
                visible BOOLEAN,
                PRIMARY KEY(thing_id, name)
            )""")

            # BINDING
            # Automatically has a 'rowid' column which is the unique binding_id
            self._sql(
            """CREATE TABLE binding (
                real_thing_id INTEGER NOT NULL,
                real_point_id INTEGER NOT NULL,
                virtual_thing_id INTEGER NOT NULL
            )""")

            # DATA
            #TODO: Restriction of 255 chars is arbitrary. Need a BLOB really.
            # Automatically has a 'rowid' column which is the unique data_transaction_id
            #NOTE: Eventually will use an integer for type
            #for the moment, a VARCHAR is used for easy debug
            self._sql(
            """CREATE TABLE queue (
                type VARCHAR(4) NOT NULL,
                from_thing_id INTEGER,
                from_point_id INTEGER,
                to_thing_id INTEGER,
                to_point_id INTEGER,
                data VARCHAR(255)
            )""")

    @staticmethod
    def _split_addr(addr): #DBSpace._split_addr
        """Split a tuple into thing_id, point_id"""
        if addr is None:
            return None, None # thing_id, point_id
        if type(addr) == tuple:
            return addr[0], addr[1] # thing_id, point_id
        return addr, None # thing_id, point_id

    @staticmethod
    def _join_addr(thing_id, point_id): #DBSpace._join_addr
        """Join thing_id, point_id into a tuple"""
        return (thing_id, point_id)

    def is_thing_addr(self, addr): #DBSpace.is_thing_addr
        """Is this a thing address??"""
        if addr is None:
            return False
        if addr[1] is None:
            return True
        return False

    def identify(self, identity): #DBSpace.identify
        pass # nothing to do

    def authenticate(self, credentials): #DBSpace.authenticate
        pass # nothing to do

    def connect(self): # DBSpace.connect
        if not os.path.exists(DBSpace.DBNAME):
            info("Creating a new DBSpace")
            self.conn = sql.connect(DBSpace.DBNAME)
            self.create_tables()
        else:
            self.conn = sql.connect(DBSpace.DBNAME)

        if self.prop_agent_id is None:
            self.prop_agent_id = self._get_new_agent_id()
            info("using disposable agent_id:%s" % str(self.prop_agent_id))
        else:
            info("reusing agent_id:%s" % str(self.prop_agent_id))
            # it had better exist, or there will be a mess later!
            rows, headings = self._sql("SELECT 1 FROM agent WHERE agent_id=?", self.prop_agent_id)
            if len(rows) != 1:
                warning("agent_id %s does not exist yet, confirming if it is the next to be allocated" % str(self.prop_agent_id))
                a = self._get_new_agent_id()
                if a != self.prop_agent_id:
                    return error("That agent_id is not known to the system")
                else:
                    info("using confirmed next agent_id: %s" % str(a))

        self.restore()

    def disconnect(self): #DBSpace.disconnect
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def restore(self): #DBSpace.restore
        print("restore")
        t_rows, t_headings = self._sql("SELECT rowid, name FROM thing WHERE agent_id=?", self.agent_id)
        for t_row in t_rows:
            thing_id, thing_name = t_row
            thing_name = str(thing_name) # watch out for unicode
            print("  restore thing:%s %s" % (str(thing_id), str(thing_name)))
            t = self._upper_create_thing(thing_name)

            # get all producing points owned by this thing
            p_rows, p_headings = self._sql("SELECT rowid, name, type FROM point WHERE thing_id=?", thing_id)
            for p_row in p_rows:
                point_id, point_name, type_char = p_row
                point_name = str(point_name) # watch out for unicode
                print("    restore point:%s %s %s" % (str(point_id), str(point_name), str(type_char)))
                if type_char == 'T': # Transmit
                    t.create_feed(point_name)
                elif type_char == 'R': # Receive
                    t.create_control(point_name)
                else:
                    return error("Unknown point type in DB:%s/%s=%s" % (str(thing_name), str(point_name), str(type_char)))

            # process all bindings for Thing(t)
            print("    restore bindings for %s" % str(thing_id))
            b_rows, b_headings = self._sql(
                """SELECT b.virtual_thing_id, b.real_thing_id, b.real_point_id, p.type,
                          t.name, p.name
                   FROM binding AS b
                   LEFT JOIN point AS p ON (b.real_thing_id=p.thing_id AND b.real_point_id=p.rowid)
                   LEFT JOIN thing AS t ON (b.real_thing_id=t.rowid)
                   WHERE b.virtual_thing_id=?""", thing_id)

            for b_row in b_rows:
                b_virtual_thing_id, b_real_thing_id, b_real_point_id, type_char, thing_name, point_name = b_row

                if type_char == 'T': # A transmitter, i.e. a feed producer
                    point_addr = self._join_addr(b_real_thing_id, b_real_point_id)
                    p = self._upper_rebind_point(parent_thing=t, name="refollow(%s/%s)" % (str(thing_name), str(point_name)),
                                                 point_addr = point_addr)
                    print("      refollow:%s" % p.__repr__())

                elif type_char == 'R': # A receiver, i.e. a control consumer
                    point_addr = self._join_addr(b_real_thing_id, b_real_point_id)
                    p = self._upper_rebind_point(parent_thing=t, name="reattach(%s/%s)" % (str(thing_name), str(point_name)),
                                                 point_addr = point_addr)
                    trace("      reattach:%s" % p.__repr__())

                else:
                    print("unknown type_char in binding: (%s,%s) [%s] (%s,None)" %
                          (str(b_real_thing_id), str(b_real_point_id), str(type_char), str(b_virtual_thing_id)))


    def tick(self, limit=None): # DBSpace.tick
        ##trace("ticking meta")
        self._tick(Space.META, limit=limit)
        ##trace("ticking data")
        self._tick(Space.DATA, limit=limit)

    def get_thing_addr(self, thing_name): # DBSpace.get_thing_addr
        """Turn a thing_name into a thing_addr"""
        rows, headings = self._sql("SELECT rowid FROM thing WHERE name=?", thing_name)
        if len(rows) == 0:
            return error("There is no Thing called '%s'" % thing_name)
        rowid = rows[0][0]
        return rowid

    def create_thing(self, thing_name): #DBSpace.create_thing
        rows, headings = self._sql("SELECT rowid, agent_id FROM thing WHERE name=?", thing_name)
        if len(rows) == 0:
            # No thing_id, so must create it
            self._sql("INSERT INTO thing (agent_id, name) VALUES(?, ?)", self.agent_id, thing_name)
            rows, headings = self._sql("SELECT rowid FROM thing WHERE name=?", thing_name)
        else:
            # check that it's not assigned to some other agentid
            agent_id = rows[0][1]
            if agent_id != self.agent_id:
                return error("Thing %s is already allocated to a different agent_id:%s" % (str(thing_name), str(agent_id)))
        rowid = rows[0][0]
        return rowid #thing_id

    def create_point(self, thing_id, point_name, point_type='X'): #DBSpace.create_point
        rows, headings = self._sql("SELECT rowid FROM point WHERE thing_id=? AND name=?", thing_id, point_name)
        if len(rows) == 0:
            # Does not exist, so create it
            self._sql("INSERT INTO point (thing_id, type, name) VALUES(?,?,?)", thing_id, point_type, point_name)
            rows, headings = self._sql("SELECT rowid FROM point WHERE thing_id=? AND name=?", thing_id, point_name)
        rowid = rows[0][0]
        return (thing_id, rowid) # (thing_id, point_id)

    def create_feed(self, thing_id, feed_name): #DBSpace.create_feed
        # 'T' means Transmitter
        return self.create_point(thing_id, feed_name, point_type='T') # (thing_id, point_id)

    def create_control(self, thing_id, control_name): #DBSpace.create_control
        # 'R' means Receiver
        return self.create_point(thing_id, control_name, point_type='R') # (thing_id, point_id)

    def _set_visibility(self, thing_id, flag): #DBSpace._set_visibility
        # Query will fail if thing_id does not exist, that's as expected
        if flag:
            flag = "TRUE"
        else:
            flag = "FALSE"

        self._sql("UPDATE thing SET visible=? WHERE rowid=?", flag, thing_id)

    def show_thing(self, thing_id): #DBSpace.show_thing
        # Query will fail if thing_id does not exist, that's as expected
        self._set_visibility(thing_id, True)

    def hide_thing(self, thing_id): #DBSpace.hide_thing
        # Query will fail if thing_id does not exist, that's as expected
        self._set_visibility(thing_id, False)

    def _set_advertisement(self, thing_id, point_id, flag): #DBSpace._set_advertisement
        # Query will fail if thing_id does not exist, that's as expected
        if flag:
            flag = "TRUE"
        else:
            flag = "FALSE"
        self._sql("UPDATE point SET visible=? WHERE thing_id=? AND rowid=?", flag, thing_id, point_id)

    def advertise_feed(self, point_addr): #DBSpace.advertise_feed
        thing_id, feed_id = self._split_addr(point_addr)
        self._set_advertisement(thing_id, feed_id, True)

    def unadvertise_feed(self, point_addr): #DBSpace.unadvertise_feed
        thing_id, feed_id = self._split_addr(point_addr)
        self._set_advertisement(thing_id, feed_id, False)

    def offer_control(self, point_addr): #DBSpace.offer_control
        thing_id, control_id = self._split_addr(point_addr)
        self._set_advertisement(thing_id, control_id, True)

    def unoffer_control(self, point_addr): #DBSpace.unoffer_control
        thing_id, control_id = self._split_addr(point_addr)
        self._set_advertisement(thing_id, control_id, False)

    def find(self, thing_id, point_id=None): #DBSpace.find
        # thing_id can be a unique id, or a str(name)
        # point_id can be a unique id for thing id, or a str(name) unique to Thing
        if type(thing_id) == str:
            rows, headings = self._sql("SELECT rowid FROM thing WHERE name=?", thing_id)
            if len(rows) == 0:
                return error("Thing not found:%s" % str(thing_id))
            thing_id = rows[0][0]

        if point_id is None: # just a Thing required
            return self._join_addr(thing_id, point_id)

        if type(point_id) == str:
            rows, headings= self._sql("SELECT rowid FROM point WHERE thing_id=? and name=?", thing_id, point_id)
            if len(rows) == 0:
                return error("Point not found:%s/%s" % (str(thing_id), str(point_id)))
            point_id = rows[0][0]
            return self._join_addr(thing_id, point_id)

        # type(point_id) presumably==int
        rows, headings = self._sql("SELECT thing_id, rowid FROM point WHERE thing_id=? and rowid=?", thing_id, point_id)
        if len(rows) == 0:
            return error("Point not found:%s/%s" % (str(thing_id), str(point_id)))
        return self._join_addr(thing_id, point_id)

    def bind_point(self, from_addr, to_addr): #DBSpace.bind_point
        ##trace("BIND POINT from sender:%s to: receiver%s" % (str(from_addr), str(to_addr)))
        #TODO:if the binding is already in the table, reject it
        ##warning("#### TODO check for already bound in DBSpace table")
        #The receiving end of the message could check this
        #although if the receiving end is not running at the moment,
        #should we still update the database for next script start db poll?
        sending_thing_id, sending_point_id = self._split_addr(from_addr)
        receiving_thing_id, receiving_point_id = self._split_addr(to_addr)

        ##trace("bind: sending_thing_id:%s"   % sending_thing_id.__repr__())
        ##trace("bind: sending_point_id:%s"   % sending_point_id.__repr__())
        ##trace("bind: receiving_thing_id:%s" % receiving_thing_id.__repr__())
        ##trace("bind: receiving_point_id:%s" % receiving_point_id.__repr__())

        self._notify(sending_thing_id, sending_point_id, receiving_thing_id, receiving_point_id, self.NOTIFY_BIND)
        return to_addr

    def unbind_point(self, from_addr, to_addr): #DBSpace.unbind_point
        #TODO: if the binding is not in the table, reject it
        ##warning("#### TODO check for already unbound in DBSpace table")
        #The receiving end of the message could check this
        #although if the receiving end is not running at the moment,
        #should we still update the database for next script start db poll?
        from_thing_id, from_point_id = self._split_addr(from_addr)
        to_thing_id, to_point_id = self._split_addr(to_addr)
        self._notify(from_thing_id, from_point_id, to_thing_id, to_point_id, self.NOTIFY_UNBIND)

    def bind_ok(self, from_addr, to_addr): #DBSpace.bind_ok
        sending_thing_id, sending_point_id       = self._split_addr(from_addr)
        receiving_thing_id, receiving_point_id   = self._split_addr(to_addr)
        self._notify(sending_thing_id, sending_point_id, receiving_thing_id, receiving_point_id, Space.NOTIFY_BOUND)

    def bind_failed(self, from_addr, to_addr): #DBSpace.bind_failed
        sending_thing_id, sending_point_id       = self._split_addr(from_addr)
        receiving_thing_id, receiving_point_id   = self._split_addr(to_addr)
        self._notify(sending_thing_id, sending_point_id, receiving_thing_id, receiving_point_id, Space.NOTIFY_BIND_FAILED)

    def unbind_ok(self, from_addr, to_addr): #DBSpace.unbind_ok
        sending_thing_id, sending_point_id       = self._split_addr(from_addr)
        receiving_thing_id, receiving_point_id   = self._split_addr(to_addr)
        self._notify(sending_thing_id, sending_point_id, receiving_thing_id, receiving_point_id, Space.NOTIFY_UNBOUND)

    def unbind_failed(self, from_addr, to_addr): #DBSpace.unbind_failed
        sending_thing_id, sending_point_id       = self._split_addr(from_addr)
        receiving_thing_id, receiving_point_id   = self._split_addr(to_addr)
        self._notify(sending_thing_id, sending_point_id, receiving_thing_id, receiving_point_id, Space.NOTIFY_UNBIND_FAILED)

    def count_bindings_for(self, point_addr): #DBSpace.count_bindings_for
        thing_id, point_id = self._split_addr(point_addr)
        rows, headings = self._sql(
            """SELECT COUNT(*)
               FROM binding
               WHERE real_thing_id=? and real_point_id=?""",
               thing_id, point_id)
        c = rows[0][0]
        return c

    ##def search_point(self):
    ##def delete_point()
    ##def delete_thing()

    #----- DATA TRANSFER INTERFACE

    def send_to(self, from_thing_id, to_point_addr, data, confirmed=False): #DBSpace.send_to
        other_thing_id, other_point_id = self._split_addr(to_point_addr)
        #NOTE: This is used when sending to a control consumer (1:1 or many:1)
        self._send(from_thing_id, None, other_thing_id, other_point_id, data)

    def send_from(self, point_addr, data): #DBSpace.send_from
        #NOTE: This is used when sending from a feed to any followers (1:many)
        thing_id, point_id = self._split_addr(point_addr)

        # See if there is at least one binding that requires a feed update
        # We only need to know zero/nonzero, so this query ensures that if
        # there were a million followers, we would not get a large
        # data set back.
        rows, headings = self._sql(
            """SELECT 1
               FROM binding
               WHERE real_thing_id=? AND real_point_id=? LIMIT 1""",
            thing_id, point_id
        )
        if len(rows) == 0:
            ##trace("No bindings for %d/%d" % (thing_id, point_id))
            return # nothing to do

        # Send it once, with just a from_addr but no to_addr
        self._send(thing_id, point_id, None, None, data)

    def _send(self, from_thing_id, from_point_id, to_thing_id, to_point_id, data): #DBSpace._send
        #helper function for sending data from other methods
        self._sql("INSERT INTO queue (type, from_thing_id, from_point_id, to_thing_id, to_point_id, data) VALUES ('DATA',?,?,?,?,?)",
                  from_thing_id, from_point_id, to_thing_id, to_point_id, data)

    def _tick(self, type, limit=None): # DBSpace._tick
        ## pump through some rows of the appropriate table
        count = 0
        while True:
            # Throttle to a max number of uses
            if count == limit: break

            # Get next record, if any
            res = self._receive_next(type)
            if res is None: break # Nothing left to do
            ##trace("DBSpace._tick got:%s" % str(res))

            # Process next record
            rowid, from_thing_id, from_point_id, to_thing_id, to_point_id, data = res
            from_addr = (from_thing_id, from_point_id)
            to_addr   = (to_thing_id, to_point_id)
            #def process(self, type, data, from_addr=None, to_addr=None): # Space.process
            uses = self.process(type, data, from_addr, to_addr)
            #trace('----')
            #trace("There were %s uses of rowid:%s" % (str(uses), str(rowid)))
            #trace(res)
            #if uses == 0:
            #    trce(str(self.listeners))
            #trace('----')

            # Must advance rowid regarless of if used,
            # otherwise we will never step over this horizon
            self._used_rowid(type, rowid)
            count += 1

    def _receive_next(self, type): # DBSpace.receive_next
        """Read next item at appropriate horizon in queue table"""
        # get rowid horizons
        meta_row_id, data_row_id = self._get_next_rowids()

        # check table type and get appropriate rowid horizon
        if type == Space.META:
            row_type = "META"
            next_rowid = meta_row_id

        elif type == Space.DATA:
            row_type = "DATA"
            next_rowid = data_row_id

        else:
            return error("Unknown table type:%s" % str(type))

        # get zero or one record from the appropriate queue, at this horizon
        rows, headings = self._sql(
            """SELECT rowid, from_thing_id, from_point_id, to_thing_id, to_point_id, data
               FROM queue
               WHERE type=? AND rowid >= ?
               ORDER BY ROWID ASC LIMIT 1""", row_type, next_rowid)

        if len(rows) == 0:
            return None # No data waiting

        #rowid, from_thing_id, from_point_id, to_thing_id, to_point_id, data = rows[0]
        return rows[0] # in above order as from SQL query
        # Note rowid has to be returned too, so we know which rowid to advance the
        # horizon to when the record has been processed. We don't advance it
        # until all processing has been done, so that crashes are recoverable.

    #----- LOW LEVEL META-INTERACTIONS
    def _notify(self, from_thing_id, from_point_id, to_thing_id, to_point_id, notification): #DBSpace._notify
        ##trace("DBSpace._notify from:(%s,%s) to:(%s,%s) notification:%s" %
        ##      (str(from_thing_id),str(from_point_id),str(to_thing_id),str(to_point_id),str(notification)))
        ##if notification == Space.NOTIFY_BOUND_TO_PRODUCER:
        ##    error("STOP HERE")
        #helper function for sending notifications from other methods
        self._sql("INSERT INTO queue (type, from_thing_id, from_point_id, to_thing_id, to_point_id, data) VALUES ('META',?,?,?,?,?)",
                  from_thing_id, from_point_id, to_thing_id, to_point_id, notification)

    def _meta_in_point(self, from_addr, to_addr, data): #DBSpace._meta_in_point
        ##trace("meta_in_point:%s %s" % (str(to_addr), str(msg)))
        from_thing_id, from_point_id = self._split_addr(from_addr)
        to_thing_id, to_point_id = self._split_addr(to_addr)

        if data == self.NOTIFY_BIND:
            if from_point_id is not None:
                ##trace(from_point_id)
                ##trace(type(from_point_id))
                return error("Unexpected not-none point_id %s/%s" % (str(from_thing_id), str(from_point_id)))
            return self._remote_bind(to_thing_id, to_point_id, from_thing_id)

        elif data == self.NOTIFY_UNBIND:
            if from_point_id is not None:
                return error("Unexpected not-none point_id %s/%s" % (str(from_thing_id), str(from_point_id)))
            return self._remote_unbind(to_thing_id, to_point_id, from_thing_id)

    def _remote_bind(self, to_thing_id, to_point_id, from_thing_id): #DBSpace._remote_bind
        ##trace("remote_bind: to:%s/%s from:%s" % (str(to_thing_id), str(to_point_id), str(from_thing_id)))
        ##bindings = self.things[to_thing_id].points[to_point_id].bindings
        ##bindings[from_thing_id] = 1 # now bound

        #If this binding already exists, we should not insert it again
        #otherwise the same data will be delivered multiple times to the same destination

        rows, headings = self._sql(
            """SELECT COUNT(*)
               FROM binding
               WHERE real_thing_id=? and real_point_id=? and virtual_thing_id=?""",
                                   to_thing_id, to_point_id, from_thing_id)
        c = rows[0][0]
        if c != 0:
            return warning("Duplicate binding - ignored") # Not done

        self._sql(
            """INSERT INTO binding (real_thing_id, real_point_id, virtual_thing_id)
               VALUES(?,?,?)""", to_thing_id, to_point_id, from_thing_id)
        return True # DONE

    def _remote_unbind(self, to_thing_id, to_point_id, from_thing_id): #DBSpace._remote_unbind
        ##trace("remote_unbind: to:%s/%s from:%s" % (str(to_thing_id), str(to_point_id), str(from_thing_id)))
        #to_thing_id, to_point_id is the service provider
        #from_thing_id is the bind requester

        ##bindings = self.things[to_thing_id].points[to_point_id].bindings
        ##bindings[from_thing_id] = 1 # now bound

        self._sql(
            """DELETE FROM binding
               WHERE real_thing_id=? AND real_point_id=? AND virtual_thing_id=?""",
                                   to_thing_id, to_point_id, from_thing_id)
        return True # Done


if 'rmdb' in CONFIG:
    DBSpace.ask_delete_db(DBSpace.DBNAME)
elif 'rmdby' in CONFIG:
    print("deleting database:%s" % DBSpace.DBNAME)
    DBSpace.ask_delete_db(DBSpace.DBNAME, True)


#===== SPACE SELECTION ========================================================

def get_MemorySpaceClass():
    # Don't use error() here as it will print loads of stuff
    raise RuntimeError("MemorySpace still needs fixing")
    ##c = MemorySpace
    ##return c # class factory method

def get_DBSpaceClass():
    import sqlite3
    c = DBSpace
    return c # class factory method

def get_IoticSpaceClass():
    import iotic
    c = iotic.create_IoticSpace # The Class factory-method

    # but to resolve the import cyclic dependency, it takes Space as a first parameter
    def call_Iotic(*args, **kwargs):
        # 'c' is a closure variable, which is actually a class factory method
        return c(Space, *args, **kwargs)
    return call_Iotic

# Available spaces we could try
spaces = {
    "iotic":  get_IoticSpaceClass,
    "DB":     get_DBSpaceClass,
    "memory": get_MemorySpaceClass
}

# Priority order for auto-find, most featured first
space_order = ["iotic", "DB", "memory"]

ConfiguredSpaceClass = None

# See if a specific space is being requested
if ("space" in CONFIG) and (CONFIG.space in spaces):
    #info("trying: %s" % CONFIG.space)
    # This call returns a Class factory method
    ConfiguredSpaceClass = spaces[CONFIG.space]()

else:
    # Not specified, so hunt in priority order for an available space
    for space in space_order:
        try:
            #info("trying space:%s" % space)
            ConfiguredSpaceClass = spaces[space]()
            info("using: %s" % space)
            break # got it
        except:
            warning("can't find space: %s" % space)

if ConfiguredSpaceClass is None:
    error("Failed to find a space that we can use")

# Now actually create the space instance

if 'agent_id' in CONFIG:
    # Use a specific agent identifier
    default_space = ConfiguredSpaceClass(agent_id=CONFIG.agent_id) ##2HERE## create
else:
    # allocate the next free agent identifer, might be disposable
    default_space = ConfiguredSpaceClass() ##2HERE## create



#===== HANDLERS ===============================================================

def DEFAULT(*args): # handler METHOD
    """default handler where no user handler provided"""
    info("default:%s" % str(args))
    return True # Default is to say I handled it

def IGNORE(*args): # handler METHOD
    """destination handler for disabling handlers, e.g. realvar.handler(iot.ignore)"""
    # Do nothing (ignore the data)
    return True # Default is t say I handled it

def create_handler(on_object, purpose):
    """Completely wires up a handler on on_object:
        default_handler METHOD for {purpose}
        self.{purpose}_handler = default_handler_{purpose}
        self.when_{purpose}(m) DECORATOR
        self.PURPOSE() redirector METHOD
    """

    #Use like this:
    #create_handler(self, "feed_created")

    # This is the actual handler that will be called by default,
    # if the user does not override it
    def default_handler(*args):
        #'purpose' is a closure variable
        print("default_%s:%s" % (str(purpose), str(args)))
    default_handler.__name__ = "default_%s" % purpose

    if on_object is not None:
        # useful name templates, so the below code makes some sense
        when_PURPOSE    = "when_%s" % purpose
        PURPOSE_handler = "%s_handler" % purpose
        PURPOSE         = purpose

        # self.{purpose}_handler = default_purpose_handler
        setattr(on_object, PURPOSE_handler, default_handler) # DEFAULT handler assignment

        # self.when_{purpose}(m): # DECORATOR
        #     self.{purpose}_handler = m
        #     return m
        def when_handler(m): # DECORATOR
            # generic form of self.{purpose}_handler = m
            setattr(on_object, PURPOSE_handler, m)
            return m
        when_handler.__name__ == when_PURPOSE
        setattr(on_object, when_PURPOSE, when_handler) # DECORATOR

        # self.{purpose}(self, *args, **kwargs): # redirector
        #     return self.{purpose}_handler(*args, **kwargs)
        def handler_redirect(*args, **kwargs):
            # must always redirect to the value inside self.{purpose}
            h = getattr(on_object, PURPOSE_handler)
            return h(*args, **kwargs)
        handler_redirect.__name__ = PURPOSE
        ##trace("try setattr(%s, %s, %s)" % (str(on_object.__repr__()), str(PURPOSE), str(handler_redirect)))
        setattr(on_object, PURPOSE, handler_redirect) # helper redirector METHOD

    return default_handler

def assert_is_Point(p):
    if p is None:
        return error("Point parameter is empty")
    if not isinstance(p, Point):
        print("wanted Point: got: %s %s" % (str(type(p)), p.__repr__()))
        return error("parameter is not a Point")


#----- ThingRef ---------------------------------------------------------------

class ThingRef(object): # ThingRef()
    def __init__(self, name, space, thing_id): #ThingRef.__init__
        self.name     = name
        self.space    = space
        self.thing_id = thing_id

    def __repr__(self): #ThingRef.__repr__
        return "ThingRef(%s %s)" % (str(self.name), str(self.thing_id))

    @auto_start
    def bind(self, point_ref): #ThingRef.bind
        ##trace("ThingRef.bind")

        if not hasattr(point_ref, "point_addr"):
            return error("point doesn't have a point_addr, so it can't be bindable")

        #This will kick off a BIND to the other end,
        #and either a BOUND or NOTBOUND coming back to the real Thing,
        # or a TIMEOUT locally
        self.space.bind_point(self.thing_id, point_ref.point_addr)

        ##TODO: Process timeout
        #This requires a feature in space that allows us to poll to see
        #if the binding we have requested has taken place or not,
        #and we'll have to poll it or later on look for a callback
        #saying it has succeeded or failed

        ##timer = Timer(2) # 2 second timeout
        ##while not timer.check() and self.state == Point.STATE_REF:
        ##    ##trace("waiting for BIND to succeed")
        ##    Thing.tick_all()

        ##if self.state == Point.STATE_REF:
        ##    # must be timeout
        ##    return error("Timeout while waiting for BIND to occur")

        ##if self.state == Point.STATE_BIND_FAILED:
        ##    self._become_ref()
        ##    return error("BIND was rejected by other end")

        ##return self

    def unbind(self, point_ref): #ThingRef.unbind
        ##trace("ThingRef.unbind")

        if not hasattr(point_ref, "point_addr"):
            return error("point doesn't have a point_addr, so it can't be bindable")

        #This will kick off a BIND to the other end,
        #and either a BOUND or NOTBOUND coming back to the real Thing,
        # or a TIMEOUT locally
        self.space.unbind_point(self.thing_id, point_ref.point_addr)

        ##TODO: Process timeout
        #This requires a feature in space that allows us to poll to see
        #if the binding we have requested has taken place or not,
        #and we'll have to poll it or later on look for a callback
        #saying it has succeeded or failed

        ##timer = Timer(2) # 2 second timeout
        ##while not timer.check() and self.state == Point.STATE_REF:
        ##    ##trace("waiting for BIND to succeed")
        ##    Thing.tick_all()

        ##if self.state == Point.STATE_REF:
        ##    # must be timeout
        ##    return error("Timeout while waiting for BIND to occur")

        ##if self.state == Point.STATE_BIND_FAILED:
        ##    self._become_ref()
        ##    return error("BIND was rejected by other end")

        return self

    def attach(self, point_ref): #ThingRef.attach
        return self.bind(point_ref)

    def detach(self, point_ref): #ThingRef.detach
        return self.unbind(point_ref)

    def follow(self, point_ref): #ThingRef.follow
        return self.bind(point_ref)

    def unfollow(self, point_ref): #ThingRef.unfollow
        return self.unbind(point_ref)


#----- THING ------------------------------------------------------------------

class Thing(object): # Thing()
    things = {}
    default_thing = None

    def __init__(self, name, space, thing_id): #Thing.__init__
        if name in Thing.things:
            return error("thing already exists:%s" % str(name))

        self.name         = name
        self.space        = space
        self.thing_id     = thing_id # this is really thing_addr

        self.feeds        = {} # LOCAL feeds that we own, keyed by name
        self.controls     = {} # LOCAL controls that we own, keyed by name

        self.your_points  = [] # LOCAL proxies for REMOTE points that others own, no name
        self.default_feed = None
        self.default_control = None
        self._create_default_handlers()

        # These are for unsolicited actions that happen in webui or other interfaces
        # if our Thing is attached to some other control(s) this point handles it
        self.unassigned_attacher = PointList("unassigned_attacher")
        def attached(point):
            ##trace("HAVE ATTACHED")
            self.unassigned_attacher.instances.append(point)
            ##trace(self.unassigned_attacher.instances)
        self.unassigned_attacher.have_attached = attached

        def detached(point):
            ##trace("HAVE DETACHED")
            self.unassigned_attacher.instances.remove(point)
            ##trace(self.unassigned_attacher.instances)
        self.unassigned_attacher.have_detached = detached

        # if our Thing is made to follow some other feed, this point handles it
        ##self.unassigned_follower = PointList("unassigned_follower")

        if len(Thing.things) == 0:
            Thing.default_thing = self
        Thing.things[name] = self

    def __repr__(self): #Thing.__repr__
        return "Thing(%s %s)" % (str(self.name), str(self.thing_id))

    def dump(self, printer=None): #Thing.dump
        def default_printer(msg):
            print(msg)
        if printer is None:
            printer = default_printer

        printer("Thing:%s %s" % (str(self.name), str(self.thing_id)))

        printer("  MY FEEDS (Feeds I own)")
        for f in self.feeds:
            printer("    %s: %s" % (f, self.feeds[f].__repr__()))

        printer("  MY CONTROLS (Controls I own)")
        for c in self.controls:
            printer("    %s: %s" % (c, self.controls[c].__repr__()))


        printer("  YOUR POINTS (Others Points that I connect to)")
        for p in self.your_points:
            printer("    %s" % p.__repr__())

        printer("  unassigned_attacher (Unsolicited attaches to others controls)")
        if len(self.unassigned_attacher.instances) != 0:
            for i in self.unassigned_attacher.instances:
                printer("    %s" % i.__repr__())

        #points_in are virtual and stored in the database layer
        #as storing them here would not scale to 1 million followers

    def get_thing_addr(self, thing_name): #Thing.get_thing_addr
        return self.space.get_thing_addr(thing_name)

    #----- DEFAULT HANDLERS ---------------------------------------------------

    #an attached is a BIND to a CONSUMER(REAL) but at the PRODUCER(VIRTUAL) end
    def default_have_attached_handler(self, point):
        ##trace("Thing.default_have_attached_handler: %s" % point.__repr__())
        return self.unassigned_attacher.have_attached(point)

    #a detach is an UNBIND fro a CONSUMER(REAL) but at the PRODUCER(VIRTUAL) end
    def default_have_detached_handler(self, point):
        ##trace("Thing.default_have_attached_handler: %s" % point.__repr__())
        return self.unassigned_attacher.have_detached(point)

    ###TODO: still need to decide which end this is
    ##def default_have_followed_handler(self, point):
    ##    pass
    ##
    ##def default_have_unfollowed_handler(self, point):
    ##    pass

    def _create_default_handlers(self): #Thing._create_default_handlers

        handlers = [
            "created", "deleted",
            "have_attached", "have_detached",
            "lost"
        ]
        for h in handlers:
            create_handler(self, h)

        # aliases
        #self.when_feed_created    = self.when_created
        #self.when_feed_deleted    = self.when_deleted
        #self.when_have_followed   = self.when_have_bound
        #self.when_have_unfollowed = self.when_have_unbound
        #self.when_lost_feed       = self.when_lost

        #self.when_have_attached   = self.when_have_bound
        #self.when_have_detached   = self.when_have_unbound
        #self.when_lost_control    = self.when_lost
        #self.when_control_created = self.when_created
        #self.when_control_deleted = self.when_deleted

        # specific handler defaults
        self.have_attached_handler  = self.default_have_attached_handler
        self.have_detached_handler  = self.default_have_detached_handler

    #----- FACTORY METHODS ----------------------------------------------------

    @staticmethod
    def find_thing(thing_name, space=None): #Thing.find_thing
        if space is None:
            space = default_space ##2HERE## deprecate default_space

        thing_id = space.find(thing_name)
        #space.find will raise error if not found
        return ThingRef(thing_name, space, thing_id)

    @staticmethod
    def create_thing(name, parent, space=None): #Thing.create_thing
        if space is None:
            space = default_space ##2HERE## deprecate default_space
        if name in Thing.things:
            # already exists, just return it
            return Thing.things[name]

        thing_id = space.create_thing(name)
        t = Thing(name, space, thing_id)
        t.parent = parent
        return t

    def create_feed(self, name): #Thing.create_feed
        # If you are creating a Feed, it must be the LOCAL PRODUCER
        if name in self.feeds:
            # already exists
            return self.feeds[name]

        point_addr = self.space.create_feed(self.thing_id, name)
        p = Point(parent_thing=self, name=name)
        ##p._become_feed(self.space, point_addr)
        p._become_real(self.space, point_addr)
        if len(self.feeds) == 0: # The first feed created for this thing is default
            self.default_feed = p
        self.feeds[name] = p
        return p

    def create_control(self, name): #Thing.create_control
        if name in self.controls:
            # already exists
            return self.controls[name]
        # If you are creating a Control, it must be the LOCAL CONSUMER
        point_addr = self.space.create_control(self.thing_id, name)
        p = Point(parent_thing=self, name=name)
        ##p._become_control(self.space, point_addr)
        p._become_real(self.space, point_addr)
        if len(self.controls) == 0: # The first control created for this thing is default
            self.default_control = p
        self.controls[name] = p
        return p

    #--------------------------------------------------------------------------

    @auto_start
    def find(self, *args): #Thing.find
        """Do a find, in a way that if you just .bind() on the result,
           this Thing will be the local owning Thing"""
        #  USAGE                                         LOCAL_THING       REMOTE_THING        REMOTE_POINT
        #  iot.find("wanted_point")                      'thing'           'thing'             addr("wanted_point")
        #  iot.find("thing", "wanted_point")             'thing'           addr("thing")       addr("wanted_point")
        #  (NO)iot.find(your_thing, "wanted_point")      'thing'           your_thing          addr("wanted_point")
        #
        #  my_thing.find("wanted_point")                 my_thing          'thing'             addr("wanted_point")
        #  my_thing.find("thing", "wanted_point")        my_thing          addr("thing")       addr("wanted_point")
        #  (NO)my_thing.find(your_thing, "wanted_point") my_thing          your_thing          addr("wanted_point")

        ##trace("Thing.find: %s/%s" % (str(thing_ref), str(point_ref)))

        # find(point_ref)
        # find(thing_ref, point_ref)

        if len(args) == 0:
            return error("What do you want to find?")

        elif len(args) == 1: # a point_ref on my thing
            thing_ref = self.thing_id
            point_ref = args[0]

        elif len(args) == 2: # A thing_ref, point_ref
            thing_ref, point_ref = args[0:2]

        else:
            return error("Can't understand find request:%s" % str(args))

        # Do a space.find() to turn the spec into an address
        point_addr = self.space.find(thing_ref, point_ref) # (thing_id, point_id)
        ##trace("Thing.find: found addr:%s" % str(addr))
        ### Throws exception if cannot find - perhaps return None and interpret here?

        # Wrap the address with a Point(REF))
        name = "found(%s/%s)" % (str(thing_ref), str(point_ref))
        p = Point(parent_thing=self, name=name) # makes EMPTY
        p._become_ref(self.space, point_addr)
        return p # An unbound Point object that refers to what we just found

    def send(self, data, confirmed=False): #Thing.send
        self.unassigned_attacher.send(data, confirmed)

    def ask(self, data): #Thing.ask
        self.send(data)

    def tell(self, data): #Thing.tell
        self.send(data, confirmed=True)

    ##TODO: eventually, when_updated needs to be when data comes in from feeds
    #from unassigned_follower

    ##def show(self): #Thing.show
    ##def hide(self): #Thing.hide
    ##def follow(self, lhs_point, rhs_thing) #Thing.follow
    ##def detach(self, local_point): #Thing.detach
    ##def unfollow(self, local_point): #Thing.unfollow
    ##def delete_point(self, local_point): #Thing.delete_point
    ##def delete(self): #Thing.delete
    ##def remove(point)  (remote detach)
    ##def block(point)   (blacklist) # auto when_follow/when_attach handling
    ##def unblock(point) (whitelist) # remove auto when_follow/when_attach handling

    #----- CONCURRENCY --------------------------------------------------------

    @staticmethod
    def tick_all(): #Thing.tick_all
        # Tick any regular actions on Points that have 'rate' defined.
        # They also use time horizons, so they only need CPU time
        # to work out the rest.
        # Must always tick everything, to give it a chance to receive
        # meta_in and data_in, as well as doing any local repeating behaviour.
        for thing_name in Thing.things:
            t = Thing.things[thing_name]
            t.tick()

    def tick(self): #Thing.tick
        # Must process all to(thing) meta messages first,
        # otherwise point ticker below will incorrectly remove from the queue

        # This is still needed for any Point repeating behaviour, so don't remove it.

        for fname in self.feeds: # LOCAL producing feeds that we own
            f = self.feeds[fname]
            f.tick()

        for cname in self.controls: # LOCAL consuming controls, that we own
            c = self.controls[cname]
            c.tick()

        for p in self.your_points: # LOCAL proxy for REMOTE feed or control, that we don't own
            p.tick()

        self.space.tick()

#----- Fanout and PointList ---------------------------------------------------

class Fanout(object):
    """A memoizing dynamic proxy, for a list of any instances"""
    def __init__(self): #Fanout.__init__
        self.instances = []

    def __repr__(self): #Fanout.__repr__
        return "Fanout(%s items)" % str(len(self.instances))

    def __iadd__(self, other): #Fanout.__iadd__
        self.instances.append(other)
        return self

    def __isub__(self, other): #Fanout.__isub__
        self.instances.remove(other)
        return self

    def __len__(self): #Fanout..__len__
        return len(self.instances)

    def __getattr__(self, name): #Fanout.__getattr__
        def fn(*args, **kwargs):
            for i in self.instances:
                fn = getattr(i, name)
                res = fn(*args, **kwargs)
                ##if res is not None:
                ##    trace("note: %s returns:%s" % (str(i.__name__), str(res)))
            return None #TODO: Review this

        fn.__name__ == "all_%s" % str(name)
        self.__setattr__(name, fn)
        ##trace("added proxy:%s" % str(fn.__name__))
        return fn


class PointList(Fanout): #PointList
    def __init__(self, name, items=None): #PointList.__init__
        self.name = name
        Fanout.__init__(self)
        if items is not None:
            for item in items:
                self += item

    def __repr__(self): #PointList.__repr__
        return "PointList(%s %s)" % (str(self.name), str(len(self)))


#----- Producer --------------------------------------------------------------
#This is a sort of 'plugin' to overlay on a Point to add new optional behaviour.
#It is more to do with SEND, but has to be here so Point can refer to it.

class Producer(object): #Producer()
    IMMEDIATE = "immediate"
    TIMED     = "timed"
    TRIGGERED = "triggered"

    def __init__(self): #Producer.__init__
        self.prop_rate = None
        self.next_tick = None
        self.prop_send_on_change = True # yes, it's on by default
        self.enabled = False #TODO: as a property rather than a method??

    @property
    def rate(self): #Producer.rate PROPERTY
        return self.prop_rate

    @rate.setter
    def rate(self, value): #Producer.rate PROPERTY
        self.prop_rate = value
        if value is not None:
            self.next_tick = time.time() + self.prop_rate
        else:
            self.next_tick = None

    @property #getter
    def send_on_change(self): #Producer.send_on_change PROPERTY
        return self.prop_send_on_change #TODO: use this style for all properties

    @send_on_change.setter
    def send_on_change(self, value): #Producer.send_on_change PROPERTY
        self.prop_send_on_change = value

    def set_mode(self, mode): #Producer.set_mode
        self.mode = mode

        if self.mode == self.IMMEDIATE:
            self.send_on_change = True
            self.rate = None

        elif self.mode == self.TIMED:
            if self.rate is None:
                self.rate = 1 # default 1 second timer
            self.send_on_change = False

        elif self.mode == self.TRIGGERED:
            self.rate = None
            self.send_on_change = False

        else:
            return error("Unknown mode:%s" % str(mode))

    def trigger(self): #Producer.trigger
        # Point is-a Producer
        ##trace("Producer.trigger:%s" % str(self.last_value))
        self.send_now(self.last_value)

    def tick(self): #Producer.tick
        if self.next_tick is not None and self.prop_rate is not None:
            now = time.time()
            ##trace("TICK now:%s next:%s" % (str(now), str(self.next_tick)))
            ##time.sleep(0.5)
            if now >= self.next_tick:
                ##trace("TIMED TRIGGER")
                self.next_tick = now + self.prop_rate
                self.trigger()

#----- Consumer ---------------------------------------------------------------
#
# Placeholder for future data consuming patterns

class Consumer(object):
    def __init__(self): #Consumer.__init__
        pass


#----- Point ------------------------------------------------------------------

#NOTE: The whole idea of this abstraction is that a point is a point
#always, regardless of if it is a reference, a local point, or a
#remote point, a Feed or a Control, or even an Empty point.
#It behaves like a Point (with sensible defaults) regardless of
#what it is actually connected to.
#There is a real symmetry to this, something we've been trying to
#find for ages. That way it is easy to plug and
#play Points into anything interchangeably with no surprises.
#It also makes automated testing much easier.

class Point(Producer, Consumer): #Point()
    #  Really it is a facade (AbstractPoint)
    """A wrapper for any kind of underlying (inner) point.
       will morph to different objects depending on use
       But provides standard application behaviour that applies to
       all points regardless of their type, binding and inner link"""

    STATE_EMPTY             = "EMPTY"       # initial state, no special behaviour
    STATE_REF               = "REF"         # an address in a space
    STATE_BOUND             = "BOUND"       # bound to a remote point that exists
    STATE_BIND_FAILED       = "BIND_FAILED" # timeout or NOTBOUND response to a BIND

    STATE_REAL              = "REAL"       # a real Point in the space (e.g. Feed or Control)

    PRODUCER                = "producer"
    CONSUMER                = "consumer"

    # A Point, unless specified, is an unbound Point with no inner behaviour
    def __init__(self, parent_thing, name): #Point.__init__
        Producer.__init__(self)
        Consumer.__init__(self)
        if name is not None and type(name) != str:
            return error("name must be str, got:%s" % str(type(name)))
        self.state        = Point.STATE_EMPTY
        self.parent_thing = parent_thing
        self.name         = name
        self.point_addr   = None

        self._create_default_handlers()
        self.last_value   = None
        self.was_updated  = False
        self.meta_registered = False
        self.data_registered = False

    def __str__(self): #Point.__str__
        # If this is a Point state that may have a meaningful value, return that value
        # otherwise return it's repr.
        # This is so that the default action when printing sender, attacher, follower
        # in app handlers, is to print useful address info.

        if self.state in [Point.STATE_EMPTY, Point.STATE_REF, Point.STATE_BIND_FAILED]:
            return self.__repr__()

        # It probably has a meaningful value, so return that value
        if self.last_value == None:
            return ""
        return str(self.last_value)

    def __repr__(self): #Point.__repr__
        return "Point(%s %s %s)" % (str(self.name), str(self.state), str(self.point_addr))

    def __call__(self, data, confirmed=False): #Point.__call__
        """Send data"""
        self.send(data, confirmed=confirmed)

    #----- STATE CHANGES ------------------------------------------------------

    def _become_ref(self, space=None, point_addr=None, register=True): #Point._become_ref
        # copy in space and point_addr if provided, leave unchanged if not provided
        if space is not None and point_addr is not None:
            self.space = space
            self.point_addr = point_addr

        if self.space is None or self.point_addr is None:
            return error ("Must provide a space and point_addr")
        self.state = Point.STATE_REF
        # As soon as a Point has an address, it needs to register for
        # receiving at least meta messages, if not data messages also
        # even REF's need meta messages, as they have to process BIND messages.
        if register:
            if not self in self.parent_thing.your_points:
                self.parent_thing.your_points.append(self)

            if not self.meta_registered:
                self.space.register_for(self, Space.META, from_addr=self.point_addr)
                self.meta_registered = True

            if self.data_registered:
                self.space.unregister_for(self, Space.DATA, from_addr=self.point_addr)
                self.data_registered = False

    def _become_bound(self, register=True): #Point._become_bound
        if self.space is None or self.point_addr is None:
            return error("Cannot change to BOUND without a space and a point_addr")
        self.state = Point.STATE_BOUND
        # As soon as a Point has an address, it needs to register for
        # receiving at least meta messages, if not data messages also
        if register:
            if not self in self.parent_thing.your_points:
                self.parent_thing.your_points.append(self)
            if not self.meta_registered:
                self.space.register_for(self, Space.META, from_addr=self.point_addr)
                self.meta_registered = True
            if not self.data_registered:
                #Note, strictly speaking, this is only for feed followers,
                #as a bound(control) does not receive data
                ##trace("_become_bound REGISTER DATA for %s" % str(self.point_addr))
                self.space.register_for(self, self.space.DATA, from_addr=self.point_addr)
                self.data_registered = True

    def _become_real(self, space, point_addr): #Point._become_real
        self.space      = space
        self.point_addr = point_addr
        self.state      = Point.STATE_REAL

        if not self.meta_registered:
            self.space.register_for(self, Space.META, to_addr=self.point_addr)
            self.meta_registered = True

        if not self.data_registered:
            self.space.register_for(self, self.space.DATA, to_addr=self.point_addr)
            self.data_registered = True

    #----- HANDLERS -----------------------------------------------------------

    def _create_default_handlers(self): #Point._create_default_handlers
        handlers = [
            "bound", "unbound",
            "have_bound", "have_unbound",
            "lost",
            "updated"
        ]
        for h in handlers:
            create_handler(self, h)

        # aliases for handler decorators
        self.when_new_follower    = self.when_bound
        self.when_new_attacher    = self.when_bound
        self.when_unfollowed      = self.when_unbound
        self.when_detached        = self.when_unbound
        self.when_have_followed   = self.when_have_bound
        self.when_have_attached   = self.when_have_bound
        self.when_have_unfollowed = self.when_have_unbound
        self.when_have_detached   = self.when_have_unbound
        self.when_lost_feed       = self.when_lost
        self.when_lost_control    = self.when_lost

    #----- PROPERTIES ---------------------------------------------------------

    @property #getter
    @auto_start
    def value(self): #Point.value PROPERTY
        """Get the last cached value, could be None"""
        ##trace("VALUE getter")
        #TODO: If this is a 'receiving point' (e.g. a feed follower, or offered control)
        #does this just poll last_value and return None, or does it wait() for the
        #next value to come in? Both schemes could be valid.
        return self.last_value

    @value.setter
    @auto_start
    def value(self, data): #Point.value PROPERTY
        """Set the cached value and trigger a send"""
        ##trace("Point.value:%s" % str(data))
        self.last_value = data
        self.send(data)

    # Not great if multiple threads consuming
    # but good enough, probably, for simple programs
    # It's a single flag, so if you get multiple messages in, you
    # might loose things (although it's based on a concept of main loop
    # polling the current value, which is probably fine without a count/queue)
    @property #getter
    @auto_start
    def is_updated(self): #Point.updated PROPERTY
        r = self.was_updated
        #trace("read was_updated:%s" % r)
        self.was_updated = False
        return r

    #--------------------------------------------------------------------------

    @auto_start
    def send(self, data=None, confirmed=False): #Point.send
        """Send a real data message, might be queued for later"""
        ##trace("point send:%s" % str(data))

        if data is not None and callable(data):
            changed = True
            self.last_value = data # remember the function
        else:
            changed = (data != self.last_value)
            self.last_value = data # always keep our cache up to date

        result = True
        # Try to send the data
        # Note, if send_now throws an Exception, that just propagates out, by design
        if self.prop_rate is None:
            result = self.send_now(data, confirmed=confirmed)

        elif self.send_on_change:
            if changed:
                result = self.send_now(data, confirmed=confirmed)
            else:
                if confirmed:
                    return error("send:can't use confirmed and deferred at same time")
        else:
            if confirmed:
                return error("send:can't use confirmed and deferred at same time")

        if confirmed:
            # Interpret the confirmation result (None, ACK, NACK)
            if result is None:
                # None means the app did nothing, default is ACK
                pass # just assume it worked
            elif type(result) == bool:
                if result == False:
                    return error("send:confirmed send was rejected by receiver")
            else: #unknown type
                ##trace("result:%s" % str(result))
                return error("send:don't know how to interpret result type:%s" % str(type(result)))

    def send_now(self, data=None, confirmed=False): #Point.send_now
        ##trace("Point.send_now:%s" % str(data))
        if callable(data):
            datav = data()
        else:
            datav = data

        if self.state == Point.STATE_BOUND:
            ##trace("BOUND send:%s" % str(datav))
            result = self.space.send_to(self.parent_thing.thing_id, self.point_addr, datav, confirmed) # PASS DOWN STACK
            ##trace("sent from:%s to:%s" % (str(self.parent_thing.thing_id), str(self.point_addr)))
            ##trace("EXIT")
            #sys.exit()
            return result

        elif self.state == Point.STATE_REAL:
            c = self.space.count_bindings_for(self.point_addr)
            ##trace("FeedProducer has %d bindings" % c)
            if c == 0:
                warning("LOOPBACK: Point(%s) has no followers:%s" % (str(self.name), str(data)))
                self.receive_data(self, datav) # local loopback  #3HERE: should pass sender Point, not receiver Point
            else:
                ##trace("Feed: Feed(%s):SHARE to %s followers" % (str(self), str(c)))
                # The space will fanout to all followers
                ##trace("send_from:%s %s" % (str(self.point_addr), str(data)))
                self.space.send_from(self.point_addr, datav)

        else: # everything else [EMPTY, REF, ##NO: CONTROL_CONSUMER##) #LOOPBACK
            warning("looping back to self")
            self.receive_data(self, datav) # LOOPBACK #3HERE: should pass sender Point, not receiver Point
            #TODO: No way to do return result of confirmed yet
            result = True #TODO: Fudge return result
            return result # confirmed True

    @auto_start
    def receive_data(self, sender, data=None, *args): #Point.receive_data
        """Dispatch data to any configured handler"""
        ##trace("Point.receive:%s" % str(data))

        # If sender is not a point, we must assume it is an address from the space
        # so let's convert it to a temporary Point object

        if not isinstance(sender, Point):
            #def __init__(self, parent_thing, name):
            sender_p = Point(parent_thing=self.parent_thing, name="tempaddr")
            #def _become_ref(self, space=None, point_addr=None, register=True): #Point._become_ref
            sender_p._become_ref(self.parent_thing.space, sender, register=False)
            sender = sender_p

        if self.updated_handler is not None:
            ##trace("point when updated")
            ##trace(self.__repr__())
            ##trace(self.updated_handler)
            result = self.updated_handler(sender, data) # point.when_updated

        elif self.parent_thing.updated_handler is not None:
            ##trace("Calling parent_thing.updated_handler")
            result = self.parent_thing.updated_handler(sender, data) # parent_thing.when_updated

        else:
            warning("Point: no handler defined")
            #If there is no handler, the message is just ignored
            result = None

        # To cover the case where we are a local loopback and a function
        # has been assigned to value, preserve the function
        if self.last_value is not None and callable(self.last_value):
            pass # preserve the last_value function
        else:
            # copy in the new value
            self.last_value = data
        ##trace("%s was updated" % self.__repr__())
        self.was_updated = True
        return result

    #-------- VERBS -----------------------------------------------------------

    # As this is an abstract Point that can morph into any type of Point,
    # it must somehow implement all the verb methods of all point types

    @auto_start
    def bind(self): #Point.bind
        if self.state != Point.STATE_REF:
            return warning("You can only bind to a Point(REF)")

        #This will kick off a BIND to the other end,
        #and either a BOUND or NOTBOUND coming back, or a TIMEOUT locally
        self.space.bind_point(self.parent_thing.thing_id, self.point_addr)

        timer = Timer(2) # 2 second timeout
        while not timer.check() and self.state == Point.STATE_REF:
            ##trace("waiting for BIND to succeed")
            Thing.tick_all()

        if self.state == Point.STATE_REF:
            # must be timeout
            return error("Timeout while waiting for BIND to occur")

        if self.state == Point.STATE_BIND_FAILED:
            self._become_ref()
            return error("BIND was rejected by other end")

        return self

    def rebind(self): #Point.rebind
        """Perform the local table update to create data structures,
           but don't initiate the META interaction, as the dependent
           Point might not be running at the moment.
        """
        ##trace("Thing(%s) rebinds to:%s" % (str(self.parent_thing), self.__repr__()))
        #NOTE: We could have a handler have_rebound()
        #it's not in the spec, but this is where it would go
        ##p = Point(parent_thing=self.parent_thing, name="meta_bind")
        ##p._become_ref(from_space, from_point_addr, register=False)
        ##p = self ##3HERE##: needs to be a lazy-Point for the sender
        ##self.have_rebound(p)
        self._become_bound()

    @auto_start
    def unbind(self): #Point.unbind
        if self.state != Point.STATE_BOUND:
            return warning("You can only unbind a Point(BOUND)")

        #This will kick off an UNBIND to the other end,
        #and either an UNBOUND or NOT_UNBOUND will come back, or a TIMEOUT locally
        self.space.unbind_point(self.parent_thing.thing_id, self.point_addr)

        timer = Timer(2) # 2 second timeout
        while not timer.check() and self.state == Point.STATE_BOUND:
            ##trace("waiting for UNBIND to succeed")
            Thing.tick_all()

        if self.state == Point.STATE_BOUND:
            # must be a timeout, stay bound
            return error("Timeout while waiting for UNBIND to occur")

        if self.state == Point.STATE_BIND_FAILED:
            # stay bound
            return error("UNBIND was rejected by other end")

        return self

    def follow(self): #Point.follow
        return self.bind()

    def attach(self): #Point.attach
        """Attaches to the inner point reference"""
        return self.bind()

    def share(self, data=None): #Point.share
        return self.send(data)

    def ask(self, data=None): #Point.ask
        return self.send(data)

    def tell(self, data=None): #Point.tell
        return self.send(data, confirmed=True)

    def unfollow(self): #Point.unfollow
        return self.unbind()

    def detach(self): #Point.unattach
        return self.unbind()

    ##def delete(self): #Point.delete

    #----- CONCURRENT STUFF

    def tick(self): #Point.tick
        if self.prop_rate is not None:
            Producer.tick(self)

    #----- META HANDLERS

    def handle_BIND(self, from_space, from_point_addr): #Point.handle_BIND
        if self.state == Point.STATE_REAL:
            other = Point(parent_thing=self.parent_thing, name="meta_bind")
            other._become_ref(from_space, from_point_addr, register=False)

            result = self.bound_handler(other)
            if result is not None and result == False:
                # send back a failure
                from_space.bind_failed(self.point_addr, from_point_addr)
                # means it was rejected, so don't send confirm back
                return result

            # send back a confirmation
            from_space.bind_ok(self.point_addr, from_point_addr)
            return result

    def handle_BOUND(self, from_space, from_point_addr): #Point.handle_BOUND
        if self.state in [Point.STATE_REF, Point.STATE_BOUND]:
            ##p = Point(parent_thing=self.parent_thing, name="meta_bind")
            ##p._become_ref(from_space, from_point_addr, register=False)
            p = self ##3HERE##: needs to be a lazy-Point for the sender
            self.have_bound(p)
            # Now change into the BOUND state
            self._become_bound()
            return True #DONE

    def handle_UNBIND(self, from_space, from_point_addr): #Point.handle_UNBIND
        if self.state == Point.STATE_REAL:
            other = Point(parent_thing=self.parent_thing, name="meta_unbind")
            # Passing registered=False means this doesn't end up in the thing.your_points table.
            # that would be bad, as it will then nick the meta messages for the real point
            other._become_ref(from_space, from_point_addr, register=False)
            result = self.unbound_handler(other)
            if result is not None and result == False:
                # send back a failure
                from_space.unbind_failed(self.point_addr, from_point_addr)
                # means it was rejected, so don't send confirm back
                return result

            # send back a confirmation
            from_space.unbind_ok(self.point_addr, from_point_addr)
            return result

    def handle_UNBOUND(self, from_space, from_point_addr): #Point.handle_UNBOUND
        if self.state in [Point.STATE_REF, Point.STATE_BOUND]:
            ##p = Point(parent_thing=self.parent_thing, name="meta_bind")
            ##p._become_ref(from_space, from_point_addr, register=False)
            p = self ##3HERE##: needs to be a lazy-Point for the sender
            self.have_unbound(p)
            # Now change back to REF state
            self._become_ref()
            return True #DONE


#----- TESTER -----------------------------------------------------------------
# A data-producing tester that you can just hook up to to generate 1 sec ticks
#This could just be a Point() once we have run() working?
#This is just a Point() with repeating behaviour?
#actually, could easily change it to be a Point later, and the examples
#that use it will still work - updated() is just an alias for
#something_happened
#TODO: would be nice to have this Point pre-baked into the iot.py
#so you can just follow it and it generates you some test data

class Tester(object):
    def __init__(self, rate=1): #Tester.__init__
        self.rate = rate
        self.next = time.time() + rate

    #TODO: if doing it with a Point
    ##@property # getter
    ##def updated(self):
    ##    return self.something_happened()

    def something_happened(self): #Tester.something_happened
        now = time.time()
        if now > self.next:
            self.next = now + self.rate
            return True
        return False

tester = Tester(1)


#----- iot.xxx module interface with properties too ---------------------------

class IOT(object): # IOT()
    FASTEST   = runner.FASTEST
    IMMEDIATE = Producer.IMMEDIATE
    TIMED     = Producer.TIMED
    TRIGGERED = Producer.TRIGGERED

    def __init__(self, parent): #IOT.__init__
        self.real_module = parent

        #TODO: Turn this into an internal Point instance we can bind to
        self.tester      = self.real_module.tester
        self.last_value  = None

        self.startup_mode           = Producer.IMMEDIATE
        self.startup_rate           = None
        self.startup_send_on_change = None

        ##self.receiver = PointList("receiver")

        # Due to a dependency race, we have to set this here
        global runner
        runner.set_parent(self)

    def __repr__(self): #IOT.__repr__
        return "It's a secret, no peeking!"

    def set_mode(self, mode): #IOT.set_mode
        #TODO: should check self.runner.is_running??
        try:
            self.unassigned_attacher.set_mode(mode)
        except:
            self.startup_mode = mode

        #NOTE: Could set_mode on self.receiver too,
        #but that gets really confusing as your controls then start
        #sending (and looping back to self)

    #----- PROPERTIES -----------------------------------------------------

    @property #readonly
    # Not auto-start, as it is a collection, not a default
    def things(self): #IOT.things PROPERTY
        # This gives access to Thing.things[name]
        # therefore also to Thing.things[name].feeds
        # and Thing.things[name].controls
        # and Thing.things[name].points
        # which are all very useful debug state
        return Thing.things

    @property #readonly
    @auto_start
    def thing(self): #IOT.thing PROPERTY
        return Thing.default_thing

    @property #readonly
    @auto_start
    def feed(self): #IOT.feed PROPERTY
        return Thing.default_thing.default_feed # use thing error handling

    @property #readonly
    @auto_start
    def control(self): #IOT.control PROPERTY
        return Thing.default_thing.default_control # use thing error handling

    @property #readonly
    @auto_start
    def unassigned_attacher(self): #IOT.unassigned_attacher PROPERTY
        return Thing.default_thing.unassigned_attacher # use our own error handling

    ##@property #readonly
    ##@auto_start
    ##def unassigned_follower(self): #IOT.unassigned_follower PROPERTY
    ##    return Thing.default_thing.unassigned_follower # use our own error handling

    @property #value.getter
    def value(self): #IOT.value PROPERTY
        #TODO: should this get last value sent from feed
        #or last value received from unassigned_follower?
        return self.last_value

    @value.setter #value.setter
    @auto_start
    def value(self, value):
        self.last_value = value
        #TODO: Should this also actuate unassigned_attacher?
        self.feed.share(value)

    @property
    def send_on_change(self): #IOT.send_on_change PROPERTY
        # We use the default 'feed' here.
        # in the future it might use unassigned_attacher also
        #TODO: if feed/unassigned_attacher are different, what do we do?
        try:
            return self.feed.send_on_change
        except:
            return self.startup_send_on_change

    @send_on_change.setter
    def send_on_change(self, value):
        #TODO: if feed/unassigned_attacher are different, what do we do?
        try:
            self.feed.send_on_change = value
        except:
            self.startup_send_on_change = value

        try:
            self.unassigned_attacher.send_on_change = value
        except:
            self.startup_send_on_change = value

    @property
    def rate(self): #IOT.rate PROPERTY
        # the default 'feed' rate
        # might use unassigned_attacher also
        #TODO: if feed/unassigned_attacher are different, what do we do?
        try:
            return self.feed.rate
        except:
            return self.startup_rate

    @rate.setter
    def rate(self, value):
        # use feed
        # might use unassigned_attacher also
        #TODO: if feed/unassigned_attacher are different, what do we do?
        try:
            self.feed.rate = value
        except Exception:
            self.startup_rate = value

        try:
            self.unassigned_attacher.rate = value
        except Exception:
            self.startup_rate = value

    @auto_start
    def trigger(self): #IOT.trigger
        #TODO: if feed/unassigned_attacher are different, what do we do?
        self.feed.trigger()
        self.unassigned_attacher.trigger()

    def restore(self): #IOT.restore
        default_space.restore() ##2HERE## deprecate default_space, use a self.space

    #----- FACTORIES ------------------------------------------------------

    def default_thing_needed(self): #IOT.default_thing_needed
        if Thing.default_thing is None:
            self.create_default_thing()
        return Thing.default_thing

    def create_default_thing(self): #IOT.create_default_thing
        if Thing.default_thing is None:
            # There is no default thing, so create one from defaults
            self.create_thing(CONFIG.default_thing_name)
        return Thing.default_thing

    def create_default_feed(self): #IOT.create_default_feed
        dt = self.default_thing_needed() #no @auto_start, so need this
        if Thing.default_thing.default_feed is None:
            # no Feeds yet, so create one, it will be the default
            dt.create_feed(CONFIG.default_feed_name)
        return Thing.default_thing.default_feed

    def create_default_control(self): #IOT.create_default_control
        dt = self.default_thing_needed() #no @auto_start, so need this
        if Thing.default_thing.default_control is None:
            # no Controls yet, so create one, it will be the default
            dt.create_control(CONFIG.default_control_name)
        return Thing.default_thing.default_control

    def create_thing(self, name): #IOT.create_thing()
        t = Thing.create_thing(name, parent=self)
        return t

    def create_feed(self, name): #IOT.create_feed()
        # always creates feed on the default thing
        dt = self.default_thing_needed() # no @auto_start, so need this
        f = dt.create_feed(name)
        return f

    def create_control(self, name): #IOT.create_control()
        # always creates control on the default thing
        dt = self.default_thing_needed() # no @auto_start, so need this
        c = dt.create_control(name)
        return c

    #----- VERBS ----------------------------------------------------------

    @auto_start
    def find(self, *args): # IOT.find()
        ##trace("iot.find:%s" % str(args))
        if len(args) == 0:
            return error("What do you want to find?")

        # @auto_start so default is always there
        return Thing.default_thing.find(*args)

    def find_thing(self, thing_name=None):
        if thing_name is None:
            return self.thing # the default thing
        else:
            return Thing.find_thing(thing_name)

    @auto_start
    def show(self): #IOT.show()
        # make default thing public
        Thing.default_thing.show() # @auto_start so already a default_thing

    @auto_start
    def hide(self): #IOT.hide()
        # make default thing hidden
        Thing.default_thing.hide() # @auto_start so already a default_thing

    @auto_start
    def follow(self, ref): # IOT.follow()
        #TODO might want a way to provide a handler here too
        # Will only work if you have single default Thing
        return Thing.default_thing.follow(ref) # @auto_start so already a default_thing

    @auto_start
    def attach(self, lhs_thing, rhs_point): # IOT.attach()
        ##trace("IOT.attach")
        return lhs_thing.attach(rhs_point)

    @auto_start
    def share(self, data=None): # IOT.share
        self.feed.share(data)

    @auto_start
    def ask(self, data=None): # IOT.ask
        self.unassigned_attacher.ask(data)

    def tell(self, data=None): #IOT.tell
        error("iot.tell is not allowed - how could we confirm multiple receipts?")

    @auto_start
    def unfollow(self, feed): #IOT.unfollow
        Thing.default_thing.unfollow(feed) # @auto_start so already a default_thing

    @auto_start
    def detach(self, point): #IOT.detach
        Thing.default_thing.detach(point) # @auto_start so already a default_thing

    @auto_start
    def delete(self, point): #IOT.delete
        Thing.default_thing.delete(point) # @auto_start so already a default_thing

    #----- HANDLERS -------------------------------------------------------
    #NOTE these are just redirectors
    #can't really use create_handler here as we don't want a new handler,
    #we just want to reuse handlers

    #FEED LHS HANDLERS
    def when_feed_created(self, m): #IOT DECORATOR
        return self.thing.when_feed_created(m) # use own error handler on 'thing'

    def when_new_follower(self, m): #IOT DECORATOR
        return self.feed.when_new_follower(m) # use own error handler on 'feed'

    def when_lost_follower(self, m): #IOT DECORATOR
        return self.feed.when_lost_follower(m) # use own error handler on 'feed'

    def when_feed_deleted(self, m): #IOT DECORATOR
        return self.thing.when_feed_deleted(m) # use own error handler on 'thing'

    # FEED RHS HANDLERS
    def when_have_followed(self, m): #IOT DECORATOR
        return self.thing.when_have_followed(m) # use own error handler on 'thing'

    def when_feed_updated(self, m): #IOT.when_feed_updated DECORATOR
        return self.feed.when_updated(m) # use own error handler on 'feed'

    def when_have_unfollowed(self, m): #IOT DECORATOR
        return self.thing.when_have_unfollowed(m) # use own error handler on 'thing'

    def when_lost_feed(self, m): #IOT DECORATOR
        return self.thing.when_lost_feed(m) # use own error handler on 'thing'

    # CONTROL RHS HANDLERS

    def when_control_created(self, m): #IOT DECORATOR
        return self.thing.when_control_created(m) # use own error handler on 'thing'

    def when_new_attacher(self, m): #IOT DECORATOR
        return self.control.when_new_attacher(m) # use own error handler on 'control'

    def when_control_updated(self, m): #IOT.when_control_updated DECORATOR
        return self.control.when_updated(m) # use own error handler on 'control'

    def when_lost_attacher(self, m): #IOT DECORATOR
        return self.control.when_lost_attacher(m) # use own error handler on 'control'

    def when_control_deleted(self, m): #IOT DECORATOR
        return self.thing.when_control_deleted(m) # use own error handler on 'thing'

    # CONTROL LHS HANDLERS

    def when_have_attached(self, m): #IOT DECORATOR
        return self.thing.when_have_attached(m) # use own error handler on 'thing'

    def when_have_detached(self, m): #IOT DECORATOR
        return self.thing.when_have_detached(m) # use own error handler on 'thing'

    def when_lost_control(self, m): #IOT DECORATOR
        return self.thing.when_lost_control(m) # use own error handler on 'thing'

    # GENERIC HANDLERS

    ##def when_updated(self, m): #IOT.when_updated DECORATOR
    ##    return self.receiver.when_updated(m)

    def DEFAULT(self, *args, **kwargs): #IOT.DEFAULT() handler METHOD
        global DEFAULT
        return DEFAULT(*args, **kwargs)

    def IGNORE(self, *args, **kwargs): # IOT.IGNORE() handler METHOD
        global IGNORE
        return IGNORE(*args, **kwargs)

    #----- CONNECTION -----------------------------------------------------

    def identify(self): #IOT.identify
        #TODO: credentials come from ini file, along with server.crt
        return default_space.identify() ##2HERE## deprecate default_space, use self.space

    def connect(self, retries=CONFIG.connect_retries): # IOT.connect
        #TODO: if temporary error, retry a fixed number of times
        #TODO: if permanent error, show error and stop script
        return default_space.connect() ##2HERE## deprecate default_space, use self.space

    def authenticate(self): #IOT.authenticate
        return default_space.authenticate() ##2HERE## deprecate default_space use self.space
        #TODO: using credentials from ini, authenticate to iotic space
        #if works, keep going
        #if fails, show error and stop script

    def disconnect(self): #IOT.disconnect
        self.stop() # seems the most reliable way to do this

    #TODO: connection monitoring
    #@unimplemented
    #def start_connection_monitor():
    #    pass # TODO
    #    #start a connection monitor via heartbeat
    #    #if connection is lost later, call user provided 'disconnected' handler
    #    #if provided. Default will be to just say 'temporary connection loss'
    #    #retry a fixed number of times.
    #    #if get reconnected, call user provided 'connected' handler
    #    #if provided. Default will be to just say 'recovered'
    #    #if fails after fixed retry time from ini, show error and stop script


    #----- RUN ----------------------------------------------------------------

    def start(self): #IOT.start
        # Create appropriate defaults, if necessary
        self.default_thing   = self.create_default_thing()
        self.create_default_feed()    #always default_thing.default_feed
        self.create_default_control() #always default_thing.default_control

        if self.default_thing is not None:
            # all Thing's have an unassigned_control
            # copy startup mode values
            dt = self.default_thing
            uc = dt.unassigned_attacher
            uc.set_mode(self.startup_mode)
            uc.rate           = self.startup_rate
            uc.send_on_change = self.startup_send_on_change

            ##self.receiver += dt.unassigned_follower #TODO: or just dt (dt.when_updated->t.when_updated)??

            if dt.default_feed is not None:
                # copy startup values
                df = dt.default_feed
                df.set_mode(self.startup_mode)
                df.rate           = self.startup_rate
                df.send_on_change = self.startup_send_on_change

            ##if dt.default_control is not None:
            ##    dc = dt.default_control
            ##    self.receiver += dc


    def run(self, *args, **kwargs): #IOT.run
        return runner.run(*args, **kwargs) ##2HERE## put runner in space, and then use self.space.run

    def tick(self): # IOT.tick
        # This is what the user calls
        # It may have some throttling behaviour in 'runner'
        return runner.tick() ##2HERE## put runner in space then use self.space.tick

    def stop(self): # IOT.stop
        runner.stop() ##2HERE## put runner in space and then use self.space stop

    def real_tick(self): #IOT.real_tick
        """This is the actual tick behaviour"""
        Thing.tick_all()

    def boot(self): #IOT.boot
        ##trace("auto booting space")
        """Call this again if you want to re-run the import behavior (e.g. testing)"""
        ##self.identify()
        self.connect() # required for DBSpace
        ##self.authenticate()
        ##self.start_connection_monitor()


#----- AUTO-CONNECT ON IMPORT -------------------------------------------------

import sys
real_module = sys.modules[__name__]
iot = IOT(real_module) ##2HERE## pass in the default_space we want it to use here, Space includes Runner

if CONFIG.auto_boot:
    print("booting...")
    iot.boot() # Note, this will connect() implying disconnect() must be done before exit
    print("booted.")

# If running from python shell, might get an exception and be thrown to the shell prompt
# after connect() has been called, so need to make sure disconnect() occurs on quit()

if main is None:
    # Using the Python shell
    # Do some magic to override quit() as atexit is not working as expected in the shell?
    try:
        import _sitebuiltins
        quitter   = _sitebuiltins.Quitter
        real_quit = quitter.__call__ # the existing quit function

        def iotquit(self):
            print("You typed quit() so I am doing iot.stop() for you")
            iot.stop()
            real_quit(self) # the real quit function
        quitter.__call__ = iotquit

    except ImportError:
        pass # no way to override quit() or exit() if the Quitter is not installed


if __name__ == "__main__": # python iot.py
    print("IoT is now running!")
    iot.run()

else: # import iot
    # WRAP
    # the whole point of this is so we can surface properties,
    # which modules do not normally support but classes do
    # Override this module in the system module table
    if main is None:
        # Using the Python shell
        print("You are now connected to the Internet of Things!")
        print("type dir(iot) for a list of commands")

    sys.modules[__name__] = iot

# END

