import server
import network
import simpy
import matplotlib.pyplot as plt
import configparser

config = configparser.ConfigParser()
config.read('config')
conf = config['timbit']

realTime = conf.getboolean('realtime')

number_of_devices = [1]
capacity = [1, 2, 3, 4, 5]
for cap in capacity:
    for nod in number_of_devices:
        print(nod, cap)
        if realTime is False:
            env = simpy.Environment()
        else:
            env = simpy.RealtimeEnvironment(initial_time=0, factor=0.001, strict=False)

        net = network.Network(env)

        srv = server.Server(env, capacity=cap)
        net.add_server(srv)

        for i in range(nod):
            net.add_mobile_node(i)

        for i in range(0):
            net.add_static_node(i)

        # 1h        is 3600000  ms
        # 10min     is 600000   ms
        # 5min      is 300000   ms

        if realTime is False:
            env.run(30000)
        else:
            env.run()

        plt.figure()
        plt.hist(srv.queueing_time, density=False, bins=30)
        plt.suptitle('Number or nodes ' + str(len(net.static_devices) + len(net.mobile_devices)))
        plt.xlabel('Queueing time [ms]')
        plt.ylabel('Number of events')
        plt.title("Capacity " + str(cap))
        plt.savefig(str(nod) + "_" + str(cap) + '_histogram.png')
        plt.close()

        x = []
        y = []

        for key in srv.queue_length:
            x.append(key)
            y.append(srv.queue_length[key])

        plt.figure()
        plt.suptitle('Number or nodes ' + str(len(net.static_devices) + len(net.mobile_devices)))
        plt.xlabel('Simulation time')
        plt.ylabel('Queue length')
        plt.title("Capacity " + str(cap))
        plt.scatter(x, y)
        plt.savefig(str(nod) + "_" + str(cap) + "_queue_length.png")
        plt.close()