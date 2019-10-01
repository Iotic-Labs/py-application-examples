#test_hw.py - clearly separate user code and iotic code

#OUTPUT
#warning:You forgot to iot.start(), doing it for you now
#warning:start() called when already running - ignoring
#simPIR=False
#iot:tick
#sharing Iotic LED:False
#just received LED:False
#GPIO[4] = False
#simPIR=False
#iot:tick
#sharing Iotic LED:False
#just received LED:False
#GPIO[4] = False
#simPIR=False
#iot:tick
#sharing Iotic LED:False
#just received LED:False
#GPIO[4] = False
#simPIR=True
#iot:tick
#sharing Iotic LED:True
#just received LED:True
#GPIO[4] = True
#simPIR=False
#iot:tick
#^CTraceback (most recent call last):
#  File "example21.py", line 144, in <module>
#    time.sleep(1)
#KeyboardInterrupt
#warning:you forgot to iot.stop(), doing it for you now
#iot:stopping...
#iot:stopped.
#/OUTPUT

import time


#----- LOCAL HARDWARE SECTION -------------------------------------------------

# HARDWARE CONFIGURATION
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
PIR = 14
GPIO.setup(PIR, GPIO.IN)
LED = 4
GPIO.setup(LED, GPIO.OUT)

# HARDWARE SIMULATOR FOR GPIO/PIR
pir_count = 0
PIR_RATE = 4 # simulation
def pir_sim():
    global pir_count
    # produce some test data on PIR
    pir_count = (pir_count + 1) % PIR_RATE
    if pir_count == 0:
        print("simPIR=True")
        GPIO.mock_input(PIR, True)
    else:
        print("simPIR=False")
        GPIO.mock_input(PIR, False)

# HARDWARE GETTER (POLLED)
def get_pir_hw():
    # user code, to get data from a sensor
    return GPIO.input(PIR)

# HARDWARE HANDLER (EVENT DRIVEN)
def pir_changed(pin):
    global pir
    print("HW PIR changed")
    pir = GPIO.input(pin)
    # immediate send
    ##   set_pir_iot(pir)
    ##   led = pir
    ##   set_led_iot(led)
GPIO.add_event_detect(PIR, GPIO.RISING & GPIO.FALLING, callback=pir_changed)


# HARDWARE SETTER
def set_led_hw(b):
    if b is None:
        print("ERROR: no value for LED")
    GPIO.output(LED, b)


#----- IOTIC SECTION ----------------------------------------------------------

#IOTIC CONFIGURATION
import iot

# Various different options on partitioning of connectivity
tx             = iot.create_thing("tx")
tx_pir_feed    = tx.create_feed("Fpir")
tx_led_feed    = tx.create_feed("Fled")

rx             = iot.create_thing("rx")
rx_pir_control = rx.create_control("Cpir")
rx_led_control = rx.create_control("Cled")

tx_pir_control = tx.find("rx", "Cpir").attach()
tx_led_control = tx.find("rx", "Cled").attach()

rx_pir_feed    = rx.find("tx", "Fpir").follow()
rx_led_feed    = rx.find("tx", "Fled").follow()



#Auto rate transmitting configuration options
## iot.feed.rate = 2
## iot.feed.send_on_change = True #note, this is ON by default
## iot.feed.send_on_change = False # This overrides the default behaviour

#IOTIC SETTER
def set_pir_iot(b):
    print("sharing Iotic PIR:%s" % str(b))
    # Feed OR Control
    tx_pir_feed.share(b)
    ## tx_pir_control.ask(b)
    ## tx_pir_control.tell(b)
    ## tx_pir_feed.value = b
    ## tx_pir_control.value = b
    ## tx_pir_control.confirming = True
    ## tx_pir_control.value = b

def set_led_iot(b):
    print("sharing Iotic LED:%s" % str(b))
    # Feed OR Control
    tx_led_feed.share(b)
    ## tx_led_control.ask(b)
    ## tx_led_control.tell(b)
    ## tx_led_feed.value = b
    ## tx_led_control.value = b
    ## tx_led_control.confirming = True
    ## tx_led_control.value = b

# IOTIC GETTER (POLL)
def get_pir_iot():
    # user code, to get data from a sensor
    return rx_pir_feed.value # poll point last_value
    ## return pir # poll value written to by update handler

def get_led_iot():
    return rx_led_feed.value # poll point last_value
    ## return led # poll value written to by update handler

# IOTIC HANDLER (EVENT DRIVEN)
#shows that you can register more than one handler at a time
@rx_pir_feed.when_updated
@rx_pir_control.when_updated
def update_pir(sender, data):
    global pir
    print("just received from:%s PIR:%s" % (str(sender), str(data)))
    pir = data
    # immediate handle
    ##   led = pir
    ##   hw_set_led(led)

@rx_led_feed.when_updated
@rx_led_control.when_updated
def update_led(sender, data):
    global led
    print("just received from:%s LED:%s" % (str(sender), str(data)))
    led = data
    # immediate handle
    ##   hw_set_led(led)


#----- MAIN APP LOOP ----------------------------------------------------------

iot.start() # no auto-start semantics yet

while True:
    pir_sim() # waggles simulated PIR input to generate GPIO callback
    iot.tick() # manually pump loop, no threads yet
    time.sleep(1)

    #----- LOCAL APP BASELINE -------------------------------------------------
    # real app code
    #PRODUCER/CONSUMER - LOCAL
    ##pir = get_pir_hw()
    ##led = pir
    ##set_led_hw(led)


    #----- PRODUCER/CONSUMER PIR ----------------------------------------------

    #PRODUCER - produces Iotic PIR
    ##pir = get_pir_hw()
    ##set_pir_iot(pir) # tx_pir_feed.share() -> rx_pir_feed.update()

    #CONSUMER - CONSUMES Iotic PIR by polling
    ##pir = get_pir_iot()
    ##led = pir
    ##set_led_hw(led)

    #----- PRODUCER/CONSUMER LED ----------------------------------------------
    #PRODUCER  - produces Iotic LED
    pir = get_pir_hw()
    led = pir
    set_led_iot(pir)

    #CONSUMER - CONSUMES Iotic LED by polling
    led = get_led_iot()
    set_led_hw(led)

#END
