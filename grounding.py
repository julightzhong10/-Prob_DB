'''
CSC267A Final Project
Zixiang Liu, Weijia Yuan
11/29/2018
This code is tested under version:
3.7.0 [MSC v.1912 64 bit (AMD64)]
'''

from PDBparser import Query
from database import Database

class Grounding:
    '''
    Simple Grounding
    '''
    def __init__(self, query, database):
        '''
        args:
            query: parsed query
            database: database handle for table access
        '''
        self.q = query
        self.db = database

    def printG(self):
        print(self.q)
        for table in self.db.tables:
            print(table)
            print(self.db.getTable(table))

    def ground(self):
        self.vdl = [] # list of dictionaries of variables (names as key) and their domains (value)

        for ucq in self.q: # for each UCQ in the query sentence
            vd = {}
            for pt in ucq: # for each predicate tuple
                tn = pt[0] # table name
                for i, v in enumerate(pt[1]): # the i th value of name v
                    if v in vd:
                        old = vd[v]
                        new = self.db.getAllPossibleValues([(tn, i+1)])
                        vd[v] = list(set(old) & set(new)) # find the intersection of two domains
                    else:
                        vd[v] = self.db.getAllPossibleValues([(tn, i+1)])
            self.vdl.append(vd)

        def withinUCQ(idx):
            vn = vs[idx] # current variable name
            vas = [] # variable assigments, list of dictionaries
            if idx == len(vs)-1: # if the last variable or in another word, base case
                for cst in vd[vn]:
                    a = {}
                    a[vn] = cst
                    vas.append(a)
            else:
                for cst in vd[vn]:
                    for a in withinUCQ(idx + 1):
                        a[vn] = cst
                        vas.append(a)
            return vas

        self.vsl = [] # list of lists of dictionaries of variable assignments
        for i, vd in enumerate(self.vdl):
            vs = list(vd.keys()) # list of all variable names
            allcbn = withinUCQ(0) # all possible combinations

            # the following block is to remove impossible combinations
            for pt in self.q[i]:
                pn = pt[0]
                pv = pt[1]
                allowedCbn = [row[:-1] for row in self.db.getTable(pn)]
                for a in allcbn[:]:
                    pcstr = []
                    for v in pv:
                        pcstr.append(a[v])
                    if not pcstr in allowedCbn:
                        allcbn.remove(a)

            self.vsl.append(allcbn)

        def betweenUCQ(idx):
            vas = [] # list of lists of dictionary
            if idx == 0:
                for a in self.vsl[idx]:
                    vas.append([a])
            else:
                for a in self.vsl[idx]:
                    for al in betweenUCQ(idx-1):
                        al.append(a)
                        vas.append(al)
            return vas
        self.gva = betweenUCQ(len(self.vsl)-1)

        self.gqs = [] # grounded logical sentence
        for al in self.gva: # for each assignment list
            for i, a in enumerate(al): # i is the index of UCQ, a is assignment dictionary
                ucq = [] # the new UCQ list, now with constants
                for pt in self.q[i]:
                    pn = pt[0] # predicate variable
                    pv = pt[1] # predicate variable name list
                    pc = [] # predicate constants substitute variable
                    for v in pv:
                        pc.append(a[v])
                    ucq.append((pn, pc))
                self.gqs.append(ucq)
        return self.gqs

    def printGrounded(self):
        print('\nGrounded Query')
        nl = 0 # new line
        for i in range(len(self.gqs)):
            print(self.gqs[i], end = '')
            nl += 1
            if nl == len(self.q):
                nl = 0
                print()
