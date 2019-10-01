#test_objects.py -  A bit like IOToy
# http://www.sparkslabs.com/iotoy/

#TESTED: WORKS
#OUTPUT
#RealMover:forward
#RealMover:left
#RealMover:stop
#RealMover:forward
#^CTraceback (most recent call last):
#  File "example24.py", line 103, in <module>
#    time.sleep(1)
#KeyboardInterrupt
#warning:you forgot to iot.stop(), doing it for you now
#iot:stopping...
#iot:stopped.
#/OUTPUT

#TODO: move Mover abstraction into 'devices'
#TODO: this could inherit from Point - that is a different example

#TODO: The whole IoToy thing was about AUTO GENERATING a proxy class
#it's just RPC stubs and skeletons all over again.
#So, the Virtualxxx object and Realxxx objects could just be
#auto-generating adaptors - you give a definition of an API
#(e.g. via provided metadata) and it RPC stub/skeleton generates
#both objects for you. Iotic Objects!!

#is-a Mover, has-a Point
class VirtualMover(object): # The Iotic sender part # VirtualMover
    def __init__(self, point):
        self.point = point

    def send(self, msg):
        self.point.send(msg)

    def forward(self):
        self.send("forward")

    def stop(self):
        self.send("stop")

    def backward(self):
        self.send("backward")

    def left(self):
        self.send("left")

    def right(self):
        self.send("right")

# There is also an iotic receiver part
# This could have-a Point, or be-a Point - both different examples

# is-a Mover, has-a Point
#error: written like it is-a point
class RealMover():
    def __init__(self, point, GPIO=None, lma=None, lmb=None, rma=None, rmb=None):
        pass #TODO wire up to GPIO pins
        #NOTE: check this is the best style to use for wiring user handler
        point.when_updated(self.update)

    #NOTE: As this is a class, and not an instance, can't wire-up handler
    #here via an annotation, as the instance does not exist yet.
    def update(self, sender, data):
        ##print("robot data:%s" % str(data))
        if   data == "left":     self.left()
        elif data == "right":    self.right()
        elif data == "forward":  self.forward()
        elif data == "backward": self.backward()
        elif data == "stop":     self.stop()
        else: print("Invalid command:%s" % str(data))

    def left(self):
        pass #TODO: configure appropriate GPIO's
        print("RealMover:left")

    def right(self):
        pass #TODO: configure appropriate GPIO's
        print("RealMover:right")

    def forward(self):
        pass #TODO: configure appropriate GPIO's
        print("RealMover:forward")

    def backward(self):
        pass #TODO: configure appropriate GPIO's
        print("RealMover:backward")

    def stop(self):
        pass #TODO: configure appropriate GPIO's
        print("RealMover:stop")


import iot, time
##import RPi.GPIO, devices

iot.start() # creates default points

##my_robot = devices.RealMover(iot.control, RPi.GPIO, 4,5,6,7)
my_robot = RealMover(iot.default_control)

# ##your_robot = devices.VirtualMover(iot.find("your_robot").attach())
#your_robot = VirtualMover(iot.find(iot.control).attach()) # local loopback
your_iot_robot = iot.find("control")
your_iot_robot.attach()
your_robot = VirtualMover(your_iot_robot)


#note the automated bind after find, will fail with exception if not found
#but will bind if has found
#TODO: need to test that!

for i in range(4):
    your_robot.forward()
    time.sleep(1)

    your_robot.left()
    time.sleep(1)

    your_robot.stop()
    time.sleep(1)

# END
