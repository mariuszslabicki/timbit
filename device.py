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
        self.tx_power = 13  # dBm
        self.sensitivity = -95  # dBm
        self.known_static_nodes = {}
        self.known_dynamic_nodes = {}
        self.conf = config
        self.correct_distance_classification = 0
        self.wrong_distance_classification = 0
        self.correct_distance_classification_improved = 0
        self.wrong_distance_classification_improved = 0
        self.correct_distance_classification_neighbour = 0
        self.wrong_distance_classification_neighbour = 0
        self.max_age_of_measurement = int(self.conf["max_age_of_measurement"])
        self.packet_loss_probability = float(
            self.conf["packet_loss_probability"])
        # self.mes = [{[None for x in range(mes_dimension)]} for y in range(mes_dimension)]
        self.mes = {}
        self.env.process(self.transmit_ADV())
        self.env.process(self.perform_server_report())
        if self.static is False:
            self.env.process(self.keep_moving())
            self.id_typed = str(self.id)+'D'
            # self.mes[self.id_typed] = {}
            self.WP_x = None
            self.WP_y = None
        else:
            self.id_typed = str(self.id)+'S'
            # self.mes[self.id_typed] = {}

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
            location_update_interval = int(
                self.conf["location_update_interval"])
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
                if self.steps_to_WP != 0:
                    self.delta_x = (self.WP_x - self.x) / self.steps_to_WP
                    self.delta_y = (self.WP_y - self.y) / self.steps_to_WP

            yield self.env.timeout(location_update_interval)
            self.make_a_step()

    def make_a_step(self):
        self.x += self.delta_x
        self.y += self.delta_y
        self.steps_to_WP -= 1

    def receive_ADV(self, sender, RSSI, distance):
        calculated_dist = 0.0261 * math.pow(RSSI, 2) + 3.4324 * RSSI + 113.64
        if (RSSI > self.sensitivity) and (random.uniform(0, 1) > self.packet_loss_probability):
            sender_id_typed = str(sender.id)+'U'
            if sender.static is False:
                sender_id_typed = str(sender.id)+'D'
                if sender.id not in self.known_dynamic_nodes:
                    self.known_dynamic_nodes[sender.id] = [
                        True, calculated_dist, distance, sender.x, sender.y]
                else:
                    self.known_dynamic_nodes[sender.id][0] = True
                    self.known_dynamic_nodes[sender.id][1] += 0.5 * (calculated_dist - self.known_dynamic_nodes[sender.id][1])
                    self.known_dynamic_nodes[sender.id][2] = distance
                    self.known_dynamic_nodes[sender.id][3] = sender.x
                    self.known_dynamic_nodes[sender.id][4] = sender.y
            if sender.static is True:
                sender_id_typed = str(sender.id)+'S'
                if sender.id not in self.known_static_nodes:
                    self.known_static_nodes[sender.id] = [True, calculated_dist, distance, sender.x, sender.y]
                else:
                    self.known_static_nodes[sender.id][0] = True
                    self.known_static_nodes[sender.id][1] += 0.5 * (calculated_dist - self.known_static_nodes[sender.id][1])
                    self.known_static_nodes[sender.id][2] = distance
                    self.known_static_nodes[sender.id][3] = sender.x
                    self.known_static_nodes[sender.id][4] = sender.y

            # mesh - direct neighbour - begin
            ids = [sender_id_typed, self.id_typed]
            ids.sort()
            if ids[0] not in self.mes:
                self.mes[ids[0]] = {}
            if ids[1] in self.mes[ids[0]]:
                old_val = self.mes[ids[0]][ids[1]][0]
                self.mes[ids[0]][ids[1]] = [((0.5 * old_val) + calculated_dist) / 1.5, self.env.now]
            else:
                self.mes[ids[0]][ids[1]] = [calculated_dist, self.env.now]
            # mesh - direct neighbour - eng

            # mesh - neighbours of neighbour - begin
            for neighbour_id in sender.known_static_nodes.keys():
                ids = [sender_id_typed, str(neighbour_id)+'S']
                ids.sort()
                if ids[0] not in self.mes:
                    self.mes[ids[0]] = {}
                if ids[1] in self.mes[ids[0]]:
                    old_val = self.mes[ids[0]][ids[1]][0]
                    self.mes[ids[0]][ids[1]] = [((0.5 * old_val) + sender.known_static_nodes[neighbour_id][2]) / 1.5, self.env.now]
                else:
                    self.mes[ids[0]][ids[1]] = [sender.known_static_nodes[neighbour_id][2], self.env.now]
                    
            for neighbour_id in sender.known_dynamic_nodes.keys():
                ids = [sender_id_typed, str(neighbour_id)+'D']
                ids.sort()
                if ids[0] not in self.mes:
                    self.mes[ids[0]] = {}
                if ids[1] in self.mes[ids[0]]:
                    old_val = self.mes[ids[0]][ids[1]][0]
                    self.mes[ids[0]][ids[1]] = [((0.5 * old_val) + sender.known_dynamic_nodes[neighbour_id][2]) / 1.5, self.env.now]
                else:
                    self.mes[ids[0]][ids[1]] = [sender.known_dynamic_nodes[neighbour_id][2], self.env.now]
            # mesh - neighbours of neighbour - end

            self.make_distance_classification(sender, calculated_dist)
        else:
            sender_id_typed = str(sender.id)+'U'
            if sender.static is False:
                sender_id_typed = str(sender.id)+'D'
            if sender.static is True:
                sender_id_typed = str(sender.id)+'S'

            my_neighbours = []
            if self.id_typed in self.mes:
                for key in self.mes[self.id_typed]:
                    if key != sender_id_typed:
                        my_neighbours.append(key)
            for key1, val1 in self.mes.items():
                if self.id_typed in val1 and key1 not in my_neighbours:
                    if key1 != sender_id_typed:
                        my_neighbours.append(key1)
            
            for mn in my_neighbours:
                ids = [self.id_typed, mn]
                ids.sort()
                if self.mes[ids[0]][ids[1]][0] < 5.0:
                    idsn = [mn, sender_id_typed]
                    if idsn[0] in self.mes:
                        if idsn[1] in self.mes[idsn[0]]:
                            if self.mes[ids[0]][ids[1]][0] + self.mes[idsn[0]][idsn[1]][0] < 5.0:
                                # print("\n", "Jestem:", self.id_typed, ", utracilem od:", sender_id_typed, ", obliczony dystans od RSSI: ", calculated_dist)
                                # print("do sasiada:", mn, "jest:", self.mes[ids[0]][ids[1]][0], "(", ids[0], ids[1] ,")", "a od niego do", sender_id_typed, "jest", self.mes[idsn[0]][idsn[1]][0], "(", idsn[0], idsn[1] ,")",)
                                self.make_distance_classification(sender, self.mes[ids[0]][ids[1]][0] + self.mes[idsn[0]][idsn[1]][0], True)
        self.calculate_distance_in_triangle()

    def perform_server_report(self):
        delta = random.randint(0, 1000)
        yield self.env.timeout(delta)
        while True:
            # remove old mesh nodes - begin
            for tdevs in self.mes.values():
                to_delete = []
                for tdev, values in tdevs.items():
                    if self.env.now - values[1] > self.max_age_of_measurement:
                        to_delete.append(tdev)
                for tdev in to_delete:
                    del tdevs[tdev]
                del to_delete
            # remove old mesh nodes - end
            report = []
            for key in self.known_dynamic_nodes:
                if self.known_dynamic_nodes[key][0] is True:
                    self.known_dynamic_nodes[key][0] = False
                    dev_info = ["D", key, self.known_dynamic_nodes[key][1], self.known_dynamic_nodes[key]
                                [2], self.known_dynamic_nodes[key][3], self.known_dynamic_nodes[key][4]]
                    report.append(dev_info)
            for key in self.known_static_nodes:
                if self.known_static_nodes[key][0] is True:
                    self.known_static_nodes[key][0] = False
                    dev_info = ["S", key, self.known_static_nodes[key][1], self.known_static_nodes[key]
                                [2], self.known_static_nodes[key][3], self.known_static_nodes[key][4]]
                    report.append(dev_info)

            report_creation_time = self.env.now
            if self.static is False:
                type = "D"
            else:
                type = "S"
            self.network.send_report_to_server(
                type, self.id, report, report_creation_time, self.mes)
            delta = 0
            yield self.env.timeout(1000 + delta)

    def make_distance_classification(self, sender, calculated_dist, neighbour=False):
        real_dist = round(math.sqrt((sender.x-self.x) **
                          2 + (sender.y-self.y)**2), 2)
        sender_id_typed = str(sender.id)+'U'
        if sender.static is False:
            sender_id_typed = str(sender.id)+'D'
        else:
            sender_id_typed = str(sender.id)+'S'

        if neighbour is False:
            if (real_dist < 5 and calculated_dist < 5.0) or (real_dist >= 5.0 and calculated_dist >= 5.0):
                self.correct_distance_classification += 1
            else:
                self.wrong_distance_classification += 1

            ids = [self.id_typed, sender_id_typed]
            ids.sort()
            calculated_dist_improved = self.mes[ids[0]][ids[1]][0]

            if (real_dist < 5 and calculated_dist_improved < 5.0) or (real_dist >= 5.0 and calculated_dist_improved >= 5.0):
                self.correct_distance_classification_improved += 1
            else:
                self.wrong_distance_classification_improved += 1
        else:
            if (real_dist < 5 and calculated_dist < 5.0) or (real_dist >= 5 and calculated_dist >= 5.0):
                self.correct_distance_classification_neighbour += 1
            else:
                # print(real_dist, calculated_dist)
                self.wrong_distance_classification_neighbour += 1

    def calculate_distance_in_triangle(self):
        triangle_list = []
        # print("++++++++++++++++++++++++++++++++++++++++++++\n", self.id_typed)
        for first_id, first_dist in self.mes[self.id_typed].items():
            # print("\t", first_id, "\t", first_dist)
            if first_id in self.mes:
                for sec_id, sec_dist in self.mes[first_id].items():
                    if sec_id in self.mes:
                        if self.id_typed in self.mes[sec_id]:
                            distances = [first_dist[0], sec_dist[0],
                                         self.mes[sec_id][self.id_typed][0]]
                            distances.sort()
                            if (distances[0] + distances[1] < distances[2]):
                                triangle_list.append(self.id_typed + "---(" + str(round(first_dist[0], 2)) + ")--->" + first_id + "---(" + str(round(
                                    sec_dist[0], 2)) + ")--->" + sec_id + "---(" + str(round(self.mes[sec_id][self.id_typed][0], 2)) + ")--->" + self.id_typed + " = ERROR")
                            else:
                                triangle_list.append(self.id_typed + "---(" + str(round(first_dist[0], 2)) + ")--->" + first_id + "---(" + str(round(
                                    sec_dist[0], 2)) + ")--->" + sec_id + "---(" + str(round(self.mes[sec_id][self.id_typed][0], 2)) + ")--->" + self.id_typed)

        if len(triangle_list) > 0:
            for line in triangle_list:
                print(line)
        print("")
