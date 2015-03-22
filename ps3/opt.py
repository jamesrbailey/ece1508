#!/usr/bin/env python

from pulp import *

rho_exp = [5, 6, 7]
def rho(x):
    return sum([(1./float(len(rho_exp)))*x**exp for exp in rho_exp])

prob = LpProblem("Erasure threshold maximization",LpMaximize)

l_min = 2
l_max = 10

lambdas = dict()
for i in range(l_min,l_max+1):
    lambdas[i] = LpVariable("lambda_%02d"%i,0,1)

#print lambdas
prob += sum([l/float(i) for i, l in lambdas.iteritems()])

m = 200  # divide continuous f(e,x) < x  into 100 discrete constraints
epsilon = 0.402457
epsilon = 0.5

for j in range(1,m+1):
    x_j = float(j) * epsilon / float(m)
    prob += sum([lambdas[i]*epsilon*(1-rho(1-x_j))**(float(i)-1) for i,l in lambdas.iteritems()]) <= x_j, "threshold %d"%j 

prob += epsilon*lambdas[2] * sum(rho_exp)/3. <= 1.
#print prob
prob += sum(lambdas.values()) == 1.


prob.solve()
print "Status:", LpStatus[prob.status]


for i,l in lambdas.iteritems():
        print l.name, "=", l.varValue

design_rate = 1 - sum([(1/3.)/i for i in rho_exp])/sum([l.varValue/i for i,l in lambdas.iteritems()])
print "design rate: %f" % design_rate
print "epsilon: %f" % epsilon
