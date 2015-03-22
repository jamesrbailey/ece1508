#!/usr/bin/env python

from pulp import *

#rho_exp = [5., 6., 7.]

def optimize(rho):
    def try_threshold(epsilon, rho):
        rho_exp = [rho]

        def rho(x):
            return sum([(1./float(len(rho_exp)))*x**exp for exp in rho_exp])
        
        prob = LpProblem("Erasure threshold maximization",LpMaximize)
        
        l_min = 2
        l_max = 40
        
        lambdas = dict()
        for i in range(l_min,l_max+1):
            lambdas[i] = LpVariable("lambda_%02d"%i,0,1)
        
        #print lambdas
        prob += sum([l/float(i) for i, l in lambdas.iteritems()])
        
        m = 40  # divide continuous f(e,x) < x  into 100 discrete constraints
        
        for j in range(1,m+1):
            x_j = float(j) * epsilon / float(m)
            prob += sum([lambdas[i]*epsilon*(1-rho(1-x_j))**(float(i)-1) for i,l in lambdas.iteritems()]) <= x_j, "threshold %d"%j 
        
        prob += epsilon*lambdas[2] * sum(rho_exp)/float(len(rho_exp)) <= 1.
        #print prob
        prob += sum(lambdas.values()) == 1.
        
        
        prob.solve()
        #print "Status:", LpStatus[prob.status]
        
        
        
        design_rate = 1 - sum([(1/float(len(rho_exp)))/(float(i)+1) for i in rho_exp])/sum([l.varValue/float(i) for i,l in lambdas.iteritems()])
        return design_rate, lambdas

    t_min = 0.3
    t_max = 0.6
    r_final = 0.5
    for i in range(20):
        t = (t_max+t_min)/2.
        (rate, lambdas) = try_threshold(t, rho)
        print rate
        if abs(rate-r_final) <1E-4:
            break
        if rate < r_final:
            #print "decrease t"
            t_max = t
        else:
            #print "increase t"
            t_min = t

    
    for i,l in lambdas.iteritems():
        if l.varValue > 1E-6:
            print l.name, "=", l.varValue
    print "design rate: %f" % rate
    print "epsilon: %f" % t


optimize(6)
