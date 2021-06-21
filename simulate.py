import device
import server
import network
import simpy

env = simpy.Environment()
network = network.Network(env)

srv = server.Server(env)
network.add_server(srv)

for i in range(2):
    network.add_in_random_position(device.Device(env, i))

# 1h        is 3600000  ms
# 10min     is 600000   ms
# 5min      is 300000   ms


env.run(30000)

print(network.server.queueing_time)