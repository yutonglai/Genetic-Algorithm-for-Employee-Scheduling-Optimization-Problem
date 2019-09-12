import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import deap

from datetimerange import DateTimeRange
from astropy.table import Table


def OneWeekSchedule(ProTrue, AssigneeDF, AssigneeDict, AssigneeList, TaskList, Wage)
    
    ProTrueWeekend = ProTrue/2
    Schedule = LaborSchedule(ProTrueWeekend, Wage)
    results  = Schedule.Scheduling()
    DayoffSchedule = Schedule.Ranking(AssigneeDF,results[0])

    if np.prod(np.sum(ProTrueWeekend,axis=0)>=1):
        ScheduleWeekend  = results[0][-1]
        TotalCostWeekend = results[1]
        TaskCompletionWeekend = results[2].flatten()
    else:
        ScheduleWeekend  = np.ones(len(AssigneeDict)).astype(int)
        TotalCostWeekend = np.sum(Wage)
        TaskCompletionWeekend = np.sum(ProTrueWeekend,axis=0)


    TotalCost      = pd.DataFrame(1,index=['Cost'], columns=range(1,8))
    TaskCompletion = pd.DataFrame(1,index=TaskList, columns=range(1,8))
    FullSchedule   = pd.DataFrame(1,index=AssigneeList, columns=range(1,8))


    import copy
    for i in range(5):
        ProTrueDaily = copy.deepcopy(ProTrue)
        AssigneeOff  = np.where(DayoffSchedule[i+1]==0)[0].tolist()
        for j in AssigneeOff:
            ProTrueDaily[j,0:len(TaskList)] = np.zeros(len(TaskList))

        if np.prod(np.sum(ProTrueDaily,axis=0)>=1):
            Schedule = LaborSchedule(ProTrueDaily, Wage)
            results  = Schedule.Scheduling()
            FullSchedule[i+1]   = results[0][-1]
            TotalCost[i+1]      = results[1]
            TaskCompletion[i+1] = results[2].flatten()
        else:
            FullSchedule[i+1]   = DayoffSchedule[i+1]
            TotalCost[i+1]      = np.sum(DayoffSchedule[i+1].tolist()*Wage)
            TaskCompletion[i+1] = np.sum(ProTrueDaily,axis=0)


    FullSchedule[6] = ScheduleWeekend
    FullSchedule[7] = ScheduleWeekend
    FullSchedule = FullSchedule.astype(int)


    TotalCost[6] = TotalCostWeekend # 5 and 6 due to list not a dataframe
    TotalCost[7] = TotalCostWeekend
    TaskCompletion[6] = TaskCompletionWeekend
    TaskCompletion[7] = TaskCompletionWeekend
    
    return (FullSchedule, DayoffSchedule, TotalCost, TaskCompletion)
