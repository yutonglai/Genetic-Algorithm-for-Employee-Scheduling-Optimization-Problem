import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from datetimerange import DateTimeRange
from astropy.table import Table


def Productivity(Date, ScheduleCodeDict, column, AssigneeDict):
    ###################################################################
    #### Calculate how much time each assignee can spend on a task ####
    AssigneeList = list(AssigneeDict.keys())
    IntersectionHour = pd.DataFrame(0.0,index=AssigneeList,columns=TaskList)

    for Assignee in AssigneeList:
        AssigneeTimeFrames = ScheduleCodeDict[AssigneeDict[Assignee][0]].split(',')

        for Task in TaskList:
            TaskTimeFrame = TaskTimeFrameDict[Task]

            for AssigneeTimeFrame in AssigneeTimeFrames:
                AssigneeStart = Date+AssigneeTimeFrame.zfill(11)[0:5]
                AssigneeEnd   = Date+AssigneeTimeFrame.zfill(11)[6::]
                TaskStart     = Date+TaskTimeFrame.zfill(11)[0:5]
                TaskEnd       = Date+TaskTimeFrame.zfill(11)[6::]

                # Obtain timeframe   
                if int(AssigneeEnd[-5:-3])>=24:
                    nextday = (datetime.strptime(Date[0:-1], '%Y-%m-%d') + timedelta(days=1)).isoformat()[0:11]
                    AssigneeEnd = nextday+str(int(AssigneeEnd[-5:-3])-24).zfill(2)+AssigneeEnd[-3::]

                if int(AssigneeStart[-5:-3])>=24:
                    nextday = (datetime.strptime(Date[0:-1], '%Y-%m-%d') + timedelta(days=1)).isoformat()[0:11]
                    AssigneeStart = nextday+str(int(AssigneeStart[-5:-3])-24).zfill(2)+AssigneeStart[-3::]

                AssigneeTimeRange = DateTimeRange(AssigneeStart, AssigneeEnd)
                TaskTimeRange = DateTimeRange(TaskStart, TaskEnd)
                try:
                    IntersectionTimeRange = str(AssigneeTimeRange.intersection(TaskTimeRange))
                    IntersectionStart = np.datetime64(IntersectionTimeRange[0:16]) 
                    IntersectionEnd   = np.datetime64(IntersectionTimeRange[22::]) 
                    Intersection      = IntersectionEnd - IntersectionStart
                    IntersectionHour[Task][Assignee] = Intersection.item().total_seconds()/3600
                except:
                    IntersectionHour[Task][Assignee] = 0                


    ##################################################################
    #### Calculate Productivity of all assignee to all tasks #########
    AssigneeDF = pd.DataFrame.from_dict(AssigneeDict, orient='index',columns=column)

    # AsgneDr: how many hours an employee need to complete a task alone
    AssigneeDr = np.array(AssigneeDF.drop(columns=['Code','Wage']))
    Wage = np.array(AssigneeDF['Wage'])

    # AsgneTaskNum: how many tasks an employee need to do in a day
    AsgneTaskNum = np.count_nonzero(AssigneeDr,axis=1)
    AssigneePro = 1/AssigneeDr
    AssigneePro[AssigneePro == np.inf] = 0

    # FullTrue: The productivity of all employee to all tasks
    ProTrue = np.array(AssigneePro*IntersectionHour)
    
    return (ProTrue, AssigneeDF, AssigneeList, Wage)
