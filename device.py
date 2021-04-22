import simpy

class Device(object):
    def __init__(self, env, dev_name):
        self.env = env
        self.network = []
        self.dev_name = dev_name
        self.action = self.env.process(self.main_loop())

    def main_loop(self):
        while True:
            yield self.env.timeout(250)
            print(self.dev_name + " I am sending ADV")
            self.network.propagate_ADV(self)

    def receive_ADV(self):
        print(self.dev_name + " Cool, I got it")