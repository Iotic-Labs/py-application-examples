# RPi.GPIO.py (mock for testing)  24/11/2016  D.J.Whale

# Actual values not important
BCM     = 1
BOARD   = 2
IN      = 4
OUT     = 8
RISING  = 16
FALLING = 32

pins = {} # number: {mode, state, conditions, callback}

def setmode(mode):
    pass # ignored

def setup(pin, mode):
    pins[pin] = {"mode": mode, "state": 0, "conditions": None, "callback": None}

def mock_input(pin, value):
    # will fail if setup() not called on pin, that is correct
    p = pins[pin]
    p["value"] = value # can be later read by input(pin)
    if p["callback"] is not None and p["conditions"] is not None:
        # process event callback handler
        c = p["conditions"]
        # assume value True or False for now, will have to fix later if numbers
        if value     and ((c & RISING) !=0 ) \
        or not value and ((c & FALLING) != 0):
            callback = p["callback"]
            callback(pin, value)


def input(pin):
    # will fail, intentionally, if pin not setup() first
    return pins[pin]["value"]

def output(pin, value):
    # will fail, intentionally, if pin not setup() first
    print("GPIO[%s] = %s" % (str(pin), str(value)))
    pins[pin]["value"] = value

def add_event_detect(pin, conditions, callback=None):
    # will fail, intentionally, if pin not setup() first
    p = pins[pin]
    p["callback"]    = callback
    p["conditions"] = conditions

def cleanup():
    pass # ignored

# END
