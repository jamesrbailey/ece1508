#!/usr/bin/env python

import random

n = 1024
chk_deg = 6
var_deg = 3

chk_nodes = n*var_deg/chk_deg

var_sockets = range(1,n+1) * var_deg

random.shuffle(var_sockets)
for i in range(chk_nodes):
    for j in range(chk_deg):
        print var_sockets.pop(),
    print 
        
