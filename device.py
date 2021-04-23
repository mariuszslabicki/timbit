import simpy

class Device(object):
    def __init__(self, env, dev_name):
        self.env = env
        self.network = []
        self.dev_name = dev_name
        self.env.process(self.transmit_ADV())
        self.env.process(self.move_device())

    def transmit_ADV(self):
        while True:
            yield self.env.timeout(250)
            print(self.env.now, self.dev_name + " I am sending ADV")
            self.network.propagate_ADV(self)

    def move_device(self):
        while True:
            yield self.env.timeout(150)
            print(self.env.now, " I am moving")

    def receive_ADV(self):
        print(self.dev_name + " Cool, I got it")
