from cgitb import small
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
        self.network = None
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
        
        self.correct_distance_classification_before_triangle = 0
        self.wrong_distance_classification_before_triangle = 0
        self.correct_distance_classification_after_triangle = 0
        self.wrong_distance_classification_after_triangle = 0
        # self.dict_dev = dict_dev
        self.max_age_of_measurement = int(self.conf["max_age_of_measurement"])
        self.packet_loss_probability = float(self.conf["packet_loss_probability"])
        # self.mes = [{[None for x in range(mes_dimension)]} for y in range(mes_dimension)]
        self.mes = {}
        self.env.process(self.transmit_ADV())
        # self.env.process(self.mesh_correction())
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
                else:
                    self.delta_x = 0.0
                    self.delta_y = 0.0

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
            
            #mesh - finding the lost neighbour - begin
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
            #mesh - finding the lost neighbour - end


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
        if neighbour is True:
            if (real_dist < 5 and calculated_dist < 5.0) or (real_dist >= 5 and calculated_dist >= 5.0):
                self.correct_distance_classification_neighbour += 1
            else:
                # print(real_dist, calculated_dist)
                self.wrong_distance_classification_neighbour += 1
    
    def mesh_correction(self):
        while True: 
            self.triangle_correction_eval(before=True)
            # self.triangle_correction()
            # self.triangle_correction_eval(after=True)
            # print(self.id_typed, self.env.now)
            yield self.env.timeout(100)
    
    def triangle_correction_eval(self, before=False, after=False):
        all_ids = []
        for key1, val1 in self.mes.items():
            if key1 not in all_ids:
                all_ids.append(key1)
            for key2 in val1:
                if key2 not in all_ids:
                    all_ids.append(key2)
        all_ids.sort()
        id1 = self.id_typed
        for id2 in all_ids:
            if id2 != id1:
                ids1_2 = [id1, id2]
                ids1_2.sort()
                if ids1_2[0] in self.mes:
                    if ids1_2[1] in self.mes[ids1_2[0]]:
                        dist1_2 = self.mes[ids1_2[0]][ids1_2[1]][0]
                        real_dist = math.hypot(self.x - self.network.dictionary_devices[id2].x, self.y - self.network.dictionary_devices[id2].y)
                        # print(ids1_2, dist1_2, id2, real_dist)
                        if (real_dist < 5 and dist1_2 < 5.0) or (real_dist >= 5 and dist1_2 >= 5.0):
                            if before:
                                self.correct_distance_classification_before_triangle += 1
                            if after:
                                self.correct_distance_classification_after_triangle += 1
                        else:
                            if before:
                                self.wrong_distance_classification_before_triangle += 1
                            if after:
                                self.wrong_distance_classification_after_triangle += 1

                        
                        

        
        
    
    def triangle_correction(self):
        all_ids = []
        for key1, val1 in self.mes.items():
            if key1 not in all_ids:
                all_ids.append(key1)
            for key2 in val1:
                if key2 not in all_ids:
                    all_ids.append(key2)
        all_ids.sort()
        
        triangle_list = []
        id1 = self.id_typed
        for id2 in all_ids:
            if id2 != id1:
                ids1_2 = [id1, id2]
                ids1_2.sort()
                if ids1_2[0] in self.mes:
                    if ids1_2[1] in self.mes[ids1_2[0]]:
                        #pierwszy bok ids1_2
                        for id3 in all_ids:
                            if id3 != id2 and id3 != id1:
                                ids2_3 = [id2, id3]
                                ids2_3.sort()
                                if ids2_3[0] in self.mes:
                                    if ids2_3[1] in self.mes[ids2_3[0]]:
                                        #drugi bok ids2_3
                                        ids3_1 = [id3, id1]
                                        ids3_1.sort()
                                        if ids3_1[0] in self.mes:
                                            if ids3_1[1] in self.mes[ids3_1[0]]:
                                                #trzeci bok ids3_1
                                                # print(ids1_2, ids2_3, ids3_1)
                                                dist1_2 = self.mes[ids1_2[0]][ids1_2[1]][0]
                                                dist2_3 = self.mes[ids2_3[0]][ids2_3[1]][0]
                                                dist3_1 = self.mes[ids3_1[0]][ids3_1[1]][0]
                                                dists = [dist1_2, dist2_3, dist3_1]
                                                dists.sort()
                                                if dists[0] + dists[1] < dists[2]: #zle trojkaty
                                                    ids = [ids1_2, ids2_3, ids3_1]
                                                    ids.sort()
                                                    if ids not in triangle_list:
                                                        triangle_list.append( ids )
                                                        # print(ids, round(dist1_2,2), round(dist2_3,2), round(dist3_1,2))

                                                    #[dist1_2, dist2_3, dist3_1]
        triangle_list.sort()
        if len(triangle_list) > 0:
            out = {}
            for line in triangle_list:
                if str(line[0]) not in out:
                    out[str(line[0])] = []
                out[str(line[0])].append(line)
            
            for key, val in out.items():
                # print(key, ":")
                biggest = True
                smallest = True
                target_bval = 9999.0
                target_mval = 0.0
                for v in val:
                    # print("\t", v)
                    dist1_2 = self.mes[v[0][0]][v[0][1]][0]
                    dist2_3 = self.mes[v[1][0]][v[1][1]][0]
                    dist3_1 = self.mes[v[2][0]][v[2][1]][0]
                    if dist1_2 > dist2_3 or dist1_2 > dist3_1:
                        smallest = False
                    else:
                        if target_mval < abs(dist2_3 - dist3_1):
                            target_mval = abs(dist2_3 - dist3_1)
                    if dist1_2 < dist2_3 or dist1_2 < dist3_1:
                        biggest = False
                    else:
                        if target_bval > dist2_3 + dist3_1:
                            target_bval = dist2_3 + dist3_1
                    # print("\t", round(dist1_2,2),"\t\t", round(dist2_3,2),"\t\t", round(dist3_1,2))
                if biggest:
                    self.mes[val[0][0][0]][val[0][0][1]][0] = target_bval-0.01
                    # print("\t", "biggest", val[0][0][0], val[0][0][1], self.mes[val[0][0][0]][val[0][0][1]][0] )
                if smallest:
                    self.mes[val[0][0][0]][val[0][0][1]][0] = target_mval+0.01
                    # print("\t", "smallest", val[0][0][0], val[0][0][1], self.mes[val[0][0][0]][val[0][0][1]][0] ) 
                # print("\n")   
                    
            
            
