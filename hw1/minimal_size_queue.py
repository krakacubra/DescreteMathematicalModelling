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
    def __init__(self, n):
        self.e_time = 0.0
        self.number = n

    def execute(self):
        customer = CustomerStat()
        customer.id = DEVS.newId
        customer.arrivalTime = self.e_time
        if len(DEVS.stats) > 0:
            customer.interArrivalTime = customer.arrivalTime - DEVS.stats[-1].arrivalTime

        # server is Free
        if DEVS.server_idle[self.number]:
            DEVS.server_idle[self.number] = False
            service_time = custm.rvs()
            service = ServiceEvent(self.number)
            service.e_time = self.e_time + service_time
            DEVS.EQ.add_event(service)
            service.id = customer.id
            customer.serviceTime = service_time
            customer.serviceBegins = self.e_time
        else:
            DEVS.customer_queue[self.number].append(customer.id)
        # server is Busy
        DEVS.stats.append(customer)
        print("\n")
        i = 0
        if DEVS.newId < max_agents - 1:
            lens = [len(DEVS.customer_queue[i]) for i in range(number_of_services)]
            while i < number_of_services and not (len(DEVS.customer_queue[i]) == min(lens)
                                                  and DEVS.server_idle[i] is True):
                    i = i + 1
            if i != number_of_services:
                next_arrival = ArrivalEvent(i)
            else:
                next_arrival = ArrivalEvent(lens.index(min(lens)))
            next_arrival.e_time = self.e_time + random.randint(arrivalRateMin, arrivalRateMax)
            DEVS.EQ.add_event(next_arrival)
        DEVS.newId = DEVS.newId + 1
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

        if len(DEVS.customer_queue[self.number]) > 0:
            service_time = custm.rvs()
            qid = DEVS.customer_queue[self.number].pop(0)
            qind = [i for i, val in enumerate(DEVS.stats) if val.id == qid][0]
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
    AE = ArrivalEvent(0)
    DEVS.EQ.add_event(AE)

    # simulation attributes
    DEVS.stats = []
    DEVS.newId = 0
    DEVS.customer_queue = [[] for i in range(number_of_services)]
    DEVS.server_idle = [True for _ in range(number_of_services)]
    DEVS.lastServedTime = [0] * number_of_services  # for Idle time

    while DEVS.EQ.queue_size() > 0:
        DEVS.process_next_event()
    return DEVS.stats


customers = run_once()
store_file(customers, 'output with minimal size queue.csv')
statistics(customers)
