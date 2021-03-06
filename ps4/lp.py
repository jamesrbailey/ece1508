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
    def __init__(self,code):
        self.vs = []
        self.test_code = code
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
        sigma = math.sqrt(1./(float(snr)))

        for v in self.vs:
            noisy_val = rd.gauss(v.actual,sigma)
            #print noisy_val
            # In AWGN the LLR starts as the ratio of the Q function on the distance from 0/1
            p0 = norm(0.,sigma).pdf(noisy_val)
            p1 = norm(1.,sigma).pdf(noisy_val)
            v.llr = math.log(p0/p1)
            #print v.actual, noisy_val, v.llr

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
        #self.prob.solve(solver=solvers.COIN_CMD())
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

    def test_awgn(self, snr):
        self.apply_awgn(snr)
        return self.decode()

def test_wer(p, channel):
    encoder = dict()
    G = np.array([[ 1, 0, 0, 0, 0, 1, 1],
                  [ 0, 1, 0, 0, 1, 0, 1],
                  [ 0, 0, 1, 0, 1, 1, 0],
                  [ 0, 0, 0, 1, 1, 1, 1] ])
    def bitvector(i):
        return np.array([[(i>>x)&1 for x in list(reversed(range(4)))]])
    for i in range(16):
        m = bitvector(i)
        cw = (np.dot(m, G) % 2)[0].tolist()
        encoder[i] = cw


    word_errors = 0
    trials = 0
    print >> sys.stderr, 'p=%f'%p
    while word_errors < 100:
        m = rd.randint(0,15)
        x = encoder[m]
        decode = LP_Decode(x)
        #print decode.test_code
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
        if trials%100 == 0:
            print trials, word_errors
        if trials > 1E4:
            break

    return float(word_errors)/float(trials)

H = [[0,0,0,1,1,1,1],
     [0,1,1,0,0,1,1],
     [1,0,1,0,1,0,1] ]


max_ex = 4
#becs = np.logspace(start=-float(max_ex), stop=0., num=30, base=2, endpoint=True)
#print becs
#print ','.join(str(bec) for bec in becs)
#print ','.join(str(test_wer(bec,"bec")) for bec in becs)


#bscs = np.logspace(start=-float(max_ex), stop=0., num=30, base=2, endpoint=True)
#wers = [test_wer(bsc,"bsc") for bsc in bscs]
#print ','.join(str(bsc) for bsc in bscs)
#print ','.join(str(wer) for wer in wers)

snrs = [2**max_ex - x + 1 for x in np.logspace(start=float(max_ex), stop=0., num=20, base=2, endpoint=True)]
#snrs = np.logspace(start=0, stop=max_ex., num=20, base=2, endpoint=True)
print ','.join(str(snr) for snr in snrs)
print ','.join(str(test_wer(snr,"awgn")) for snr in snrs)
