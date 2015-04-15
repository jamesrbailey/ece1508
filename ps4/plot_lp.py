#!/usr/bin/env python
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import glob
from scipy import interpolate

matplotlib.rc('font', family='Computer Modern') 
matplotlib.rc('text', usetex=True)

def running_mean(x, N):
    weights = np.repeat(1.0, N)/N
    mean = np.convolve(x, weights, 'full')
    return mean

def plot_file(filepath, label=None):
    data = np.genfromtxt(filepath,dtype=float,delimiter=",")
    x_data = data[0]
    y_data = data[1]
    window = 1
    y_new = running_mean(y_data,window)
    x_new = np.linspace(x_data.min(), x_data.max(), y_new.shape[0])
    print y_new,x_new

    #shrink = int(float(window)/2+2)
    #x_new = x_new[shrink:-shrink]
    #y_new = y_new[shrink:-shrink]
    plt.plot(x_new, y_new, linewidth=2, label=label)

def plot_show(name, x_label, legend=None):

    plt.grid(b=True, which='major', color='grey', linestyle='--')
    plt.grid(b=True, which='minor', color='grey', linestyle='--')
    if legend:
        plt.legend(title=None, loc="lower left")
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel("Word error rate")
    plt.yscale("log")
    plt.show()


plot_file("results/bp_bec.data", label=r'$BP$')
plot_file("results/ml_bec.data", label=r'$ML$')
plot_file("results/lp_bec.data", label=r'$LP$')
plt.ylim([1E-4,1E0])
plot_show(name="Decoder Performance over BEC with [7,4] Hamming Code ", x_label="Erasure Probability", legend="Decode")

plot_file("results/bp_bsc.data", label=r'$BP$')
plot_file("results/ml_bsc.data", label=r'$ML$')
plot_file("results/lp_bsc.data", label=r'$LP$')
plt.ylim([1E-4,1E0])
plot_show(name="Decoder Performance over BSC with [7,4] Hamming Code ", x_label="Crossover Probability", legend="Decode")

