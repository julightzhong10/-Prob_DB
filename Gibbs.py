'''
CSC267A Final Project
Zixiang Liu
12/02/2018
This code is tested under version:
3.7.0 [MSC v.1912 64 bit (AMD64)]
'''

from random import random
from database import Database
from PDBparser import Query
from grounding import Grounding

class Gibbs:
    '''
    The predicate terms are independent of each other
    Therefore Gibbs sampling is equivalent to direct sampling
    By sample a probability distribution each time and test the satisfaction
    Gibbs Sampling returns the approximate probability of query_test
    '''
    def __init__(self, query, database):
        '''
        args:
            qf: query file name
            tbl: table file names list
                both are used to initialize a grounding object
        '''
        self.g = Grounding(query, database) # a grounding object

    def sample(self, n):
        '''
        args:
            n: number to sample
        return:
            float: the approximate probability
        '''
        self.g.ground()
        success = 0
        for i in range(n):
            probd = {}
            for pn in self.g.db.tables:
                probd[pn] = {}
                for k in [','.join(row[:-1]) for row in self.g.db.getTable(pn)]:
                    probd[pn][k] = random()
            for j, ucq in enumerate(self.g.gqs):
                flag = True
                for k, pt in enumerate(ucq):
                    pn = pt[0]
                    pcstr = ','.join(pt[1])
                    prob = self.g.db.selectByArgs(pn, pt[1])
                    if probd[pn][pcstr] > prob:
                        flag = False
                        break
                if flag:
                    success += 1
                    break

        self.rate = float(success)/float(n)
        return self.rate
