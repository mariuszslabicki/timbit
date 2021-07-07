import device
import server
import network
import simpy

realTime = False

if realTime is False:
    env = simpy.Environment()
else:
    env = simpy.RealtimeEnvironment(initial_time=0, factor=0.001, strict=False)

network = network.Network(env)

srv = server.Server(env)
network.add_server(srv)

for i in range(100):
    network.add_in_random_position(device.Device(env, i))

# 1h        is 3600000  ms
# 10min     is 600000   ms
# 5min      is 300000   ms

if realTime is False:
    env.run(30000)

else:
    env.run()

print(srv.queueing_time)