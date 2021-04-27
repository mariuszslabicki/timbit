import simpy

class Server(object):
    def __init__(self, env):
        self.env = env
        self.q1 = simpy.Resource(env, capacity=1)
        self.queueing_time = []
        self.processing_time = []

    def receive_report(self):
        print(self.env.now, "Server: I have received report")
        self.env.process(self.process_message())
        print(self.env.now, "Server: Done")

    def process_message(self):
        print(self.env.now, "Server: waiting for queue")
        with self.q1.request() as process_report:
            print(self.env.now, "Server: start queueing")
            queueing_start = self.env.now
            yield process_report
            self.queueing_time.append(self.env.now - queueing_start)
            print(self.env.now, "Server: start processing")
            yield self.env.timeout(10)
        print(self.env.now, "Server: finished processing")
