#!/usr/bin/env python
import numpy as np
import random as rd
from math import *

rd.seed(100)  # fixing seed for randomizer

H = np.array([[ 0, 0, 0, 1, 1, 1, 1],
              [ 0, 1, 1, 0, 0, 1, 1],
              [ 1, 0, 1, 0, 1, 0, 1] ])

# Determined by putting H in standard form, then G = [I|P]
G = np.array([[ 1, 0, 0, 0, 0, 1, 1],
              [ 0, 1, 0, 0, 1, 0, 1],
              [ 0, 0, 1, 0, 1, 1, 0],
              [ 0, 0, 0, 1, 1, 1, 1] ])

def bitvector(i):
    return np.array([[(i>>x)&1 for x in list(reversed(range(4)))]])

encoder = dict()
for i in range(16):
    m = bitvector(i)
    cw = np.dot(m, G) % 2
    encoder[i] = cw

def distance(a,b):
    return np.linalg.norm(a-b)

def decode_ml(y):
    return encoder[np.argmin([distance(y, cw) for cw in encoder.values()])]

def decode_ml_bec(y):
    best_cw = None
    for cw in encoder.values():
        cw = cw[0]
        match = True
        for i in range(len(y)):
            if (y[i] != "e") and (int(y[i]) != cw[i]):
                match = False
                break

        if match == True:
                best_cw = cw
                break
    return best_cw

def channel_bsc(x, p):
    if p > 0.5:  # this is kind of a kludge since my ML decoder assumes p<0.5 and does minimum distance
        p = 1-p
    out = np.array([(b,b^1)[rd.random() < p] for b in np.nditer(x)])
    #print x,"-->", out
    return out

def channel_bec(x, p):
    # Erasure is denoted by 0.5 output value. This works well with subsequent decoding.
    out = np.array([(b,"e")[rd.random() < p] for b in np.nditer(x)])
    #print x,"-->", out
    return out

def channel_awgn(x, snr):
    N = 1 / (snr) # E_b is 0.5, since it is average energy of 0 and 1
    sigma = sqrt(N)
    out = np.array([b+rd.gauss(0,sigma) for b in np.nditer(x)])
    #print x,"-->", out
    return out


def testbench(decode, channel, channel_params):
    word_error = []
    for k in channel_params:
        error_count = 0
        trials = 0
        while error_count < 100 and trials < 1E5:
            trials += 1
            m = rd.randint(0,15)
            x = encoder[m]
            y = channel(x, k)
            x_hat = decode(y)
            errors = x_hat ^ x
            if np.count_nonzero(errors) > 0:
                error_count += 1
            if trials % 100 == 0:
                print trials, error_count
        wer = error_count/float(trials)
        word_error.append(wer)

        print k, wer
    return word_error


#params = np.logspace(start=-8., stop=0., num=30, base=2, endpoint=False)
#wers = testbench(decode_ml, channel_bsc, params)
#with open("bsc_ex.data", "w") as f:
#    f.write(",".join([str(r) for r in wers])+'\n')
#    f.write(",".join([str(p) for p in params])+'\n')
#print ','.join(str(p) for p in params)
#print ','.join(str(wer) for wer in wers)

params = np.logspace(start=-3., stop=0., num=30, base=2, endpoint=False)
wers = testbench(decode_ml_bec, channel_bec, params)
#with open("bec_ex.data", "w") as f:
#    f.write(",".join([str(r) for r in wers])+'\n')
#    f.write(",".join([str(p) for p in params])+'\n')
print ','.join(str(p) for p in params)
print ','.join(str(wer) for wer in wers)

#params = np.logspace(start=3.0, stop=-4, num=120, base=2)
#wers = testbench(decode_ml, channel_awgn, params)
#with open("awgn_ex.data", "w") as f:
#    f.write(",".join([str(r) for r in wers])+'\n')
#    f.write(",".join([str(p) for p in params])+'\n')
#print "awgn: ",wers





