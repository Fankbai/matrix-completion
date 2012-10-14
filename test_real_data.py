# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 09:19:57 2012

@author: Fela Winkelmolen

Tests using the data from http://archive.ics.uci.edu/ml/datasets/SPECTF+Heart
"""

import scipy as sp
import scipy.linalg
from matrixgeneration import *
import matrixdecomposition as md


#############################################################
class Experiment:
    def __init__(self, **opt):
        # default values
        self.filename = opt.pop('filename', None) or 'SMALL'
        self.seed = opt.pop('seed', None) or 0
        self.holes = opt.pop('holes', None) or 0.2 # holes percentage
        self.completion = opt.pop('completion', None) or 'matrix'
        
        self.options = opt
        self.generate_matrix()

    def run(self):
        self.generate_mask()
        TH, GA = self.TH, self.GA
        Y, Mask = self.Y, self.mask
        #print Mask
        A = self.matrix_completion()
        #print TH*Mask
        #print A
        diff = (TH-A)#*(1-Mask)
        #print diff
        #print Mask.sum()
        error = sqrt((diff**2).sum() / TH.size)
        return error
    
    def matrix_completion(self):
        if self.completion == 'matrix':
            res, _ = md.matrix_decomposition(self.Y, self.mask, **self.options)
        elif self.completion == 'mean':
            means = self.Y.mean(0) # means along the column axis
            # calculate the true means along the column axis
            # using only the values in the mask
            rows, cols = self.Y.shape
            means = sp.zeros(cols)
            # calculate the true means along the column axis
            # using only the values in the mask
            for c in range(cols):
                sum = 0.0
                n = 0
                for r in range(rows):
                    if self.mask[r][c]:
                        sum += self.Y[r][c]
                        n += 1
                if n == 0:
                    means[c] = 0
                else:
                    means[c] = sum/n
            
            #print means
            res = double(self.Y)
            for r in range(rows):
                for c in range(cols):
                    if not self.mask[r][c]:
                        res[r][c] = means[c]
        return res
        
    
    # called once after initialization
    def generate_matrix(self):
        filename = 'data/' + self.filename + '.train'
        self.TH, _ = self.load_data(filename)
        self.GA = self.TH * 0
        self.Y = self.TH + self.GA
    
    def generate_mask(self, holes=None):
        if holes:
            self.holes = holes
        rows, cols = self.GA.shape
        if self.seed != None:
            seed(self.seed)
        self.mask = rand(rows,cols) > self.holes    
    
    @staticmethod
    def load_data(filename):
        M = [[int(i) for i in line.split(',')] for line in open(filename)]
        M = sp.array(M)
        y = M[:, 0]
        X = M[:, range(1, M.shape[1])]
        return (X, y)

def hole_experiment(**opt):
    n = opt.pop('steps', None) or 5
    runs = opt.pop('runs', None) or 1
    label = opt.pop('label', None)
    #opt['mu_d'] = 0
    y = sp.array(range(n+1)) / float(n)
    x = []
    for holes in y:
        print '.',
        acc = []
        e = Experiment(**opt)
        for i in range(runs):
            e.generate_mask(holes)
            acc.append(e.run())
        x.append(sp.array(acc).mean())
    plot(y, x, label=label)
    legend(loc=0)

def param_experiment(param_name, params, **opt):
    label = opt.pop('label', None) or param_name
    x = []
    for p in params:
        opt[param_name] = p
        e = Experiment(**opt)
        x.append(e.run())
    print x
    plot(params, x, label=label)
    legend(loc=0)


# example experiment
#hole_experiment(steps=15, alpha=100000, mu_d=1, completion='mean', seed=10, label='mean')
param_experiment('mu_d', [0, 0.3, 0.6, 0.9, 1.2], alpha=100000)
#param_experiment('alpha', [1, 2, 3, 4, 5, 6], alpha=100000)