import device
import random
import math

class Network(object):
    def __init__(self, env, config, pathloss_model):
        self.mobile_devices = []
        self.static_devices = []
        self.env = env
        self.config = config
        self.x_size = int(self.config["network_size_x"])
        self.y_size = int(self.config["network_size_y"])
        self.pathloss_model = pathloss_model
        self.pathloss_disk_range = int(self.config["pathloss_disk_range"])
        if self.pathloss_model == "matrix_based":
            import pathloss_matrix
            self.obstacle_calc = pathloss_matrix.PathlossCalculator(self.x_size+2, self.y_size+2)
        if self.pathloss_model == "fastel_dynamic":
            import pathloss_fastel
            self.pathloss_calc = pathloss_fastel.PathlossCalculator()

    def add_mobile_node(self, id):
        dev = device.Device(self.env, id, self.config)
        self.mobile_devices.append(dev)
        dev.network = self
        dev.x_limit = self.x_size
        dev.y_limit = self.y_size
        dev.x = random.randint(0, dev.x_limit)
        dev.y = random.randint(0, dev.y_limit)

    def add_static_node(self, id):
        dev = device.Device(self.env, id, self.config, static=True)
        self.static_devices.append(dev)
        dev.network = self
        dev.x_limit = self.x_size
        dev.y_limit = self.y_size
        dev.x = random.randint(0, dev.x_limit)
        dev.y = random.randint(0, dev.y_limit)

    def add_server(self, srv):
        self.server = srv
        self.server.network = self

    def propagate_ADV(self, sender):
        for device in self.mobile_devices:
            if device == sender:
                continue
            distance = math.hypot(sender.x - device.x, sender.y - device.y)
            if self.pathloss_disk_range > 0:
                if distance > self.pathloss_disk_range:
                    continue
            if distance < 1:
                distance = 1
            if self.pathloss_model == "rssi_based":
                RSSI = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
            if self.pathloss_model == "matrix_based":
                pure_loss = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
                obstacle_loss = self.obstacle_calc.return_obstacle_pathloss(math.floor(sender.x), math.floor(sender.y), math.floor(device.x), math.floor(device.y))
                RSSI = pure_loss - obstacle_loss
            if self.pathloss_model == "fastel_static":
                RSSI = -67.580939 + 10 * (-1.78691694) * math.log10(distance/5)
            if self.pathloss_model == "fastel_dynamic":
                path_loss = self.pathloss_calc.return_pathloss(sender.x, sender.y, device.x, device.y)
                RSSI = path_loss
            device.receive_ADV(sender, RSSI, distance, self.pathloss_model)
        for device in self.static_devices:
            if device == sender:
                continue
            distance = math.hypot(sender.x - device.x, sender.y - device.y)
            if self.pathloss_disk_range > 0:
                if distance > self.pathloss_disk_range:
                    continue
            if distance < 1:
                distance = 1
            if self.pathloss_model == "rssi_based":
                RSSI = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
            if self.pathloss_model == "matrix_based":
                pure_loss = -9.427 * math.log(distance) - 62.874 + random.normalvariate(0, 5)
                obstacle_loss = self.obstacle_calc.return_obstacle_pathloss(math.floor(sender.x), math.floor(sender.y), math.floor(device.x), math.floor(device.y))
                RSSI = pure_loss - obstacle_loss
            if self.pathloss_model == "fastel_static":
                RSSI = -67.580939 + 10 * (-1.78691694) * math.log10(distance/5)
            if self.pathloss_model == "fastel_dynamic":
                path_loss = self.pathloss_calc.return_pathloss(sender.x, sender.y, device.x, device.y)
                RSSI = path_loss
            device.receive_ADV(sender, RSSI, distance, self.pathloss_model)

    def send_report_to_server(self, nodeType, id, report, creationTime):
        self.server.receive_report(nodeType, id, report, creationTime)
    
    def send_response_to_device(self, nodeType, id, creationTime):
        if nodeType == "M":
            self.mobile_devices[id].receive_response(creationTime)
        if nodeType == "S":
            self.static_devices[id].receive_response(creationTime)
        