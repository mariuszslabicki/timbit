import numpy as np
import math
import random

class PathlossCalculator(object):
    def __init__(self, x, y, obstacle_ratio=0.2):
        self.obstacles = np.zeros((x, y))
        no_of_elements = x*y
        no_of_obstacles = math.ceil(no_of_elements * obstacle_ratio)
        for i in range(no_of_obstacles):
            obstacle_x = random.randint(0, x-1)
            obstacle_y = random.randint(0, y-1)
            obstacle_value = random.randrange(10)
            self.obstacles[obstacle_x, obstacle_y] = obstacle_value

    def return_freespace_pathloss(self, x_a, y_a, x_b, y_b):
        distance = math.hypot(x_a - x_b, y_a - y_b)
        free_space_path_loss = 20*math.log10(distance) + 20*math.log10(2400) - 27.55
        return free_space_path_loss

    def return_passed_obstacles(self, x_a, y_a, x_b, y_b):
        x_begin = math.ceil(x_a)
        y_begin = math.ceil(y_a)
        x_end = math.ceil(x_b)
        y_end = math.ceil(y_b)
        distance = math.hypot(x_begin - x_end, y_begin - y_end)
        if distance == 0:
            visited_fields = []
            return visited_fields
        x_shift = (x_end - x_begin) / distance
        y_shift = (y_end - y_begin) / distance

        x_current = x_begin
        y_current = y_begin

        visited_fields = [(math.ceil(x_current), math.ceil(y_current))]

        for step in range(math.floor(distance)+1):
            if (math.ceil(x_current), math.ceil(y_current)) != visited_fields[-1]:
                visited_fields.append((math.ceil(x_current), math.ceil(y_current)))
            x_current += x_shift
            y_current += y_shift
        return visited_fields

    def return_obstacle_pathloss(self, x_a, y_a, x_b, y_b):
        passed_obstacles = self.return_passed_obstacles(x_a, y_a, x_b, y_b)
        extra_attenuation = 0
        for obstacle in passed_obstacles:
            extra_attenuation += self.obstacles[obstacle[0], obstacle[1]]
        return extra_attenuation

    def return_pathloss(self, x_a, y_a, x_b, y_b):
        free_space_pathloss = self.return_freespace_pathloss(x_a, y_a, x_b, y_b)
        obstacless_loss = self.return_obstacle_pathloss(x_a, y_a, x_b, y_b)
        pathloss = free_space_pathloss + obstacless_loss
        return pathloss