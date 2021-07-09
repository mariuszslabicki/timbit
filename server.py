import simpy
import time

class Server(object):
    def __init__(self, env):
        self.start = time.perf_counter()
        self.env = env
        self.q1 = simpy.Resource(env, capacity=1)
        self.queueing_time = []
        self.processing_time = []

    def receive_report(self, id, report, creationTime):
        end = time.perf_counter()
        print("RealTime", end - self.start)
        print(self.env.now, "Received report from device", id)
        if len(report) > 0:
            for entry in report:
                print("Dev:", entry[0], "\t measuredD:", entry[1], "\t lastRealD:", entry[2])
        else:
            print("Received empty report")
        self.env.process(self.process_report(report, creationTime))

    def process_report(self, report, creationTime):
        with self.q1.request() as process_report:
            yield process_report
            self.queueing_time.append(self.env.now - creationTime)
            print("Time from report creation to processing was", self.env.now - creationTime)
            yield self.env.timeout(10)
