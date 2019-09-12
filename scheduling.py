import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import deap

from datetimerange import DateTimeRange
from deap import base
from deap import creator
from deap import tools

from astropy.table import Table

print(pd.__version__)
print(np.__version__)
print(deap.__version__)

class LaborSchedule:
        
    def __init__(self, ProTrue, Wage):
        toolbox = base.Toolbox()

        # FullPro: The productivity of all employee in a day
        self.ProFull       = ProTrue
        self.Wage          = Wage
        self.NumOfAssignee = len(self.ProFull)
        self.NumOfTasks    = len(self.ProFull[0])             
        self.ProComb       = np.sum(self.ProFull,axis=0)
#         self.ProCombThresh = np.clip(self.ProComb,0,1)
        self.Schedule      = np.array([self.ProFull.sum(axis=1)!=0])
        self.Cost          = self.Schedule*self.Wage
        self.TotalCost     = self.Cost.sum()
        self.TaskComplete  = self.ProFull.sum(axis=0)
        
    def evaluation(self, individual):    
        TotalCost = self.TotalCost

        # Schedule for given days
        Assignment = np.reshape(individual,(self.NumOfAssignee,1))
        DailySchedule = Assignment.sum(axis=1)!=0

        # Schedule productivity for given days
        SchProComb = Assignment*self.ProFull

        # The given days' task completed
        TaskCompleteComb = np.sum(SchProComb,axis=0)
        # TaskCompleteComb = np.reshape(TaskCompleteComb,(1,self.NumOfTasks))
        # TaskCompleteComb = TaskCompleteComb.T

        # If the Tasks can be completed and each employee can have at least
        # one day off, then calculate the total cost
        # Assume all the tasks have to be completed within given duration limit or Not compute cost
        if np.prod(TaskCompleteComb>=1):
            DailyCost = DailySchedule*self.Wage
            TotalCost = DailyCost.sum()
        return TotalCost,
    
            
    def Scheduling(self, CXPB=0.2, MUTPB=0.2, NGEN=50, n=10000):        
        random.seed(64)
        toolbox  = base.Toolbox()
        Schedule = np.array([np.zeros(len(self.Wage))])
        
        # define classes
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)   
        
        # Attribute generator 
        # define 'attr_bool' to be an attribute ('gene')
        # which corresponds to integers sampled uniformly
        # from the range [0,1] (i.e. 0 or 1 with equal probability)
        toolbox.register("attr_bool", random.randint, 0, 1)

        # Structure initializers
        # define 'individual' to be an individual (chromosome)
        # each individual defines a schedule of a day with 0 representing not coming and 1 representing coming.
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, self.NumOfAssignee)
        
        # define the population to be a list of individuals (chromosomes)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        
        # creating populations 
        pop = toolbox.population(int(n))
        
        print("Start of evolution")

        # Evaluate the entire population   
        fitnesses = list(map(self.evaluation, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(pop))

        # Begin the evolution
        for g in range(NGEN):
            print("-- Generation %i --" % g)

            # Select the next generation individuals
            offspring = tools.selTournament(pop, len(pop), tournsize=3) 
            
            # Clone the selected individuals
            offspring = list(map(toolbox.clone, offspring))

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):                
                # cross two individuals with probability CXPB
                if random.random() < CXPB:                    
                    # toolbox.mate(child1, child2)                    
                    tools.cxTwoPoint(child1, child2)
                    
                    # fitness values of the children
                    # must be recalculated later
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:                
                # mutate an individual with probability MUTPB
                if random.random() < MUTPB:
                    tools.mutFlipBit(mutant,indpb=0.05)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.evaluation, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            print("  Evaluated %i individuals" % len(invalid_ind))

            # The population is entirely replaced by the offspring
            pop[:] = offspring

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in pop]

            print("-- End of (successful) evolution --")

            best_ind   = tools.selBest(pop, 1)[0]
            Assignment = np.reshape(best_ind,(self.NumOfAssignee,1))
            Day1Sche   = np.array([Assignment.sum(axis=1)!=0])

            Day1Cost   = Day1Sche*self.Wage
            TotalCost  = Day1Cost.sum()

            # Schedule productivity for given days
            SchProComb = Assignment*self.ProFull

            # The given days' tasks completed
            TaskCompleteComb = np.sum(SchProComb, axis=0)
            TaskCompleteComb = np.reshape(TaskCompleteComb,(1,self.NumOfTasks))
            TaskCompleteComb = TaskCompleteComb.T
            
            if np.prod(TaskCompleteComb>=1):
                Schedule = np.concatenate((Schedule,Day1Sche),axis=0)
                TaskComplete = TaskCompleteComb
                print(Schedule[-1,:])
                print(TotalCost)
                print(TaskComplete)
            else:
                Schedule = np.concatenate((Schedule,self.Schedule),axis=0)
                TaskComplete = self.TaskComplete
                
        return(Schedule,TotalCost,TaskComplete)
        
                
    def Ranking(self, AssigneeDF, Schedule):
        Importance = pd.DataFrame(np.sum(Schedule,axis=0).astype(int))
        Rank = Importance.rank()
        Availability = pd.DataFrame(AssigneeDF['Code'])
        Availability['Rank'] = np.array(Rank)

        MinDuplicSize = 999999999
        MinRankStd = 999999999
        Duplic = np.array([[0,0]])
        Availabilities = np.array([0])
        
        for k in range(10000):
            Availability = Availability.sample(frac=1)
            Availabilitysplit  = np.array_split(Availability,5)
            RankMean   = Availability['Rank'].mean()
            DuplicSize = 0
            RankStd    = 0

            for j in range(5):
                OriginSize = len(pd.Series(Availabilitysplit[j]['Code']))
                UniqueSize = len(pd.Series(Availabilitysplit[j]['Code']).unique())
                DuplicSize = DuplicSize + OriginSize - UniqueSize
                RankStd    = RankStd + np.absolute(Availabilitysplit[j]['Rank'].mean() - RankMean)

            if DuplicSize<MinDuplicSize and RankStd<MinRankStd:
                MinRankStd    = RankStd
                MinDuplicSize = DuplicSize
                tempDuplic    = np.array([[DuplicSize,RankStd]])
                Duplic        = np.concatenate((Duplic,tempDuplic),axis=0)
                print(k)
                print(Duplic)
                print(Availabilitysplit)
                print(str(Availabilitysplit[0]['Rank'].mean()),
                      str(Availabilitysplit[1]['Rank'].mean()),
                      str(Availabilitysplit[2]['Rank'].mean()),
                      str(Availabilitysplit[3]['Rank'].mean()),
                      str(Availabilitysplit[4]['Rank'].mean()),
                      RankMean)

        # Day-off schedule
        split = np.array_split(Availability,5)
        DayoffSchedule = pd.DataFrame(1,index=list(AssigneeDF.index),columns=range(1,8))
        for i in range(5):
            index = list(split[i].index.get_level_values(0))
            DayoffSchedule.loc[index,i+1] = 0
        return(DayoffSchedule)
        
