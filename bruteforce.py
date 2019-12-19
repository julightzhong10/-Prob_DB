'''
CSC267A Final Project
Weijia Yuan
11/27/2018
This is the main code of brute force function for PDB database
The first version is only for case "Q(x1), R(x1, y1)"
'''
import copy
import csv
from PDBparser import Query
from database import Database
from grounding import Grounding


def dpll(f, dic):
    '''
    :param f: formula of grounding
    :param dic: dictionary of possibility of each table
    :return: the result of this query
    '''
    global res

    def dfs(f, literals, v, dic):
        global res
        if len(v) == length:
            if withinUCQ(f, v):
                p = 1
                for i in v:
                    if v[i] is True:
                        p *= dic[i[0]][i[1]]
                    else:
                        q = 1 - dic[i[0]][i[1]]
                        p *= q
                res += p
            return
        else:
            l, s = literals[0], literals[1:]
            v1, v2 = copy.deepcopy(v), copy.deepcopy(v)
            v1[l], v2[l] = True, False
            dfs(f, s, v1, dic)
            dfs(f, s, v2, dic)

    flat = [i for j in f for i in j]
    literals = []
    for l in flat:
        if l not in literals:
            literals.append(l)
    length = len(literals)
    res = 0
    dfs(f, literals, {}, dic)
    return res


def withinUCQ(f, v):
    '''
    :param f: formula from grounding query
    :param v: list contains the variable of True or False
    :return: the grounding query is satisfiable or not
    '''
    new = copy.deepcopy(f)
    for i in v.keys():
        for c in new:
            for n,j in enumerate(c):
                if j == i:
                    c[n] = i
    if any(all(v[i] is True for i in c) for c in new):
        return True
    else:
        return False


def getGrounding(query, database):
    '''
    :param query: query read from input
    :param table: table read from input
    :return: gounded query for brute force solution
    '''
    # example grounding [('Q', ['0']), ('R', ['0', '0'])]
    g = Grounding(query, database)
    g = g.ground()
    #only deal with UCQ
    for c in g:
        for n, nTable in enumerate(c):
            tpl = (nTable[0], ','.join(nTable[1]))
            c[n] = tpl
    return g

def sol_UCQ(g, database):
    # get a dictionary that contains all the table
    # {'Q': {'0': 0.7, '1': 0.3, '2': 0.5}, 'R': {'0,0': 0.8, '0,1': 0.4, '0,2': 0.5, '1,2': 0.6, '2,2': 0.9}}
    dic = {}
    for tb in database.tables:
        tmp = database.getTable(tb)
        dic[tb] = {(','.join(row[:-1])):row[-1] for row in tmp}

    # use brute force to get the possibility resolution of query
    res = dpll(g, dic)
    return res

