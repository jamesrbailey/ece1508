#!/usr/bin/env python

import random

def integral_1_0(degs):
    return sum([lda/float(i) for i,lda in degs.iteritems()])

n = 1200
var_degs = {2: 0.41219295, 3: 0.17736197, 4: 0.11853289, 7: 0.10937977, 8: 0.18253242}
chk_degs = {6: 1}
#var_degs = {02 : 0.33863999, 03 : 0.14245879, 04 : 0.096385821, 06 : 0.11922015, 07 : 0.071134724, 15 : 0.064873236, 16 : 0.16728729}
#chk_degs = {7: 1}
#var_degs = {02: 0.2879355, 03: 0.12254115, 04: 0.088188941, 05: 0.0011121546, 06: 0.12907345, 07: 0.013984156, 12: 0.11254155, 13: 0.055905012, 33: 0.18871809}
#chk_degs = {8: 1}

l_avg = 1./integral_1_0(var_degs)
r_avg = 1./integral_1_0(chk_degs)

chk_nodes = int(n*l_avg/r_avg)
design_rate = 1-l_avg/r_avg
#print "l_avg %f" % l_avg
#print "r_avg %f" % r_avg
#print "check nodes %d" % chk_nodes
#print "design_rate %f" % design_rate

var_sockets = []
var_deg_count = {degree: 0 for degree in var_degs.keys()}
for v in range(1,n+1):
    p = float(v)/float(n)

    cdf = 0.
    for degree,lda in var_degs.iteritems():
        cdf += lda
        if p < cdf:
            break
    #print "v%d has degree %d" %(v,degree)
    var_sockets += [v]*degree
    var_deg_count[degree] += 1

#print var_deg_count

random.shuffle(var_sockets)
for i in range(chk_nodes):
    for j in range(chk_degs.keys()[0]):
        print var_sockets.pop(),
    print 
        
