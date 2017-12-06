# -*- coding: cp1251 -*-


# Queue of Events
class EventsQueue:
    def __init__(self):
        self.global_time = 0
        self.m_events = []
              
    def queue_size(self):
        return len(self.m_events)

    def add_event(self, m_events):
        count = len(self.m_events)
        if count == 0:            
            self.m_events.append(m_events)
            return 0            

        if m_events.e_time >= self.m_events[count - 1].e_time:
            self.m_events.append(m_events)
            return 0                                     
        
        for i in range(0, count - 1):
            if m_events.e_time >= self.m_events[i].e_time:
                if m_events.e_time < self.m_events[i + 1].e_time:
                    self.m_events.insert(i + 1, m_events)
                    return 0

    def process_next_event(self):
        if len(self.m_events) == 0:
            return 0
        self.m_events[0].execute()
        self.global_time = self.m_events[0].e_time
        del self.m_events[0]


# Discrete Event System Specification
class DEVS:
    EQ = EventsQueue()
    GlobalTime = 0.0

    def __init__(self):
        pass

    @staticmethod    
    def process_next_event():
        DEVS.EQ.process_next_event()
        DEVS.GlobalTime = DEVS.EQ.global_time

def store_file(castomers, file_name):
    #  --- store all in file  ---
    f = open(file_name, 'w')
    f.write("Id;Interarrival Time;Arrival Time;Service Time;Time Service Begins;Waiting time in Queue;Time Service Ends;"
            "Time Customer Spends in System;Idle time of Server\n")
    for s in castomers:
        f.write("{0};{1};{2};{3};{4};{5};{6};{7};{8}\n".format(s.id, s.interArrivalTime, s.arrivalTime, s.serviceTime,
                                                               s.serviceBegins, s.waitingTimeInQueue, s.serviceEnds,
                                                               s.timeInSystem, s.idleTimeOfServer))
    f.close()


def statistics(castomers):
    # 1) Average waiting time in queue
    avTimeInQueue = sum([x.waitingTimeInQueue for x in castomers]) / len(castomers)
    print("\nAverage waiting time: {0:.2f}".format(avTimeInQueue))

    # 2) Probability that a customer has to wait
    probToWait = len([x for x in castomers if x.waitingTimeInQueue > 0]) / len(castomers)
    print("\nProbability that a customer has to wait: {0:.2f}".format(probToWait))

    # 3) Probability of an Idle server
    probIdle = sum([x.idleTimeOfServer for x in castomers]) / DEVS.GlobalTime
    print("\nProbability of an Idle server: {0:.2f}".format(probIdle))

    # 4) Average service time (theoretical 3.2)
    avServiceTime = sum([x.serviceTime for x in castomers]) / len(castomers)
    print("\nAverage service time: {0:.2f}".format(avServiceTime))

    # 5) Average time between arrivals (theoretical 4.5)
    avTimeBetwArr = sum([x.interArrivalTime for x in castomers]) / (len(castomers) - 1)
    print("\nAverage time between arrivals: {0:.2f}".format(avTimeBetwArr))

    # 6) Average waiting time for those who wait
    numOfCustWhoWait = len([x for x in castomers if x.waitingTimeInQueue > 0])
    if numOfCustWhoWait > 0:
        avTimeWhoWait = sum([x.waitingTimeInQueue for x in castomers]) / numOfCustWhoWait
        print("\nAverage waiting time for those who wait: {0:.2f}".format(avTimeWhoWait))
    else:
        # avTimeWhoWait = 0
        print("\nNobody was waiting in a queue")

    # 7) Average time a customer spends in the system
    avTimeInTheSystem1 = sum([x.timeInSystem for x in castomers]) / len(castomers)
    print("\nAverage time a customer spends in the system: {0:.2f}".format(avTimeInTheSystem1))

    avTimeInTheSystem2 = avTimeInQueue + avServiceTime
    print("\nAverage time a customer spends in the system (alternative): {0:.2f}".format(avTimeInTheSystem2))

