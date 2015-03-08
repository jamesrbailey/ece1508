#!/usr/bin/env python

import matplotlib.pyplot as plt

def plot_files(name, ex_file, spa_file, x_label):
    with open(ex_file) as f:
        wers = f.readline().strip().split(",")
        ps = f.readline().strip().split(",")
    bsc_ex = plt.plot(ps, wers, 'bs', label="Exhaustive")
    
    with open(spa_file) as f:
        wers = f.readline().strip().split(",")
        ps = f.readline().strip().split(",")
    plt.plot(ps, wers, 'g^', label="SPA")
    plt.legend()
    plt.title(name)
    plt.xlabel(x_label)
    plt.ylabel("Word error rate")
    plt.show()

plot_files("Hamming [7,4] on BSC Channel", "bsc_ex.data", "bsc_spa.data", "Symbol crossover probability")
plot_files("Hamming [7,4] on BEC Channel", "bec_ex.data", "bec_spa.data", "Symbol erasure probability")
plot_files("Hamming [7,4] on AWGN Channel", "awgn_ex.data", "awgn_spa.data", "Symbol SNR")

