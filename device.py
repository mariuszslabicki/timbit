import random
import simpy

class Device(object):
    def __init__(self, env):
        self.env = env
        self.x = None
        self.y = None
        self.x_limit = None
        self.y_limit = None
        self.env.process(self.transmit_ADV())
        self.env.process(self.keep_moving())

    def transmit_ADV(self):
        while True:
            yield self.env.timeout(250)
            print(self.env.now, "" "I am sending ADV")
            self.network.propagate_ADV(self)

    def keep_moving(self):
        while True:
            yield self.env.timeout(150)
            self.make_a_move()
            print(self.env.now, " I am moving to ", self.x, self.y)

    def make_a_move(self):
        self.x = self.x + random.choice([-1, 1])
        if self.x > self.x_limit:
            self.x = self.x_limit
        self.y = self.y + random.choice([-1, 1])
        if self.y > self.y_limit:
            self.y = self.y_limit

    def receive_ADV(self):
        print(self.env.now, " Cool, I got it")
