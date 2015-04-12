#!/usr/bin/env python

from pulp import *
import itertools

class Variable:
    def __init__(self):
        self.LpV = None
        self.llr = 0
    def __str__(self):
        return self.LpV.name

class LP_Decode:
    def __init__(self):
        self.vs = []

    def create_vars(self,n):
        for i in range(n):
            var = Variable()
            var.LpV = LpVariable("v%d"%i,0,1)
            self.vs.append(var)

    def constrain_parity(H):
        for i in len(H):
            checks = H[i]
            for j in len(checks):
                for S_size in range(1,len(variables),2):
                    for S in itertools.combinations(variables, S_size):
                        S_bar = [x for x in variables if x not in S]
                        constraint = sum([v.LpV for v in S_bar]) + len(S)-sum([v.LpV for v in S]) >= 1.
                        print constraint


decode = LP_Decode()

#      0 0 0 1 1 1 1
# H =  0 1 1 0 0 1 1
#      1 0 1 0 1 0 1

H = [[0 0 0 1 1 1 1],
     [0 1 1 0 0 1 1],
     [1 0 1 0 1 0 1] ]

decode.constrain_parity([vs[3], vs[4], vs[5], vs[6]])
decode.constrain_parity([vs[1], vs[2], vs[5], vs[6]])
decode.constrain_parity([vs[0], vs[2], vs[4], vs[6]])

#prob = LpProblem("Erasure threshold maximization",LpMaximize)
#prob += sum([l/float(i) for i, l in self.lambdas.iteritems()])


