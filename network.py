import device
import random
import math

class Network(object):
    def __init__(self, env, config, pathloss_model):
        self.mobile_devices = []
        self.static_devices = []
        self.dictionary_devices = {}
        self.env = env
        self.config = config
        self.x_size = int(self.config["network_size_x"])
        self.y_size = int(self.config["network_size_y"])
        # self.mes_dimension = int(self.config["number_of_mobile_dev"]) + int(self.config["number_of_static_dev"])
        self.pathloss_model = pathloss_model
        if self.pathloss_model == "matrix_based":
            import pathloss_matrix
            self.obstacle_calc = pathloss_matrix.PathlossCalculator(self.x_size+2, self.y_size+2)

    def add_mobile_node(self, id):
        dev = device.Device(self.env, id, self.config)
        self.mobile_devices.append(dev)
        dev.network = self
        self.dictionary_devices[str(id)+'D'] = dev
        dev.x_limit = self.x_size
        dev.y_limit = self.y_size
        dev.x = random.randint(0, dev.x_limit)
        dev.y = random.randint(0, dev.y_limit)

    def add_static_node(self, id):
        dev = device.Device(self.env, id, self.config)
        self.static_devices.append(dev)
        dev.network = self
        self.dictionary_devices[str(id)+'S'] = dev
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
                RSSI = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
            if self.pathloss_model == "matrix_based":
                pure_loss = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
                obstacle_loss = self.obstacle_calc.return_obstacle_pathloss(math.floor(sender.x), math.floor(sender.y), math.floor(device.x), math.floor(device.y))
                RSSI = pure_loss - obstacle_loss
            device.receive_ADV(sender, RSSI, distance)
        for device in self.static_devices:
            if device == sender:
                continue
            distance = math.hypot(sender.x - device.x, sender.y - device.y)
            if distance < 1:
                distance = 1
            if self.pathloss_model == "rssi_based":
                RSSI = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
            if self.pathloss_model == "matrix_based":
                pure_loss = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
                obstacle_loss = self.obstacle_calc.return_obstacle_pathloss(math.floor(sender.x), math.floor(sender.y), math.floor(device.x), math.floor(device.y))
                RSSI = pure_loss - obstacle_loss
            device.receive_ADV(sender, RSSI, distance)

    def send_report_to_server(self, nodeType, id, report, creationTime, measurements):
        self.server.receive_report(nodeType, id, report, creationTime, measurements)
        