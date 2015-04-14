#!/usr/bin/env python

import random as rd
import math

k = 1E4
c = 0.01
delta = 0.5

#as follows. First, let R = c√k ln(k/δ)
R = c * math.sqrt(k) * math.ln(k/delta)

def ideal_soliton():
    pass



print R
