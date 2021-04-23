import device
import network
import simpy

print("Begin")

env = simpy.Environment()
network = network.Network()

dev_a = device.Device(env)

network.add_in_random_position(dev_a)

env.run(1000)