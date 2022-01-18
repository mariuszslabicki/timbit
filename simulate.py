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
    
# print("queueing_time", net.server.queueing_time)
# print("processing_time", net.server.processing_time)
