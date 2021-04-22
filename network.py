class Network(object):
    def __init__(self):
        self.devices = []

    def register_device(self, device):
        self.devices.append(device)
        device.network = self

    def propagate_ADV(self, sender):
        print("Network: I am propagating ADV")
        for device in self.devices:
            if device == sender:
                continue
            device.receive_ADV()