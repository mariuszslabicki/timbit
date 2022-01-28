import device
import random
import math

class Network(object):
    def __init__(self, env, config, pathloss_model):
        self.mobile_devices = []
        self.static_devices = []
        self.env = env
        self.pathloss_model = pathloss_model
        if self.pathloss_model == "matrix_based":
            import pathloss_matrix
        self.config = config
        self.x_size = int(self.config["network_size_x"])
        self.y_size = int(self.config["network_size_y"])
        self.mes_dimension = int(self.config["number_of_mobile_dev"]) + int(self.config["number_of_static_dev"])

    def add_mobile_node(self, id):
        dev = device.Device(self.env, id, self.config, self.mes_dimension)
        self.mobile_devices.append(dev)
        dev.network = self
        dev.x_limit = self.x_size
        dev.y_limit = self.y_size
        dev.x = random.randint(0, dev.x_limit)
        dev.y = random.randint(0, dev.y_limit)

    def add_static_node(self, id):
        dev = device.Device(self.env, id, self.config, self.mes_dimension, static=True)
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
            if self.pathloss_model == "rssi_based":
                RSSI = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 25)
            device.receive_ADV(sender, RSSI, distance)
        for device in self.static_devices:
            if device == sender:
                continue
            distance = math.hypot(sender.x - device.x, sender.y - device.y)
            if distance < 1:
                distance = 1
            if self.pathloss_model == "rssi_based":
                RSSI = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
            device.receive_ADV(sender, RSSI, distance)

    def send_report_to_server(self, nodeType, id, report, creationTime, measurements):
        self.server.receive_report(nodeType, id, report, creationTime, measurements)
        