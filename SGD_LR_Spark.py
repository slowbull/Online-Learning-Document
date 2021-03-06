
"""
author: Jonny

Reference： http://martin.zinkevich.org/publications/nips2010.pdf

Notation: Please run genData.py at first.
"""

from __future__ import print_function

import sys

import numpy as np
from pyspark import SparkContext


D = 20  # Number of dimensions
nclusters = 5 # number of cores
lr = 0.01 # learning rate

# Read a batch of points from the input file into a NumPy matrix object. We operate on batches to
# make further computations faster.
# The data file contains lines of the form <label>, <x1>, <x2>, ... , <xD>. We load each block of these
# into a NumPy array of size numLines * (D + 1) and pull out column 0 vs the others in gradient().
def readPointBatch(iterator):
    strs = list(iterator)
    matrix = np.zeros((len(strs), D + 1))
    for i, s in enumerate(strs):
        matrix[i] = np.fromstring(s.replace(',', ' '), dtype=np.float32, sep=' ')
    return [matrix]


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: logistic_regression <file> <iterations>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="PythonLR")
    points = sc.textFile(sys.argv[1],nclusters).mapPartitions(readPointBatch).cache()
    iterations = int(sys.argv[2])
    
    # Initialize w to a random value
    #w = 2 * np.random.ranf(size=D) - 1
    w = np.zeros(D)
    print("Initial w: " + str(w))

    # Compute logistic regression gradient for a matrix of data points
    def gradient(matrix, wi):
        Y = matrix[:, 0]    # point labels (first column of input file)
        X = matrix[:, 1:]   # point coordinates
        # For each point (x, y), compute gradient function, then sum these up
        idx = np.arange(len(Y))
        np.random.shuffle(idx)
        for i in idx:
            wi -= lr * (1+np.exp(-Y[i]*X[i].dot(wi)))**(-1) * np.exp(-Y[i]*X[i].dot(wi)) * (Y[i]*X[i])
        return wi
    
    def add(x, y):
        x += y
        return x

    def obj(matrix,w):
        Y = matrix[:,0]
        X = matrix[:,1:]
        loss = 0
        for i in range(len(Y)):
            loss += 1 / (1+np.exp(-Y[i]*X[i].dot(w)))
        return loss
    
    for i in range(iterations):
        print("On iteration %i" % (i + 1))
       # w = points.map(lambda m: gradient(m, w)).reduce(add)
        w = points.map(lambda m: gradient(m,w)).reduce(add)
        w = w / nclusters  
        sumloss = points.map(lambda m: obj(m,w)).reduce(add)  # calculate loss function value 
        
        print("w: " + str(w) + "\n")
        print("objective function {0}".format(sumloss))
        
    print("the end")
    sc.stop()
