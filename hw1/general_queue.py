# -*- coding: cp1251 -*-
from DEVS import *
import random
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt


arrivalRateMin = 1
arrivalRateMax = 2
max_agents = 1000
service_xk = np.arange(2, 8) + 1
service_pk = (0.1, 0.2, 0.3, 0.25, 0.1, 0.05)
custm = stats.rv_discrete(name='custm', values=(service_xk, service_pk))
number_of_services = int(input('Number of services:'))

# ---- Customer Statistics ----
class CustomerStat:
    def __init__(self):
        self.id = -1
        self.arrivalTime = -1
        self.serviceTime = -1
        self.interArrivalTime = 0
        self.serviceBegins = -1
        self.waitingTimeInQueue = 0
        self.serviceEnds = -1
        self.timeInSystem = -1
        self.idleTimeOfServer = 0


# ---- Arrival Event ----
class ArrivalEvent:
    def __init__(self):
        self.e_time = 0.0

    def execute(self):
        customer = CustomerStat()
        customer.id = DEVS.newId
        customer.arrivalTime = self.e_time
        if len(DEVS.stats) > 0:
            customer.interArrivalTime = customer.arrivalTime - DEVS.stats[-1].arrivalTime
        if DEVS.newId < max_agents - 1:
            next_arrival = ArrivalEvent()
            next_arrival.e_time = self.e_time + random.randint(arrivalRateMin, arrivalRateMax)
            DEVS.EQ.add_event(next_arrival)

        server = -1
        # find an idle server
        for i in range(number_of_services):
            if DEVS.server_idle[i]:
                server = i
                break

        # server is Free
        if server != -1:
            DEVS.server_idle[server] = False
            service_time = custm.rvs()

            service = ServiceEvent(server)
            service.e_time = self.e_time + service_time
            service.id = customer.id
            DEVS.EQ.add_event(service)
            customer.serviceTime = service_time
            customer.serviceBegins = self.e_time
        # server is Busy
        else:
            # increase waiting line
            DEVS.customerQueue.append(customer.id)

        DEVS.newId = DEVS.newId + 1
        DEVS.stats.append(customer)
        # ---- Service Event ----


class ServiceEvent:
    def __init__(self, n):
        self.e_time = 0.0
        self.number = n
        self.id = 0

    def execute(self):
        ind = [i for i, val in enumerate(DEVS.stats) if val.id == self.id][0]
        DEVS.stats[ind].serviceEnds = self.e_time
        DEVS.stats[ind].timeInSystem = DEVS.stats[ind].serviceEnds - DEVS.stats[ind].arrivalTime
        DEVS.stats[ind].waitingTimeInQueue = DEVS.stats[ind].serviceBegins - DEVS.stats[ind].arrivalTime # 0 without queue
        DEVS.stats[ind].idleTimeOfServer = DEVS.stats[ind].serviceBegins - DEVS.lastServedTime[self.number]

        if len(DEVS.customerQueue) > 0:
            qid = DEVS.customerQueue.pop(0)
            qind = [i for i, val in enumerate(DEVS.stats) if val.id == qid][0]

            service_time = custm.rvs()
            service = ServiceEvent(self.number)
            service.e_time = self.e_time + service_time
            service.id = qid
            DEVS.EQ.add_event(service)

            DEVS.stats[qind].serviceBegins = self.e_time
            DEVS.stats[qind].serviceTime = service_time
        else:
            DEVS.server_idle[self.number] = True

        DEVS.lastServedTime[self.number] = self.e_time


def run_once():
    # run simulation
    AE = ArrivalEvent()
    DEVS.EQ.add_event(AE)

    # simulation attributes
    DEVS.customerQueue = []
    DEVS.stats = []
    DEVS.newId = 0
    DEVS.lastServedTime = [0]*number_of_services  # for Idle time
    DEVS.server_idle = [True for i in range(number_of_services)]

    while DEVS.EQ.queue_size() > 0:
        DEVS.process_next_event()
    return DEVS.stats


customers = run_once()
store_file(customers, 'output with general queue.csv')
statistics(customers)


