#!/usr/bin/env python
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rc('font', family='Computer Modern') 
matplotlib.rc('text', usetex=True)


def plot_file(filepath, label=None):
    data = np.genfromtxt(filepath,dtype=int)
    mean = int(np.mean(data))
    var = int(np.var(data))
    plt.hist(data, bins=50, histtype='step')
    plt.annotate('$\mu=%d ~~ \sigma^2=%d$'%(mean,var), xy=(0.9, 0.9), xycoords='axes fraction', fontsize=16,
                            horizontalalignment='right', verticalalignment='top')

def plot_show(name, x_label, legend=None):

    plt.grid(b=True, which='major', color='grey', linestyle='--')
    plt.grid(b=True, which='minor', color='grey', linestyle='--')
    if legend:
        plt.legend(title=None, loc="lower left")
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel("Occurences")
    #plt.yscale("log")
    plt.show()

plot_file("results/raptor.data", label=r'$LP$')
plot_show(name="Raptor Code Rate, $(3,6)-LDPC precode$", x_label="Number encoded symbols")

plot_file("results/raptor_just_lt.data", label=r'$LP$')
plot_show(name="LT Code Rate, no precode", x_label="Number encoded symbols")

plot_file("results/raptor_just_lt.data", label=r'$LP$')
plot_show(name="LT Code Rate, no precode", x_label="Number encoded symbols")

