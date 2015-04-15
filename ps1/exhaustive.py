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
    encoder[i] = [str(x) for x in cw[0]]

def distance(a,b):
    return np.linalg.norm(a-b)

def decode_ml(y):
    return encoder[np.argmin([distance_hamming(y, cw) for cw in encoder.values()])]

def distance_bec(x,y):
    d = 0
    #print x, y
    for xb,yb in zip(x,y):
        #xb = str(xb)
        #yb = str(yb)
        #print xb, yb
        if xb == "e" or yb == "e":
            next
        elif xb != yb:
            d += 1
    return d

def distance_hamming(x,y):
    d = 0
    for xb,yb in zip(x,y):
        if xb != yb:
            d += 1
    return d


def decode_ml_bec(y):
    for cw in encoder.values():
        if distance_bec(cw, y) == 0:
            return cw

    print x
    raise Exception("could not decode")

def channel_bsc(x, p):
    if p > 0.5:  # this is kind of a kludge since my ML decoder assumes p<0.5 and does minimum distance
        p = 1-p
    out = []
    for xb in x:
        if rd.random() < p:
            if x == "1":
                ob = "0"
            else:
                ob = "1"
        else:
            ob = xb
        out.append(ob)

    return out

def channel_bec(x, p):
    # Erasure is denoted by 0.5 output value. This works well with subsequent decoding.
    out = [(b,"e")[rd.random() < p] for b in x]
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
        while error_count < 200 and trials < 1E5:
            trials += 1
            m = rd.randint(0,15)
            x = encoder[m]
            y = channel(x, k)
            x_hat = decode(y)
            for xb,xhb in zip(x,x_hat):
                if xb != xhb:
                    error_count += 1
                    break

            if trials % 10000 == 0:
                print trials, error_count

        wer = error_count/float(trials)
        print trials,error_count,wer
        word_error.append(wer)

    return word_error


params = np.logspace(start=-8., stop=0., num=30, base=2, endpoint=False)
wers = testbench(decode_ml, channel_bsc, params)
print ','.join(str(p) for p in params)
print ','.join(str(wer) for wer in wers)

#params = np.logspace(start=-8., stop=0., num=50, base=2, endpoint=False)
#wers = testbench(decode_ml_bec, channel_bec, params)
#with open("bec_ex.data", "w") as f:
#    f.write(",".join([str(r) for r in wers])+'\n')
#    f.write(",".join([str(p) for p in params])+'\n')
#print ','.join(str(p) for p in params)
#print ','.join(str(wer) for wer in wers)

#params = np.logspace(start=3.0, stop=-4, num=120, base=2)
#wers = testbench(decode_ml, channel_awgn, params)
#with open("awgn_ex.data", "w") as f:
#    f.write(",".join([str(r) for r in wers])+'\n')
#    f.write(",".join([str(p) for p in params])+'\n')
#print "awgn: ",wers





