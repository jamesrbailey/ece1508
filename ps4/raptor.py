#!/usr/bin/env python

import random as rd
import math
import sys
import scipy.stats as stats

class robust_soliton:
    def __init__(self):
        pass

    def values(self):
        return [1,2,3,4,5,8,9,19,65,66]

    def probs(self):
        return [self.masses(d) for d in self.values()]

    def masses (self, d):
        if d == 1:
            mass = 0.008
        elif d == 2:
            mass = 0.5
        elif d == 3:
            mass = 0.17
        elif d == 4:
            mass = 0.7
        elif d == 5:
            mass = 0.8
        elif d == 8:
            mass = 0.5
        elif d == 9:
            mass = 0.4
        elif d == 19:
            mass = 0.05
        elif d == 65:
            mass = 0.02
        elif d == 66:
            mass = 0.003


        return mass


k = int(10E3)
max_enc_bits = int(100E3)
delta = 0.5

for trial in  range(100):
    print trial
    with open("data_raptor/%d.data"%trial, 'w') as file:
        pmf = robust_soliton()
        rs_rv = stats.rv_discrete(values=(pmf.values(), pmf.probs()))
        
        #tx_info_bits = list(stats.bernoulli.rvs(p=0.5, size=k))
        tx_info_bits = [0]*k
        
        
        
        # this is the encoder.  there are some non-pythonic optimizations here.
        encoding = []  # represents encoding structure in terms of info bits indices
        info_to_enc = dict() # this is a reverse LUT to find encoder symbols that are connected to info bits
        enc_bits = []  # represents encoded symbols
        degrees = rs_rv.rvs(size=max_enc_bits)
        info_indices = range(k)
        for i in range(max_enc_bits):
            degree = degrees[i]
            info_bits = rd.sample(info_indices, degree)
            encoding.append(info_bits)
            enc_bits.append(sum([tx_info_bits[x] for x in encoding[i]])%2)
            for ib in info_bits:
                if ib not in info_to_enc:
                    info_to_enc[ib] = []
                info_to_enc[ib].append(i)
        
        
        rx_info_bits = [None]*k
        rx_enc_bits = []
        decoding = list(encoding)
        decoded = 0
        for i in range(max_enc_bits):
            rx_enc_bits.append(enc_bits.pop(0))
        
            ripple = set([i])
            while ripple:
                j = ripple.pop()
                if len(decoding[j]) == 1:
                    ib = decoding[j][0]
                    if rx_info_bits[ib] is None:
                        decoded += 1
                        ripple.update([x for x in info_to_enc[ib] if x <= i])
                        rx_info_bits[ib] = rx_enc_bits[j]
        
                else:
                    for nb in decoding[j]:
                        if rx_info_bits[nb] is not None:
                            rx_enc_bits[j] += rx_info_bits[nb]
                            rx_enc_bits[j] %= 2
                            decoding[j].remove(nb)
                            ripple.add(j)
        
            symbols_required = i+1
            #file.write(' '.join((str(b), "e")[b is None] for b in rx_info_bits) + '\n')
            if decoded == k:
                break
        

        matched = True
        for i in range(k):
            if tx_info_bits[i] != rx_info_bits[i]:
                matched = False
        
        print symbols_required
        sys.stdout.flush()
        if matched is False and symbols_required < max_enc_bits:
            print "failed"
    
