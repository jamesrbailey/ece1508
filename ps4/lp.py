#!/usr/bin/env python

from pulp import *
import itertools
import random as rd
import numpy as np
import sys
import math
from scipy.stats import norm

class Variable:
    def __init__(self):
        self.LpV = None
        self.llr = 0

    def __str__(self):
        return self.LpV.name

class LP_Decode:
    def __init__(self):
        self.vs = []
        self.test_code = [0., 0., 0., 1., 1., 1., 1.]
        self.prob = LpProblem("LLR Error Minimization",LpMinimize)

    def create_vars(self,n):
        for i in range(n):
            var = Variable()
            var.LpV = LpVariable("v%d"%i,0,1)
            var.actual = self.test_code[i]
            self.vs.append(var)

    def constrain_parity(self, H):
        for row in H:
            variables = []
            for i in range(len(row)):
                if row[i] == 1:
                    variables.append(self.vs[i])
                    
            for S_size in range(1,len(variables),2):
                for S in itertools.combinations(variables, S_size):
                    S_bar = [x.LpV for x in variables if x not in S]
                    S = [x.LpV for x in S]
                    constraint = sum(S_bar) + len(S)-sum(S) >= 1.
                    self.prob += constraint

    def apply_bec(self, p_e):
        for v in self.vs:
            if rd.random() < p_e:
                v.llr = 0.
            else:
                v.llr = 1E6 if v.actual == 0. else -1E6
        self.update_cost()

    def apply_bsc(self, p):
        for v in self.vs:
            if v.actual == 0.:
                v.llr = +1 
            elif v.actual == 1.:
                v.llr = -1.

            if rd.random() < p:
                v.llr = -v.llr 

        self.update_cost()

    def apply_awgn(self, snr):
        sigma = math.sqrt(1./(float(snr))

        for v in self.vs:
            noisy_val = rd.gauss(v.actual,sigma)
            print noisy_val

        self.update_cost()

    def apply_llr(self,llrs):
        for i in range(len(llrs)):
            self.vs[i].LpV.varValue = 1.
            self.vs[i].llr = llrs[i]
        self.update_cost()

    def update_cost(self):
        self.prob += sum([v.LpV * v.llr for v in self.vs])

    def decode(self):
        #print self.prob
        self.prob.solve()
        errors = 0
        for v in self.vs:
            if v.LpV.varValue != v.actual:
                errors += 1

        return errors

    def test_bec(self, p_e):
        self.apply_bec(p_e)
        return self.decode()

    def test_bsc(self, p):
        self.apply_bsc(p)
        return self.decode()

def test_wer(p, channel):
    word_errors = 0
    trials = 0
    print >> sys.stderr, 'p=%f'%p
    while word_errors < 100:
        decode = LP_Decode()
        decode.create_vars(7)
        decode.constrain_parity(H)

        if channel == "bec":
            result = decode.test_bec(p)
        elif channel == "bsc":
            result = decode.test_bsc(p)
        elif channel == "awgn":
            result = decode.test_awgn(p)
        else:
            raise Exception("invalid channel selected")

        if result > 0:
            word_errors += 1

        trials += 1
        #print trials, word_errors
        if trials > 1E4:
            break

    return float(word_errors)/float(trials)


H = [[0,0,0,1,1,1,1],
     [0,1,1,0,0,1,1],
     [1,0,1,0,1,0,1] ]

#becs = np.logspace(start=-2., stop=0., num=1, base=2, endpoint=True)
becs = np.logspace(start=-4., stop=0., num=20, base=2, endpoint=True)
print ','.join(str(bec) for bec in becs)
print ','.join(str(test_wer(bec,"bec")) for bec in becs)


#wers = np.logspace(start=-9., stop=-1., num=20, base=2, endpoint=True)
#print ','.join(str(wer) for wer in wers)
#print ','.join(str(test_wer(wer,"bsc")) for wer in wers)

