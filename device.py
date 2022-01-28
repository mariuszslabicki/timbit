import random
import math
import simpy

class Device(object):
    def __init__(self, env, id, config, mes_dimension, static=False):
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
        self.correct_distance_classification = 0
        self.wrong_distance_classification = 0        
        self.correct_distance_classification_improved = 0
        self.wrong_distance_classification_improved = 0
        self.max_age_of_measurement = int(self.conf["max_age_of_measurement"])
        self.packet_loss_probability = float(self.conf["packet_loss_probability"])
        # self.mes = [{[None for x in range(mes_dimension)]} for y in range(mes_dimension)] 
        self.mes = {}
        self.env.process(self.transmit_ADV())
        self.env.process(self.perform_server_report())
        if self.static is False:
            self.env.process(self.keep_moving())
            self.id_typed = str(self.id)+'D'
            self.mes[self.id_typed] = {}
            self.WP_x = None
            self.WP_y = None
        else:
            self.id_typed = str(self.id)+'S'
            self.mes[self.id_typed] = {}
            

    def transmit_ADV(self):
        while True:
            # print(self.env.now, "ID:", self.id, end=" ")
            # if self.static:
            #     print("static")
            # else:
            #     print("dynamic")
            # print(self.known_dynamic_nodes, end="\n\n\n")
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
                last_x = self.WP_x
                last_y = self.WP_y
                while last_x == self.WP_x and last_y == self.WP_y:
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
            if random.uniform(0,1) > self.packet_loss_probability:
                id_typed = str(sender.id)+'U'
                if sender.static is False:
                    id_typed = str(sender.id)+'D'
                    if sender.id not in self.known_dynamic_nodes:
                        self.known_dynamic_nodes[sender.id] = [True, calculated_dist, distance, sender.x, sender.y]
                    else:
                        self.known_dynamic_nodes[sender.id][0] = True
                        self.known_dynamic_nodes[sender.id][1] += 0.5 * (calculated_dist - self.known_dynamic_nodes[sender.id][1])
                        self.known_dynamic_nodes[sender.id][2] = distance
                        self.known_dynamic_nodes[sender.id][3] = sender.x
                        self.known_dynamic_nodes[sender.id][4] = sender.y
                if sender.static is True:
                    id_typed = str(sender.id)+'S'
                    if sender.id not in self.known_static_nodes:
                        self.known_static_nodes[sender.id] = [True, calculated_dist, distance, sender.x, sender.y]
                    else:
                        self.known_static_nodes[sender.id][0] = True
                        self.known_static_nodes[sender.id][1] += 0.5 * (calculated_dist - self.known_static_nodes[sender.id][1])
                        self.known_static_nodes[sender.id][2] = distance
                        self.known_static_nodes[sender.id][3] = sender.x
                        self.known_static_nodes[sender.id][4] = sender.y
                if id_typed in self.mes[self.id_typed]:
                    old_val = self.mes[self.id_typed][id_typed][0]
                    self.mes[self.id_typed][id_typed] = [((0.5 * old_val) + calculated_dist) / 1.5, self.env.now]
                else:
                    self.mes[self.id_typed][id_typed] = [calculated_dist, self.env.now]
                if id_typed not in self.mes:
                    self.mes[id_typed] = {}
                for neighbour_id in sender.known_static_nodes.keys():
                    if str(neighbour_id)+'S' in self.mes[id_typed]:
                        old_val = self.mes[id_typed][str(neighbour_id)+'S'][0]
                        self.mes[id_typed][str(neighbour_id)+'S']=[((0.5 * old_val) + sender.known_static_nodes[neighbour_id][2]) / 1.5, self.env.now]
                    else:
                        self.mes[id_typed][str(neighbour_id)+'S']=[sender.known_static_nodes[neighbour_id][2], self.env.now]
                for neighbour_id in sender.known_dynamic_nodes.keys():
                    if str(neighbour_id)+'D' in self.mes[id_typed]:
                        old_val = self.mes[id_typed][str(neighbour_id)+'D'][0]
                        self.mes[id_typed][str(neighbour_id)+'D']=[((0.5 * old_val) + sender.known_dynamic_nodes[neighbour_id][2]) / 1.5, self.env.now]
                    else:
                        self.mes[id_typed][str(neighbour_id)+'D']=[sender.known_dynamic_nodes[neighbour_id][2], self.env.now]
                self.make_distance_classification(sender, calculated_dist)

    def perform_server_report(self):
        delta = random.randint(0, 1000)
        yield self.env.timeout(delta)
        while True:
            for tdevs in self.mes.values():
                to_delete = []
                for tdev, values in tdevs.items():
                    if self.env.now - values[1] > self.max_age_of_measurement:
                        to_delete.append(tdev)
                for tdev in to_delete:
                    del tdevs[tdev]
                del to_delete
            report = []
            for key in self.known_dynamic_nodes:
                if self.known_dynamic_nodes[key][0] is True:
                    self.known_dynamic_nodes[key][0] = False
                    dev_info = ["D", key, self.known_dynamic_nodes[key][1], self.known_dynamic_nodes[key][2], self.known_dynamic_nodes[key][3], self.known_dynamic_nodes[key][4]]
                    report.append(dev_info)
            for key in self.known_static_nodes:
                if self.known_static_nodes[key][0] is True:
                    self.known_static_nodes[key][0] = False
                    dev_info = ["S", key, self.known_static_nodes[key][1], self.known_static_nodes[key][2], self.known_static_nodes[key][3], self.known_static_nodes[key][4]]
                    report.append(dev_info)

            report_creation_time = self.env.now
            if self.static is False:
                type = "D"
            else:
                type = "S"
            self.network.send_report_to_server(type, self.id, report, report_creation_time, self.mes)
            delta = 0
            yield self.env.timeout(1000 + delta)
            
    def make_distance_classification(self, sender, calculated_dist):
        real_dist = math.sqrt( (sender.x-self.x)**2 + (sender.y-self.y)**2 )
        # print("me:", self.x, self.y, "sender:", sender.x, sender.y, "real distance:", real_dist, "calculated distance:", calculated_dist)
        if (real_dist < 5 and calculated_dist < 5) or (real_dist >= 5 and calculated_dist >= 5):
            self.correct_distance_classification += 1
        else:
            self.wrong_distance_classification += 1
        
        sender_id_typed = str(sender.id)+'U'
        if sender.static is False:
            sender_id_typed = str(sender.id)+'D'
        else:
            sender_id_typed = str(sender.id)+'S'
        
        calculated_dist_improved = self.mes[self.id_typed][sender_id_typed][0]
        if sender_id_typed in self.mes:
            if self.id_typed in self.mes[sender_id_typed]:
                calculated_dist_improved += self.mes[sender_id_typed][self.id_typed][0]
                calculated_dist_improved /= 2.0
                
        if (real_dist < 5 and calculated_dist_improved < 5) or (real_dist >= 5 and calculated_dist_improved >= 5):
            self.correct_distance_classification_improved += 1
        else:
            self.wrong_distance_classification_improved += 1