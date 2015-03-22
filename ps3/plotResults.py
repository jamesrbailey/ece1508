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
    data = np.genfromtxt(filepath,dtype=float)
    x_data = data[0]
    for x in range(1,len(data[:,0])):
        window = 5
        y_data = data[1]
        #print y_data
        y_new = running_mean(y_data,window)
        x_new = np.linspace(x_data.min(), x_data.max(), y_new.shape[0])
        x_new = np.linspace(0.25, x_data.max(), y_new.shape[0])

        shrink = int(float(window)/2+2)
        x_new = x_new[shrink:-shrink]
        y_new = y_new[shrink:-shrink]
        plt.plot(x_new, y_new, linewidth=2, label=label)

def plot_show(name, x_label, legend=None):

    plt.grid(b=True, which='major', color='grey', linestyle='--')
    plt.grid(b=True, which='minor', color='grey', linestyle='--')
    if legend:
        plt.legend(title=None, loc="lower left")
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel("Bit error rate")
    plt.yscale("log")
    plt.show()

def plot_dir(dir):
    for path in glob.glob(dir+"/*.data"):
        plot_file(path, label="c1, r=5")

plot_dir("results/r5")
plot_show(name=r'$LDPC(1200, \lambda_{opt1}(x), x^5)$', x_label="Erasure Probability")

plot_dir("results/r6")
plot_show(name=r'$LDPC(1200, \lambda_{opt2}(x), x^6)$', x_label="Erasure Probability")

plot_dir("results/r7")
plot_show(name=r'$LDPC(1200, \lambda_{opt3}(x), x^7)$', x_label="Erasure Probability")

plot_file("results/avg_reg.data", label=r'$LDPC(1200, x^2, x^5)$')
plot_file("results/r5_avg.data", label=r'$LDPC(1200, \lambda_{opt1}(x), x^5)$')
plot_file("results/r6_avg.data", label=r'$LDPC(1200, \lambda_{opt2}(x), x^6)$')
plot_file("results/r7_avg.data", label=r'$LDPC(1200, \lambda_{opt3}(x), x^7)$')
plt.ylim([10E-6,1E0])
plot_show(name="Performance over 10 random codes", x_label="Erasure Probability", legend="Ensemble")
