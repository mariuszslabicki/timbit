import server
import network
import simpy

realTime = True

if realTime is False:
    env = simpy.Environment()
else:
    env = simpy.RealtimeEnvironment(initial_time=0, factor=0.001, strict=False)

network = network.Network(env)

srv = server.Server(env)
network.add_server(srv)

for i in range(5):
    network.add_mobile_node(i)

for i in range(1):
    network.add_static_node(i)

# 1h        is 3600000  ms
# 10min     is 600000   ms
# 5min      is 300000   ms

if realTime is False:
    env.run(30000)

else:
    env.run()

print(srv.queueing_time)