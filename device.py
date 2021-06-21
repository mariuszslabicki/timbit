import random
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
        self.tx_power = 0 #dBm
        self.sensitivity = -95 #dBm
        self.receided_ADV = {}
        self.env.process(self.transmit_ADV())
        self.env.process(self.keep_moving())
        self.env.process(self.perform_server_report())

    def transmit_ADV(self):
        while True:
            self.network.propagate_ADV(self)
            random_shift = random.randint(0, 10)
            yield self.env.timeout(250 + random_shift)

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

    def receive_ADV(self, sender, path_loss, distance):
        if sender.tx_power - path_loss > self.sensitivity:
            if sender.id not in self.receided_ADV:
                self.receided_ADV[sender.id] = [[sender.tx_power - path_loss], [distance]]
            else:
                self.receided_ADV[sender.id][0].append(sender.tx_power - path_loss)
                self.receided_ADV[sender.id][1].append(distance)
        

    def perform_server_report(self):
        delta = random.randint(0, 1000)
        yield self.env.timeout(delta)
        while True:
            # print("Wysylam report")
            # print(self.receided_ADV)
            report = []
            for key in self.receided_ADV:
                report.append(key)
                report.append(self.receided_ADV[key][0])
                report.append(self.receided_ADV[key][1])

            self.network.send_report_to_server(self.id, report)
            self.receided_ADV = {}
            delta = random.randint(0, 1000)
            yield self.env.timeout(5000 + delta)