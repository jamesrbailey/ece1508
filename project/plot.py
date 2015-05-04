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
    mean = np.convolve(x, weights, 'same')
    return mean

def plot_file(filepath, label=None):
    data = np.genfromtxt(filepath,dtype=float,delimiter=" ")
    x_data = data[0]
    y_data = data[1]

    #window = 3
    #y_data = running_mean(y_data,window)
    print y_data,x_data

    #shrink = int(window-1)
    #x_data = x_data[shrink:-shrink]
    #y_data = y_data[shrink:-shrink]
    plt.plot(x_data, y_data, linewidth=2, label=label)

def plot_show(name, x_label, legend=None):

    plt.grid(b=True, which='major', color='grey', linestyle='--')
    plt.grid(b=True, which='minor', color='grey', linestyle='--')
    if legend:
        plt.legend(title=None, loc="lower right")
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel("Word error rate")
    plt.yscale("log")
    plt.show()


plot_file("results/m1024/base.data", label=r'(3,6)-regular base code')
plot_file("results/m1024/pd_l64.data", label=r'SC-LDPC BP')
plt.ylim([1E-5,1E0])
plot_show(name="Spatial-Coupling Gain of (3,6)-regular LDPC", x_label="Erasure Probability", legend="Decoder")

plot_file("results/m1024/pd_l64.data", label=r'BP')
plot_file("results/m1024/wd_w1_l64.data", label=r'$w=1$')
plot_file("results/m1024/wd_w2_l64.data", label=r'$w=2$')
plot_file("results/m1024/wd_w4_l64.data", label=r'$w=4$')
plot_file("results/m1024/wd_w8_l64.data", label=r'$w=8$')
plt.ylim([1E-5,1E0])
plot_show(name="Window Decoder Performance of SC-LDPC", x_label="Erasure Probability", legend="Decoder")

plot_file("results/m2500/wd_w1_l64.data", label=r'$w=1$')
plot_file("results/m2500/wd_w2_l64.data", label=r'$w=2$')
plot_file("results/m2500/wd_w4_l64.data", label=r'$w=4$')
plot_file("results/m2500/wd_w8_l64.data", label=r'$w=8$')
plt.ylim([1E-5,1E0])
plot_show(name="Window Decoder Performance of SC-LDPC, $n=2500$", x_label="Erasure Probability", legend="Decoder")

