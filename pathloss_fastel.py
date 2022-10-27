import numpy as np
import math
import random

class PathlossCalculator(object):
    def __init__(self, no_of_shifts = 8):
        self.no_of_shifts = no_of_shifts
        self.shifts = np.zeros(no_of_shifts)
        for i in range(no_of_shifts):
            self.shifts = i

    def return_base_el1(self, x_a, y_a, x_b, y_b):
        distance = math.hypot(x_a - x_b, y_a - y_b)
        if distance == 0:
            distance = 1
        free_space_path_loss = -67.580939 + 10 * (-1.78691694) * math.log10(distance/5)
        return free_space_path_loss

    def return_shift_el2(self, x_a, y_a, x_b, y_b):
        distance = math.hypot(x_a - x_b, y_a - y_b)
        if distance == 0:
            distance = 1
        hash_val = hash((x_a, y_a, x_b, y_b)) % self.no_of_shifts
        base = -67.580939 + 10 * (-1.78691694) * math.log10(distance/5)
        if hash_val == 0:
            per_test = -69.29690794096979 + 10 * (-1.50561351) * math.log10(distance/5)
            shift = per_test - base
        if hash_val == 1:
            per_test = -67.01127675840979 + 10 * (-1.7242235) * math.log10(distance/5)
            shift = per_test - base
        if hash_val == 2:
            per_test = -67.01127675840979 + 10 * (-1.97650906) * math.log10(distance/5)
            shift = per_test - base
        if hash_val == 3:
            per_test = -63.31364902506964 + 10 * (-1.7284497) * math.log10(distance/5)
            shift = per_test - base
        if hash_val == 4:
            per_test = -71.62839356735259 + 10 * (-0.96362623) * math.log10(distance/5)
            shift = per_test - base
        if hash_val == 5:
            per_test = -68.53537852548243 + 10 * (-2.35421553) * math.log10(distance/5)
            shift = per_test - base
        if hash_val == 6:
            per_test = -69.40521376433786 + 10 * (-2.49415982) * math.log10(distance/5)
            shift = per_test - base
        if hash_val == 7:
            per_test = -65.13406881077039 + 10 * (-2.64404849) * math.log10(distance/5)
            shift = per_test - base

        return shift

    def return_variance_el3(self, x_a, y_a, x_b, y_b):
        variance = random.normalvariate(0, 5)
        return variance

    def return_pathloss(self, x_a, y_a, x_b, y_b):
        x_a_floor = np.floor(x_a)
        y_a_floor = np.floor(y_a)
        x_b_floor = np.floor(x_b)
        y_b_floor = np.floor(y_b)
        el1_loss = self.return_base_el1(x_a_floor, y_a_floor, x_b_floor, y_b_floor)
        el2_loss = self.return_shift_el2(x_a_floor, y_a_floor, x_b_floor, y_b_floor)
        el3_loss = self.return_variance_el3(x_a_floor, y_a_floor, x_b_floor, y_b_floor)
        pathloss = el1_loss + el2_loss + el3_loss
        return pathloss