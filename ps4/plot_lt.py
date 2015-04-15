#!/usr/bin/env python
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import glob
from scipy import interpolate

matplotlib.rc('font', family='Computer Modern') 
matplotlib.rc('text', usetex=True)


def plot_file(filepath, label=None):
    data = np.genfromtxt(filepath,dtype=float,delimiter=",")
    x_data = data[0]
    y_data = data[1]
    plt.hist(x_data,y_data,histtype='step')

def plot_show(name, x_label, legend=None):

    plt.grid(b=True, which='major', color='grey', linestyle='--')
    plt.grid(b=True, which='minor', color='grey', linestyle='--')
    if legend:
        plt.legend(title=None, loc="lower left")
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel("Number encoded symbols")
    #plt.yscale("log")
    plt.show()

plot_file("results/lt_c0p01.data", label=r'$LP$')
plot_show(name="LT Performance, $c=0.01$", x_label="Crossover Probability", legend="Decode")

