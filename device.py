import random
import math
import simpy

class Device(object):
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.x = None
        self.y = None
        self.x_limit = None
        self.y_limit = None
        self.steps_to_WP = 0
        self.tx_power = 13 #dBm
        self.sensitivity = -95 #dBm
        self.known_devices = {}
        self.env.process(self.transmit_ADV())
        self.env.process(self.keep_moving())
        self.env.process(self.perform_server_report())

    def transmit_ADV(self):
        while True:
            self.network.propagate_ADV(self)
            random_shift = random.randint(0, 10)
            yield self.env.timeout(100 + random_shift)

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

    def make_a_move(self):
        self.x += self.delta_x
        self.y += self.delta_y
        self.steps_to_WP -= 1

    def receive_ADV(self, sender, RSSI, distance):
        if RSSI > self.sensitivity:
            calculated_dist = 0.0261 * math.pow(RSSI, 2) + 3.4324 * RSSI + 113.64
            if sender.id not in self.known_devices:
                self.known_devices[sender.id] = [calculated_dist, distance]
            else:
                self.known_devices[sender.id][0] += 0.5 * (calculated_dist - self.known_devices[sender.id][0])
                self.known_devices[sender.id][1] = distance
        

    def perform_server_report(self):
        delta = random.randint(0, 1000)
        yield self.env.timeout(delta)
        while True:
            report = []
            for key in self.known_devices:
                dev_info = [key, self.known_devices[key][0], self.known_devices[key][1]]
                report.append(dev_info)

            report_creation_time = self.env.now
            self.network.send_report_to_server(self.id, report, report_creation_time)
            delta = 0
            yield self.env.timeout(1000 + delta)