import simpy
import time

class Server(object):
    def __init__(self, env):
        self.start = time.perf_counter()
        self.env = env
        self.q1 = simpy.Resource(env, capacity=1)
        self.queueing_time = []
        self.processing_time = []

    def receive_report(self, nodeType, id, report, creationTime):
        end = time.perf_counter()
        print("RealTime", end - self.start)
        print(self.env.now, "Received report from device", nodeType, id)
        if len(report) > 0:
            for entry in report:
                print("Type", entry[0], "Dev:", entry[1], "\t measuredD:", entry[2], "\t lastRealD:", entry[3], "\t lastRealX:", entry[4], "\t lastRealY:", entry[5])
        else:
            print("Received empty report")
        self.env.process(self.process_report(report, creationTime))

    def process_report(self, report, creationTime):
        with self.q1.request() as process_report:
            yield process_report
            self.queueing_time.append(self.env.now - creationTime)
            print("Time from report creation to processing was", self.env.now - creationTime)
            yield self.env.timeout(10)
