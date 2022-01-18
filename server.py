import simpy
import time

class Server(object):
    def __init__(self, env, capacity = 1):
        self.start = time.perf_counter()
        self.env = env
        self.q1 = simpy.Resource(env, capacity=capacity)
        self.queueing_time = []
        self.processing_time = []
        self.queue_length = {}

    def receive_report(self, nodeType, id, report, creationTime, measurements):
        # end = time.perf_counter()
        # print("RealTime", end - self.start)
        print(self.env.now, "Received report from device", str(id)+nodeType)
        # if len(report) > 0:
        #     for entry in report:
        #         print("Type", entry[0], "Dev:", entry[1], "\t measuredD:", round(entry[2],3), "\t lastRealD:", round(entry[3],3), "\t lastRealX:", round(entry[4],3), "\t lastRealY:", round(entry[5],3))
        # else:
        #     print("Received empty report")
        for from_, targets_ in measurements.items():
            print("From "+from_, end=" to ")
            print(targets_)
        print()
        self.env.process(self.process_report(report, creationTime))

    def process_report(self, report, creationTime):
        with self.q1.request() as process_report:
            yield process_report
            self.queueing_time.append(self.env.now - creationTime)
            # print("Time from report creation to processing was", self.env.now - creationTime)
            self.queue_length[self.env.now] = len(self.q1.queue)
            yield self.env.timeout(10)
