import random

class Network(object):
    def __init__(self, x_size=100, y_size=100):
        self.devices = []
        self.x_size = x_size
        self.y_size = y_size

    def add_in_random_position(self, device):
        self.devices.append(device)
        device.network = self
        device.x_limit = self.x_size
        device.y_limit = self.y_size
        device.x = random.randint(0, device.x_limit)
        device.y = random.randint(0, device.y_limit)

    def propagate_ADV(self, sender):
        print("Network: I am propagating ADV")
        for device in self.devices:
            if device == sender:
                continue
            device.receive_ADV()