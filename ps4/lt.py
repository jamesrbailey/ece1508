#!/usr/bin/env python

import random as rd
import math
import scipy.stats as stats

class robust_soliton:
    def __init__(self, k, c, delta):
        self.k = k
        self.c = c
        self.delta = delta
        self.R = self.c * math.sqrt(self.k) * math.log(self.k/self.delta)
        self.Z = sum([self.pmf_ideal_soliton(d)+self.tau(d) for d in range(1,k+1)])

    def values(self):
        return range(1, self.k+1)

    def probs(self):
        return [self.pmf_robust_soliton(d) for d in self.values()]



    def pmf_ideal_soliton(self, d):
        mass = None
        if d == 0 or d > self.k:
            raise Exception("%d not in range [1,%d] required for ideal soliton"%(d,k))
        elif d == 1:
            mass = 1./self.k
        else:
            mass = 1./(d*(d-1.))
        return mass
    
    def tau(self, d):
        t = None
        if d < 1.:
            raise Exception("%d < 1 in tau(d)"%d)
        elif 1. <= d <= (math.ceil(self.k/self.R) - 1):
            t = (self.R/self.k) * (1./d)
        elif d == math.ceil(self.k/self.R):
            t = (self.R/self.k) * math.log(self.R/self.delta)
        elif (math.ceil(self.k/self.R) + 1) <= d <= self.k:
            t = 0
        else:
            raise Exception("%d not in range tau(d)"%d)
    
        return t

    def pmf_robust_soliton(self, d):
        return (self.pmf_ideal_soliton(d) + self.tau(d))/self.Z


    def test_ideal_soliton(self):
        cdf = 0
        for i in range(1,self.k+1):
            mass = self.pmf_ideal_soliton(i)
            cdf += mass
            print mass, cdf

    def test_tau(self):
        cdf = 0
        for i in range(1,self.k+1):
           mass = self.tau(i)
           cdf += mass
           print i, mass, cdf
        
        print self.R, self.k/self.R, math.ceil(self.k/self.R)

    def test_robust_soliton(self):
        cdf = 0
        for i in range(1,self.k+1):
            mass = self.pmf_robust_soliton(i)
            cdf += mass
            print mass, cdf
#pmf_rs.test_ideal_soliton()
#pmf_rs.test_tau()
#pmf_rs.test_robust_soliton()



k = int(10E3)
#k = 20
c = 0.01
delta = 0.5

pmf = robust_soliton(k, c, delta)

rs_rv = stats.rv_discrete(values=(pmf.values(), pmf.probs()))
#print rv.rvs(size=1000)

tx_info_bits = list(stats.bernoulli.rvs(p=0.5, size=k))

max_enc_bits = int(12E3)
#max_enc_bits = 400


# this is the encoder.  there are some non-pythonic optimizations here.
encoding = []  # represents encoding structure in terms of info bits indices
enc_bits = []  # represents encoded symbols
degrees = rs_rv.rvs(size=max_enc_bits)
info_indices = range(k)
for i in range(max_enc_bits):
    degree = degrees[i]
    encoding.append(rd.sample(info_indices, degree))
    enc_bits.append(sum([tx_info_bits[x] for x in encoding[i]])%2)
    #print encoding[i]
    #print enc_bits[i]


# decoder

rx_info_bits = [None]*k
rx_enc_bits = []
decoding = list(encoding)
decoded = 0
for i in range(max_enc_bits):
    rx_enc_bits.append(enc_bits.pop(0))
    for j in range(i+1):
        if len(decoding[j]) == 1:
            if rx_info_bits[decoding[j][0]] is None:
                decoded += 1

            rx_info_bits[decoding[j].pop(0)] = rx_enc_bits[j]
        else:
            for nb in decoding[j]:
                if rx_info_bits[nb] is not None:
                    rx_enc_bits[j] += rx_info_bits[nb]
                    rx_enc_bits[j] %= 2
                    decoding[j].remove(nb)
    print i, decoded
    if decoded == k:
        break

    #print rx_enc_bits
print tx_info_bits
print rx_info_bits


