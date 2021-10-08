import random
import math
import simpy

class Device(object):
    def __init__(self, env, id, config, static=False):
        self.env = env
        self.id = id
        self.static = static
        self.x = None
        self.y = None
        self.x_limit = None
        self.y_limit = None
        self.steps_to_WP = 0
        self.tx_power = 13 #dBm
        self.sensitivity = -95 #dBm
        self.known_static_nodes = {}
        self.known_dynamic_nodes = {}
        self.conf = config
        self.env.process(self.transmit_ADV())
        self.env.process(self.perform_server_report())
        if self.static is False:
            self.env.process(self.keep_moving())

    def transmit_ADV(self):
        while True:
            self.network.propagate_ADV(self)
            random_shift = random.randint(0, 10)
            yield self.env.timeout(100 + random_shift)

    def keep_moving(self):
        while True:
            location_update_interval = int(self.conf["location_update_interval"])
            updates_in_s = 1000/location_update_interval
            if self.steps_to_WP == 0:
                staying_time = random.uniform(int(self.conf["resting_time_min"]), int(self.conf["resting_time_max"]))
                yield self.env.timeout(staying_time)
                self.WP_x = random.randint(0, self.x_limit)
                self.WP_y = random.randint(0, self.y_limit)
                distance = math.hypot(self.x - self.WP_x, self.y - self.WP_y)
                speed = random.uniform(float(self.conf["node_speed_min"]), float(self.conf["node_speed_max"]))
                self.steps_to_WP = math.ceil(distance*updates_in_s*(1/speed))
                self.delta_x = (self.WP_x - self.x) / self.steps_to_WP
                self.delta_y = (self.WP_y - self.y) / self.steps_to_WP

            yield self.env.timeout(location_update_interval)
            self.make_a_step()

    def make_a_step(self):
        self.x += self.delta_x
        self.y += self.delta_y
        self.steps_to_WP -= 1

    def receive_ADV(self, sender, RSSI, distance):
        if RSSI > self.sensitivity:
            calculated_dist = 0.0261 * math.pow(RSSI, 2) + 3.4324 * RSSI + 113.64
            if sender.static is False:
                if sender.id not in self.known_dynamic_nodes:
                    self.known_dynamic_nodes[sender.id] = [True, calculated_dist, distance, sender.x, sender.y]
                else:
                    self.known_dynamic_nodes[sender.id][0] = True
                    self.known_dynamic_nodes[sender.id][1] += 0.5 * (calculated_dist - self.known_dynamic_nodes[sender.id][1])
                    self.known_dynamic_nodes[sender.id][2] = distance
                    self.known_dynamic_nodes[sender.id][3] = sender.x
                    self.known_dynamic_nodes[sender.id][4] = sender.y
            if sender.static is True:
                if sender.id not in self.known_static_nodes:
                    self.known_static_nodes[sender.id] = [True, calculated_dist, distance, sender.x, sender.y]
                else:
                    self.known_static_nodes[sender.id][0] = True
                    self.known_static_nodes[sender.id][1] += 0.5 * (calculated_dist - self.known_static_nodes[sender.id][1])
                    self.known_static_nodes[sender.id][2] = distance
                    self.known_static_nodes[sender.id][3] = sender.x
                    self.known_static_nodes[sender.id][4] = sender.y

    def perform_server_report(self):
        delta = random.randint(0, 1000)
        yield self.env.timeout(delta)
        while True:
            report = []
            for key in self.known_dynamic_nodes:
                if self.known_dynamic_nodes[key][0] is True:
                    self.known_dynamic_nodes[key][0] = False
                    dev_info = ["M", key, self.known_dynamic_nodes[key][1], self.known_dynamic_nodes[key][2], self.known_dynamic_nodes[key][3], self.known_dynamic_nodes[key][4]]
                    report.append(dev_info)
            for key in self.known_static_nodes:
                if self.known_static_nodes[key][0] is True:
                    self.known_static_nodes[key][0] = False
                    dev_info = ["S", key, self.known_static_nodes[key][1], self.known_static_nodes[key][2], self.known_static_nodes[key][3], self.known_static_nodes[key][4]]
                    report.append(dev_info)

            report_creation_time = self.env.now
            if self.static is False:
                type = "M"
            else:
                type = "S"
            self.network.send_report_to_server(type, self.id, report, report_creation_time)
            delta = 0
            yield self.env.timeout(1000 + delta)