import simpy

class Server(object):
    def __init__(self, env):
        self.env = env
        self.q1 = simpy.Resource(env, capacity=1)
        self.queueing_time = []
        self.processing_time = []

    def receive_report(self, id, report):
        print(self.env.now, "Received report from device", id)
        print(report)
        self.env.process(self.process_report(report))

    def process_report(self, report):
        with self.q1.request() as process_report:
            queueing_start = self.env.now
            yield process_report
            self.queueing_time.append(self.env.now - queueing_start)
            yield self.env.timeout(10)
