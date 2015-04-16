#!/usr/bin/env python

from pulp import *

class LDPC_opt:
    def __init__(self):
        self.rho_exp = [5]
        self.l_min = 2
        self.l_max = 100
        self.m = 40
        
        self.lambdas = None

    def rho(self, x):
        return sum([(1./float(len(self.rho_exp)))*x**exp for exp in self.rho_exp])

    def optimize_lambda(self, epsilon):
        self.lambdas = dict()
        for i in range(self.l_min,self.l_max+1):
            self.lambdas[i] = LpVariable("lambda_%02d"%i,0,1)

        prob = LpProblem("Erasure threshold maximization",LpMaximize)
        prob += sum([l/float(i) for i, l in self.lambdas.iteritems()])
        
        for j in range(1,self.m+1):
            x_j = float(j) * epsilon / float(self.m)
            prob += sum([self.lambdas[i]*epsilon*(1-self.rho(1-x_j))**(float(i)-1) for i,l in self.lambdas.iteritems()]) <= x_j, "threshold %d"%j 
        
        prob += epsilon*self.lambdas[2] * sum(self.rho_exp)/float(len(self.rho_exp)) <= 1.
        prob += sum(self.lambdas.values()) == 1.
        
        prob.solve()

    def optimize_for_rate(self, target_rate):
        self.l_max = 100
        t_min = 0.1
        t_max = 1.0
        while True:
            t = (t_max+t_min)/2.
            ensemble.optimize_lambda(t)
            design_rate = ensemble.design_rate
            #print design_rate

            # dynamic l_max optimizer
            l_biggest = 0
            for i,l in ensemble.lambdas.iteritems():
                if l.varValue > 0:
                    l_biggest = max(l_biggest, i)

            if abs(design_rate-target_rate) <1E-4 and self.l_max != l_biggest:
                break
            if design_rate < target_rate:
                t_max = t
            else:
                t_min = t

            self.l_max = int((self.l_max + l_biggest)/2. + 1)
            if t == t_min:
                break
        return t
        
    @property
    def design_rate(self):
        design_rate = 1 - sum([(1/float(len(self.rho_exp)))/(float(i)+1) for i in self.rho_exp])/sum([l.varValue/float(i) for i,l in self.lambdas.iteritems()])
        return design_rate

    def print_info(self):
        for i,l in self.lambdas.iteritems():
            if l.varValue > 0:
                print l.name, "=", l.varValue
        print "design rate: %f" % self.design_rate


ensemble = LDPC_opt()

ensemble.rho_exp = [5]
t = ensemble.optimize_for_rate(0.5)
ensemble.print_info()
print "epsilon: %f" % t

ensemble.rho_exp = [6]
t = ensemble.optimize_for_rate(0.4)
ensemble.print_info()
print "epsilon: %f" % t

ensemble.rho_exp = [7]
t = ensemble.optimize_for_rate(0.3)
ensemble.print_info()
print "epsilon: %f" % t
