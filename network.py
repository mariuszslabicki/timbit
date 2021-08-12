import device
import random
import math

class Network(object):
    def __init__(self, env, x_size=100, y_size=100):
        self.mobile_devices = []
        self.static_devices = []
        self.env = env
        self.x_size = x_size
        self.y_size = y_size

    def add_mobile_node(self, id):
        dev = device.Device(self.env, id)
        self.mobile_devices.append(dev)
        dev.network = self
        dev.x_limit = self.x_size
        dev.y_limit = self.y_size
        dev.x = random.randint(0, dev.x_limit)
        dev.y = random.randint(0, dev.y_limit)

    def add_static_node(self, id):
        dev = device.Device(self.env, id, static=True)
        self.static_devices.append(dev)
        dev.network = self
        dev.x_limit = self.x_size
        dev.y_limit = self.y_size
        dev.x = random.randint(0, dev.x_limit)
        dev.y = random.randint(0, dev.y_limit)

    def add_server(self, srv):
        self.server = srv

    def propagate_ADV(self, sender):
        for device in self.mobile_devices:
            if device == sender:
                continue
            distance = math.hypot(sender.x - device.x, sender.y - device.y)
            if distance < 1:
                distance = 1
            #Path loss from here: https://en.wikipedia.org/wiki/ITU_model_for_indoor_attenuation
            # path_loss = 20*math.log10(2400) + 30*math.log10(distance) - 28 + random.normalvariate(0, 5)
            # device.receive_ADV(sender, path_loss, distance)
            RSSI = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
            device.receive_ADV(sender, RSSI, distance)
        for device in self.static_devices:
            if device == sender:
                continue
            distance = math.hypot(sender.x - device.x, sender.y - device.y)
            if distance < 1:
                distance = 1
            #Path loss from here: https://en.wikipedia.org/wiki/ITU_model_for_indoor_attenuation
            # path_loss = 20*math.log10(2400) + 30*math.log10(distance) - 28 + random.normalvariate(0, 5)
            # device.receive_ADV(sender, path_loss, distance)
            RSSI = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
            device.receive_ADV(sender, RSSI, distance)

    def send_report_to_server(self, nodeType, id, report, creationTime):
        self.server.receive_report(nodeType, id, report, creationTime)
        