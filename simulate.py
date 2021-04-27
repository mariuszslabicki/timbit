import device
import server
import network
import simpy

print("Begin")

env = simpy.Environment()
network = network.Network(env)

srv = server.Server(env)
network.add_server(srv)

dev_a = device.Device(env)
dev_b = device.Device(env)
network.add_in_random_position(dev_a)
network.add_in_random_position(dev_b)

network.devices[0].x = 10
network.devices[0].y = 10
network.devices[1].x = 11
network.devices[1].y = 11

env.run(1000)

print(network.server.queueing_time)