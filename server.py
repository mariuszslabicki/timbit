import simpy
import time

class Server(object):
    def __init__(self, env, capacity = 1, server_responses_on = False):
        self.start = time.perf_counter()
        self.env = env
        self.server_processing_capacity = capacity
        self.q1 = simpy.Resource(env, capacity=capacity)
        self.queueing_time = []
        self.processing_time = []
        self.queue_length = {}
        self.responses_on = server_responses_on

    def receive_report(self, nodeType, id, report, creationTime):
        # print(self.env.now, "Server received report")
        # end = time.perf_counter()
        # print("RealTime", end - self.start)
        # print(self.env.now, "Received report from device", nodeType, id)
        # if len(report) > 0:
            # for entry in report:
                # print("Type", entry[0], "Dev:", entry[1], "\t measuredD:", entry[2], "\t lastRealD:", entry[3], "\t lastRealX:", entry[4], "\t lastRealY:", entry[5])
        # else:
            # print("Received empty report")
        self.env.process(self.process_report(nodeType, id, report, creationTime))
    
    def send_report(self, nodeType, id, creationTime):
        # print(self.env.now, "Server sending reponse now")
        self.network.send_response_to_device(nodeType, id, creationTime)

    def process_report(self, nodeType, id, report, creationTime):
        with self.q1.request() as process_report:
            yield process_report
            self.queueing_time.append(self.env.now - creationTime)
            # print("Time from report creation to processing was", self.env.now - creationTime)
            self.queue_length[self.env.now] = len(self.q1.queue)
            timeout = 10 + 2 * (self.server_processing_capacity - 1)
            yield self.env.timeout(timeout)
            if self.responses_on is True:
                self.send_report(nodeType, id, creationTime)
