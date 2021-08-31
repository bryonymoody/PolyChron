#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 15:49:17 2021

@author: bryony
"""
import pandas as pd
from random import sample
import numpy as np
#import automated_mcmc_ordering_coupling as mcmc
n = 6 #number of phases
m = 18 # number of contexts
A = 0#upper lim
P = 3600 #lower lim
CALIBRATION = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)
CONTEXT_NO = [str(i) for i in list(range(1,m+1))]

PHI_REF = []
f = []
for i in range(1,n+1):
    e = [i]*int((m/n))
    f = f + e
    PHI_REF.append(str(i))
    
KEY_REF = [str(i) for i in f]
KEY_REF.reverse()
PREV_PHASE = ['start'] + ['abuting']*(n-1)
POST_PHASE = ['abuting']*(n-1) + ['end']
STRAT_VEC = [[[], []]]*m
PHI_REF.reverse()
x = sample(range(A+100,P-100), n+1)
x.sort()
bounds = [x[0]]
for j in range(1, len(x)-1):
    bounds = bounds + [x[j]]*2
bounds = bounds + [x[len(x)-1]]  


unif_samp_dict = {}
phase_bounds = []
for a in range(0, len(bounds), 2):
    phase_bounds.append([bounds[a], bounds[a+1]])
    
for f, g in enumerate(PHI_REF):
    unif_samp_dict[g] = phase_bounds[f]
    
cal_samps = []   
for l in phase_bounds:
 #   print(range(l[0], l[1]))
      cal_samps = cal_samps + list(np.random.uniform(l[0], l[1], int(m/n)))    
cal_df = pd.DataFrame(cal_samps)
cal_df.to_csv("cal_list", index = False)
RCD_EST = [CALIBRATION["Carbon_year"][CALIBRATION["Calendar_year"] == int(i)].item() for i in cal_samps]
RCD_EST.reverse()    
RCD_ERR = [50]*m
TOPO_SORT = CONTEXT_NO

#mcmc.run_MCMC(CALIBRATION, STRAT_VEC, RCD_EST, RCD_ERR, KEY_REF, CONTEXT_NO, PHI_REF, PREV_PHASE, POST_PHASE, TOPO_SORT)

