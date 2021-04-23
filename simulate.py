import device
import network
import simpy

print("Begin")

env = simpy.Environment()
network = network.Network()

dev_a = device.Device(env, "dev_a")
# dev_b = device.Device(env, "dev_b")
# dev_c = device.Device(env, "dev_c")

network.register_device(dev_a)
# network.register_device(dev_b)
# network.register_device(dev_c)

env.run(1000)