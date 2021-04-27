import random
import math

class Network(object):
    def __init__(self, env, x_size=100, y_size=100):
        self.devices = []
        self.env = env
        self.x_size = x_size
        self.y_size = y_size

    def add_in_random_position(self, device):
        self.devices.append(device)
        device.network = self
        device.x_limit = self.x_size
        device.y_limit = self.y_size
        device.x = random.randint(0, device.x_limit)
        device.y = random.randint(0, device.y_limit)

    def add_server(self, srv):
        self.server = srv

    def propagate_ADV(self, sender):
        print("Network: I am propagating ADV")
        for device in self.devices:
            if device == sender:
                continue
            print("Distance is", math.hypot(sender.x - device.x, sender.y - device.y))
            if math.hypot(sender.x - device.x, sender.y - device.y) > sender.communication_range:
                continue
            device.receive_ADV()

    def send_report_to_server(self):
        print(self.env.now, "Network: delivering to server")
        self.server.receive_report()
        print(self.env.now, "Network: finished delivering to server")
        