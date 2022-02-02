import server
import network
import simpy
import matplotlib.pyplot as plt
import configparser

config = configparser.ConfigParser()
config.read('config')
conf = config['timbit']

realTime = conf.getboolean('realtime_processing')

if realTime is False:
    env = simpy.Environment()
else:
    env = simpy.RealtimeEnvironment(initial_time=0, factor=0.001, strict=False)

pathloss_model = conf.get('pathloss_model')

net = network.Network(env, conf, pathloss_model)

srv = server.Server(env, capacity=int(conf["server_processing_capacity"]))
net.add_server(srv)

for i in range(int(conf["number_of_mobile_dev"])):
    net.add_mobile_node(i)

for i in range(int(conf["number_of_static_dev"])):
    net.add_static_node(i)

if realTime is False:
    env.run(conf["simulation_time"])
else:
    env.run()

correct_distance_classification_sum = 0
wrong_distance_classification_sum = 0
for dev in net.mobile_devices:
    correct_distance_classification_sum += dev.correct_distance_classification
    wrong_distance_classification_sum += dev.wrong_distance_classification
for dev in net.static_devices:
    correct_distance_classification_sum += dev.correct_distance_classification
    wrong_distance_classification_sum += dev.wrong_distance_classification

print ("Simple: ")
print ("Correct classification:", correct_distance_classification_sum, "Wrong classificaton:", wrong_distance_classification_sum)
print ("Correct %:",  correct_distance_classification_sum /  (correct_distance_classification_sum + wrong_distance_classification_sum) * 100.0)

correct_distance_classification_sum = 0
wrong_distance_classification_sum = 0
for dev in net.mobile_devices:
    correct_distance_classification_sum += dev.correct_distance_classification_improved
    wrong_distance_classification_sum += dev.wrong_distance_classification_improved
for dev in net.static_devices:
    correct_distance_classification_sum += dev.correct_distance_classification_improved
    wrong_distance_classification_sum += dev.wrong_distance_classification_improved


print ("Improved: ")
print ("Correct classification:", correct_distance_classification_sum, "Wrong classificaton:", wrong_distance_classification_sum)
print ("Correct %:",  correct_distance_classification_sum /  (correct_distance_classification_sum + wrong_distance_classification_sum) * 100.0)


correct_distance_classification_sum = 0
wrong_distance_classification_sum = 0
correct_distance_classification_neighbour_sum = 0
wrong_distance_classification_neighbour_sum = 0
for dev in net.mobile_devices:
    correct_distance_classification_sum += dev.correct_distance_classification_improved
    wrong_distance_classification_sum += dev.wrong_distance_classification_improved
    correct_distance_classification_neighbour_sum += dev.correct_distance_classification_neighbour
    wrong_distance_classification_neighbour_sum += dev.wrong_distance_classification_neighbour
for dev in net.static_devices:
    correct_distance_classification_sum += dev.correct_distance_classification_improved
    wrong_distance_classification_sum += dev.wrong_distance_classification_improved
    correct_distance_classification_neighbour_sum += dev.correct_distance_classification_neighbour
    wrong_distance_classification_neighbour_sum += dev.wrong_distance_classification_neighbour


print ("Improved + neighbour detection: ")
print ("Correct classification:", correct_distance_classification_sum, "Wrong classificaton:", wrong_distance_classification_sum)
print ("Correct classification neighbour:", correct_distance_classification_neighbour_sum, "Wrong classificaton neighbour:", wrong_distance_classification_neighbour_sum)

print ("Correct %:",  (correct_distance_classification_sum + correct_distance_classification_neighbour_sum) /  (correct_distance_classification_sum + wrong_distance_classification_sum + correct_distance_classification_neighbour_sum + wrong_distance_classification_neighbour_sum) * 100.0)


# print("queueing_time", net.server.queueing_time)
# print("processing_time", net.server.processing_time)
