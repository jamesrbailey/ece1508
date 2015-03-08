#!/usr/bin/env python
import numpy as np
import random as rd
import math
from scipy.stats import norm

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

def channel_bsc(x, p):
    out = np.array([(b,b^1)[rd.random() < p] for b in np.nditer(x)])
    #print x,"-->", out
    return out

def channel_bec(x, p):
    # Erasure is denoted by 0.5 output value. This works well with subsequent decoding.
    out = np.array([(b,0.5)[rd.random() < p] for b in np.nditer(x)])
    #print x,"-->", out
    return out

def channel_awgn(x, snr):
    N = 1 / (2*snr) # E_b is 0.5, since it is average energy of 0 and 1
    sigma = math.sqrt(N)
    out = np.array([b+rd.gauss(0,sigma) for b in np.nditer(x)])
    #print x,"-->", out
    return out


def testbench(decode, channel, channel_params, trials):
    word_error = []
    for k in channel_params:
        error_count = 0
        for t in range(trials):
            m = rd.randint(0,15)
            x = encoder[m]
            y = channel(x, k)
            x_hat = decode(y)
            errors = x_hat ^ x
            if np.count_nonzero(errors) > 0:
                error_count += 1
        word_error.append(error_count/float(trials))
    return word_error

class Variable:
    def __init__(self, _index, _init):
        self.index = _index
        self.init = _init
        self.checks = []
        self.inbox = dict()

    def send_messages(self):
        for check in self.checks: 
            message = self.init 
            if self.inbox:
                message += sum([u for (c, u) in self.inbox.items() if c != check])
            else:
                #print "Variable mailbox empty"
                pass

            check.inbox[self] = message
            #print "v%d sending message %f to c%d" % (self.index, message, check.index)
        #self.inbox.clear() # this is probably not required since every message will be overwritten

    @property
    def marginal(self):
        return sum(self.inbox.values()) + self.init

class Check:
    def __init__(self,index):
        self.index = index
        self.variables = []
        self.inbox = dict()

    def send_messages(self):
        for variable in self.variables: 
            if self.inbox:
                tanh_product = reduce(lambda x,y: x*y, [math.tanh(u/2) for (v, u) in self.inbox.items() if v != variable])
                # bounding the tanh product less than +-1
                if tanh_product >= 1:
                    tanh_product = 1-1E-6
                if tanh_product <= -1:
                    tanh_product = -1+1E-6
                message = 2*math.atanh(tanh_product)
            else:
                #print "Check mailbox empty"
                message = 0

            variable.inbox[self] = message
        #self.inbox.clear() # this is probably not required since every message will be overwritten

class SPA_graph:
    def __init__(self, y, k_channel, channel_type="bec"):

        # first instantiate all the check nodes
        self.checks = []
        for i in range(H.shape[0]):
            c = Check(i)
            self.checks.append(c)

        # now instantiate all the variable nodes
        self.variables = []
        for i in range(H.shape[1]):
            #print y
            if channel_type == "bsc":
                # In BSC our LLR is based on p(y=1|x=0) = p
                if y[i] == 0:
                    llr = math.log((1-k_channel)/(k_channel))
                elif y[i] == 1:
                    llr = math.log((k_channel)/(1-k_channel))
                else:
                    raise Exception("Expecting 1 or 0")
            elif channel_type == "bec":
                # In BEC our LLR approaches +/- infinity when we aren't erased
                if y[i] == 0:
                    llr = 1E6 # this is a large number
                elif y[i] == 1:
                    llr = -1E6 # this is a large
                elif y[i] == 0.5:
                    llr = 0
                else:
                    raise Exception("Expecting 0/1/0.5")
            elif channel_type == "awgn":
                # In AWGN the LLR starts as the ratio of the Q function on the distance from 0/1
                N = 1 / (2*k_channel) # E_b is 0.5, since it is average energy of 0 and 1
                sigma = math.sqrt(N)
                p0 = norm(0,sigma).pdf(y[i])  # these aren't normalized wrt each other
                p1 = norm(1,sigma).pdf(y[i])
                llr = math.log(p0/p1)


            #print "llr ", llr

            v = Variable(i,llr)  # TODO need to init properly
            self.variables.append(v)

            # connect appropriate checks to this variable and vice versa
            for j in range(H.shape[0]):
                if H[j][i] == 1:
                    c = self.checks[j]
                    v.checks.append(c)
                    c.variables.append(v)
                    #print "Connecting variable %d to check %d" % (i,j)

    def iterate(self):
        for check in self.checks:
            check.send_messages()

        for variable in self.variables:
            variable.send_messages()

        #print "iteration results: ",self.x_hat

    @property
    def x_hat(self):
        out = np.array([(0,1)[v.marginal < 0] for v in self.variables])
        return out


def decode_spa(y, channel_type, k_channel):
    graph = SPA_graph(y, k_channel=k_channel, channel_type=channel_type)
    x_hat_prev = None
    for i in range(5):
        graph.iterate()
        x_hat = graph.x_hat
        if x_hat_prev is not None:
            if np.count_nonzero(x_hat ^ x_hat_prev) > 0:
                #print "iteration %d: "%i,x_hat_prev,"-->",x_hat
                pass
        x_hat_prev = x_hat
    return graph.x_hat

def testbench(decode, channel, channel_type, channel_params, trials=200):
    word_error = []
    for k in channel_params:
        print "k=",k
        error_count = 0
        corrected = 0
        for t in range(trials):
            m = rd.randint(0,15)
            x = encoder[m]
            y = channel(x, k)
            x_hat = decode(y, channel_type, k_channel=k)
            errors = x_hat ^ x
            #print "result",x,"-->",y,"-->",x_hat
            if np.count_nonzero(errors) > 0:
                error_count += 1
            elif np.count_nonzero((y + x_hat)%2) >0:
                corrected += 1
        word_error.append(error_count/float(trials))
        #print "corrected %d @ %f" % (corrected, k)
    return word_error


params = np.logspace(start=-9., stop=0., num=120, base=2, endpoint=False)
wers = testbench(decode_spa, channel_bsc, "bsc", params)
with open("bsc_spa.data", "w") as f:
    f.write(",".join([str(r) for r in wers])+'\n')
    f.write(",".join([str(p) for p in params])+'\n')
print "bsc: ",wers

params = np.logspace(start=-9., stop=0., num=120, base=2, endpoint=False)
wers = testbench(decode_spa, channel_bec, "bec", params)
with open("bec_spa.data", "w") as f:
    f.write(",".join([str(r) for r in wers])+'\n')
    f.write(",".join([str(p) for p in params])+'\n')
print "bec: ",wers

params = np.logspace(start=3.0, stop=-4, num=120, base=2)
wers = testbench(decode_spa, channel_awgn, "awgn", params)
with open("awgn_spa.data", "w") as f:
    f.write(",".join([str(r) for r in wers])+'\n')
    f.write(",".join([str(p) for p in params])+'\n')
print "awgn: ",wers





