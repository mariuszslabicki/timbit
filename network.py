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
        for device in self.devices:
            if device == sender:
                continue
            distance = math.hypot(sender.x - device.x, sender.y - device.y)
            if distance < 1:
                distance = 1
            #Path loss from here: https://en.wikipedia.org/wiki/ITU_model_for_indoor_attenuation
            # path_loss = 20*math.log10(2400) + 30*math.log10(distance) - 28 + random.normalvariate(0, 5)
            # device.receive_ADV(sender, path_loss, distance)
            RSSI = -9.427 * math.log(distance) - 62.874
            device.receive_ADV(sender, RSSI, distance)

    def send_report_to_server(self, id, report, creationTime):
        self.server.receive_report(id, report, creationTime)
        