# Genetic-Algorithm-for-Employee-Scheduling-Optimization-Problem
An implementation of genetic algorithm on scheduling optimization problem

A0. Summary

The modeling is part of the StorX AI project. It focuses on store labor scheduling optimization and related tasks.

A1. Developer info

Name: Yutong Lai

Location: San Diego, United State.

Email: yutong@retechlabs.com

A2. Objective

Develop AI algorithm to Help Wumart store managers determine the optimized labor schedule that can satisfy different applicable assumptions while lowering the labor cost.

A3. Assumptions & Limitations

Assumptions:

        1. Each assignee has the ability to handle different tasks;

        2. The amount of each task can be quantified;

        3. Each assignee’s productivity rate are different;

        4. Each assignee receives different wages;

        5. Each assignee will have at least one day off in a week;

        6. There will be more tasks at the weekend; (06/25/2019)

        7. The task types can be scheduled in advance. (07/16/2019)

Limitations:

        1. Minimize the overall labor cost;

        2. Care about the assignee preference and availability of time;

        3. Ensure enough employee for different tasks in different days;(06/19/2019)

        4. Ensure that the daily number of assignee in the store is as equal as possible; (06/19/2019)

        4. For a typical week, more assignee need to be allocate for the weekend;(06/26/2019)

        5. Ensure that the important/most effective assignee will not have the same day off;(06/19/2019)

        6. Consider task amount in promotion days.(06/21/2019)
        
        
#### Input data:
```
Date = '2019-07-22T'
#### load in working time code
ScheduleCode = pd.read_csv('/home/yutong/Dropbox/Retech Labs/StorX/data/schedule code list & decoded time 20180409 V2.csv')

#### Task time period
TaskTimeFrameDict = {'T1':'08:20-11:45',
                     'T2':'10:15-12:55',
                     'T3':'12:30-14:00',
                     'T4':'17:10-20:30'}

ScheduleCodeDict = ScheduleCode.set_index('Code')['time'].to_dict()
TaskList = list(TaskTimeFrameDict.keys())

#### The first column is time code, the last column is salary
column       =           ['Code'] +     TaskList    + ['Wage']
AssigneeDict = {'FA0001':['10K',   2,    3,    4,    5,   191],
                'FA0002':['10H',   3,    4,    2,    4,   155],
                'FA0003':['7AE',   2,    2,    4,    6,   172],
                'FA0004':['7AQ',   2,    5,    2,    3,   162],
                'FA0005':['7AG',   1,    4,    6,    2,   120],
                'FA0006':['17B',   2,    2,    4,    4,   169],
                'PA0001':['5M' ,   2,    2,    2,    6,    69],
                'PA0002':['6AJ',   3,    4,    1,    5,    59],
                'PA0003':['6D' ,   5,    3,    2,    2,    72],
                'PA0004':['7AE',   2,    2,    3,    4,    55],
                'PA0005':['7AU',   6,    4,    3,    2,    56],
                'PA0006':['7BS',   2,    2,    2,    3,    45]}
```
#### Compute the true productivity according to the working time code and task time period
```
from productivity import Productivity

ProTrue, AssigneeDF, AssigneeList, Wage = Productivity(Date, ScheduleCodeDict, column, AssigneeDict)
```
#### Compute a schedule for a week, assuming weekend's workload is twice more than usual
```
from MakeSchedule import OneWeekSchedule

FullSchedule, DayoffSchedule, TotalCost, TaskCompletion = OneWeekSchedule(ProTrue, AssigneeDF, AssigneeDict, AssigneeList, TaskList, Wage)
```
#### We will get the optimized schedule, day-off schedule, Total cost and how the tasks are completed


##### Table 1. An optimized week-schedule
EmployeeID  |1  |2  |3  |4  |5  |6  |7
-----------:|:-:|:-:|:-:|:-:|:-:|:-:|:-
    FA0001  |0  |0  |0  |0  |0  |0  |0
    FA0002  |0  |0  |0  |0  |0  |0  |0
    FA0003  |0  |1  |0  |0  |0  |1  |1
    FA0004  |0  |0  |0  |0  |0  |0  |0
    FA0005  |0  |0  |0  |0  |0  |0  |0
    FA0006  |0  |0  |0  |0  |0  |0  |0
    PA0001  |0  |0  |0  |1  |0  |1  |1
    PA0002  |0  |0  |0  |1  |0  |0  |0
    PA0003  |1  |1  |1  |0  |1  |1  |1
    PA0004  |1  |0  |1  |1  |1  |1  |1
    PA0005  |1  |1  |1  |0  |1  |1  |1
    PA0006  |0  |0  |0  |1  |0  |1  |1

##### Table 2. The human BrainSpan-RNA sequence data
GeneID / Sample |1        |2        |3        |4        |5        |6        |......  |524        
---------------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:------:|:--------
ENSG00000000003 |5.226783 |4.658283 |4.345572 |4.841400 |4.392196 |3.970916 |......  |2.029566     
ENSG00000000419 |5.144586 |4.443982 |4.302681 |4.546363 |4.338313 |3.587409 |......  |4.900434     
ENSG00000001036 |3.471608 |3.072748 |2.971666 |3.208103 |3.200653 |3.031687 |......  |2.757560
......          |......   |......   |......   |......   |......   |......   |......  |......
ENSG00000259770 |3.555986 |3.458692 |3.094457 |3.282903 |3.154652 |2.900298 |......  |3.080229
