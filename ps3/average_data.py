#!/usr/bin/env python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('data_files', nargs='+',
                           help='data files to be averaged')

args = parser.parse_args()
num_files = len(args.data_files)
sum_data = None
for path in args.data_files:
    with open(path) as f:
        probs = f.readline().split()
        data = [float(x) for x in f.readline().split()]
        if sum_data is None:
            sum_data = [0]*len(data)
        sum_data = [ sum(x) for x in zip(data, sum_data) ]

avg_data = [x/float(num_files) for x in sum_data]
print " ".join(probs)
print " ".join([str(x) for x in avg_data])
