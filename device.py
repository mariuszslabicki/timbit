import random
import simpy

class Device(object):
    def __init__(self, env):
        self.env = env
        self.x = None
        self.y = None
        self.x_limit = None
        self.y_limit = None
        self.steps_to_WP = 0
        self.communication_range = 10
        self.env.process(self.transmit_ADV())
        self.env.process(self.keep_moving())

    def transmit_ADV(self):
        while True:
            yield self.env.timeout(250)
            print(self.env.now, "I am sending ADV")
            self.network.propagate_ADV(self)

    def keep_moving(self):
        while True:
            if self.steps_to_WP == 0:
                self.steps_to_WP = 5
                self.WP_x = random.randint(0, self.x_limit)
                self.WP_y = random.randint(0, self.y_limit)
                self.delta_x = (self.WP_x - self.x) / self.steps_to_WP
                self.delta_y = (self.WP_y - self.y) / self.steps_to_WP

            yield self.env.timeout(150)
            self.make_a_move()
            print(self.env.now, " I am moving to ", self.x, self.y)

    def make_a_move(self):
        self.x += self.delta_x
        self.y += self.delta_y
        self.steps_to_WP -= 1

    def receive_ADV(self):
        print(self.env.now, " Cool, I got it")
        self.network.send_report_to_server()
