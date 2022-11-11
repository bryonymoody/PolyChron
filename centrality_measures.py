#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 17:19:33 2022

@author: bryony
"""
import pandas as pd
import automated_mcmc_ordering_coupling_copy as mcmc
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import os
CALIBRATION_DATA = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)
#katz
# dd = nx.pagerank(G, alpha=0.85, personalization=None, max_iter=100, tol=1e-06, nstart=None, weight='weight', dangling=None)
# df = pd.DataFrame.from_dict(dd, orient = 'index')


def prob_from_samples(x_temp, A, P, lim=0.95, probs=0):
  if probs == 0:
      x_temp = np.array(x_temp)
      n = P - A + 1
      probs, x_vals = np.histogram(x_temp, range = (A, P), bins=n, density=1)
  df = pd.DataFrame({'Theta':x_vals[1:], 'Posterior':probs})
  y = df.sort_values(by=['Theta'], ascending=False)
  posterior_x = np.array(y['Posterior'])
#  posterior_theta = np.array(y['Theta']) 
  return posterior_x


def prob_overlap(ll1, ll2):
  ### hellenger distance
    dist_probs = np.array([(np.sqrt(ll2[i])-np.sqrt(j))**2 for i,j in enumerate(ll1)])
    h = 1 - 1/np.sqrt(2)*(np.sqrt(np.sum(dist_probs)))
    return h 

P = 10000
A = 0

# print(df[0])
path = os.getcwd()
graph_tests = [x for x in os.listdir(path) if "graph_theory" in x] # gets all the models
reference_model = pd.read_csv(path + "/77_78_sequence/mcmc_results/full_results_df" ) #needs automating for any project
#reference_model = pd.read_csv(path + "/reference_model/mcmc_results/full_results_df" ) #needs automating for any project
paramters = list(reference_model.columns) # gets all the paramters for the reference model
new_ref_df = pd.DataFrame() #empty df for reference model data
for j in reference_model.columns[1:]:
    new_ref_df[j] = prob_from_samples(reference_model[j], A, P) #gets all the psoterior probabilites 
df_dict = {} # dictionary to store the posterior model dataframes
df_dict['ref_model'] = new_ref_df # adding reference model to the dict

#adds the df of posterior distributions for all the other models
for i in graph_tests:
     df_res = pd.read_csv(path + "/" + str(i) + "/mcmc_results/full_results_df" )
     new_df = pd.DataFrame()
     for j in df_res.columns[1:]:
         new_df[j] = prob_from_samples(df_res[j], A, P)
     df_dict[i] = new_df 

overlap_metrics = {} # empty dict for overlap of posteriors for all the difference models
for k in df_dict.keys():
    label = k.replace("graph_theory_tests_", "") # gets the label i.e. the context that has been removed
    cols = df_dict[k].columns #for all the different models it gets the parameters
    df = df_dict[k] #and the data frame
    ref_cols = df_dict['ref_model'].columns # gets the parameters for the reference model
    ref_df = df_dict['ref_model'] # and the dataframe for the reference model
    mode_metrics = {} #empty divt to store the overlap metrics for each df
    ave_list = [] # store all overlap metrics so we can find an average
    for i in cols:
        if "=" in i: #if one parameter we split it into two
            x = i.split(" = ")
            ll1_a = df[i] #gets the df for each one 
            ll1_b = df[i] # this is the same dataframe as they are equivelent in time 
            c_a = [j for j in ref_cols if x[0] in j] # gets the parameter from the reference model for comparison
            ll2_a = ref_df[c_a[0]] # and its dataframe
            mode_metrics[x[0]]  = prob_overlap(list(ll1_a), list(ll2_a)) # gets the overlap metric
            ave_list.append(mode_metrics[x[0]]) #stores so we can find the average later
            c_b = [j for j in ref_cols if x[1] in j] # as above
            ll2_b = ref_df[c_b[0]]
            mode_metrics[x[1]]  = prob_overlap(list(ll1_b), list(ll2_b))
            ave_list.append(mode_metrics[x[1]])
        else:
            ll1 = df[i] # if only one parameter just get the df right away
            c = [j for j in ref_cols if i in j]#find equivalent in reference model
            ll2 = ref_df[c[0]] # then all as above
            mode_metrics[i]  = prob_overlap(list(ll1), list(ll2))
            ave_list.append(mode_metrics[i])
    mode_metrics['average'] = np.mean(ave_list)
    overlap_metrics[label] = mode_metrics   
    
    
katz_df = pd.read_csv("katz_centr.csv") # katz centrality worked out for the reference model
katz_df = katz_df.transpose()
katz_df = pd.DataFrame(katz_df.values[1:], columns = katz_df.iloc[0]) 

ll_over_df = pd.read_csv("overlap_df.csv")
ll_over_df = pd.DataFrame(ll_over_df[['node', 'neighbour', 'overlap_measure']]) #overlap df for the reference model


#test 1
katz_list = []
overlap_list = []
scalar_list = []
for i in overlap_metrics.keys():
    if i != "ref_model":
        katz_list.append(katz_df[i][0])
        overlap_list.append(overlap_metrics[i]['average'])
        ol_df = ll_over_df[ll_over_df['node'] == i]
        scalar = sum([katz_df[j][0]*(1-list(ol_df['overlap_measure'])[i]) for i, j in enumerate(ol_df['neighbour'])])/sum([katz_df[j][0] for j in ol_df['neighbour']])
        scalar_list.append(scalar*katz_df[i][0])

new_metric_list = [value[1] - value[0] for value in zip(scalar_list, katz_list)]

#test2 
katz_list = []
overlap_list = []
scalar_list = []
for i in overlap_metrics.keys():
    if i != "ref_model":
        katz_list.append(katz_df[i][0])
        overlap_list.append(overlap_metrics[i]['average'])
        ol_df = ll_over_df[ll_over_df['node'] == i]
        scalar = sum(ol_df['overlap_measure'])/len(ol_df)
        scalar_list.append(scalar*katz_df[i][0])

new_metric_list = [sum(value) for value in zip(scalar_list, katz_list)]


plt.figure(figsize=(8,6))
ax = plt.subplot(111)
ax.scatter(katz_list, overlap_list)
#ax.set_xlim(0.06, 0.28)
#ax.set_ylim(0.6, 1)
  
#test 3 only looking at phase boundaries
#test2 
katz_list = []
overlap_list = []
scalar_list = []
for i in overlap_metrics.keys():
    if (i != "ref_model") and (i != 'CH94'):
        print(i)
        katz_list.append(katz_df[i][0])
        overlap_list.append(np.average([overlap_metrics[i]['a_s_m'], overlap_metrics[i]['b_sth_area']]))
        ol_df = ll_over_df[ll_over_df['node'] == i]
        scalar = sum(ol_df['overlap_measure'])/len(ol_df)
        scalar_list.append(scalar*katz_df[i][0])

new_metric_list = [sum(value) for value in zip(scalar_list, katz_list)]

#test 4 
katz_list = []
overlap_list = []
scalar_list = []
for i in overlap_metrics.keys():
    if (i != "ref_model") :
        katz_list.append(katz_df[i][0])
        overlap_list.append(np.average([overlap_metrics[i]['a_ae'], overlap_metrics[i]['b_l']]))
        ol_df = ll_over_df[ll_over_df['node'] == i]
        i_f = []
        for l,m in enumerate(ol_df['overlap_measure']):
            if m < 0.25:
                i_f.append(0)
            elif (m >= 0.25) and (m < 0.75):
                i_f.append(1)
            else :
                i_f.append(2)      
        scalar = sum(i_f)/len(ol_df)
        scalar_list.append(scalar*katz_df[i][0])

new_metric_list = [sum(value) for value in zip(scalar_list, katz_list)]
annotations = [i for i in overlap_metrics.keys() if (i != "ref_model")]

plt.figure(figsize=(8,6))
ax = plt.subplot(111)
ax.scatter(new_metric_list, overlap_list)
for i, label in enumerate(annotations):
    ax.annotate(label, (new_metric_list[i], overlap_list[i]))
#ax.set_xlim(0.06, 0.2)






## overlap of likelihoods
# plt.figure(figsize=(8,6))
# ll1 = mcmc.likelihood_func(1000, 50, 250,  2000, CALIBRATION_DATA)
# ll2 = mcmc.likelihood_func(1010, 50, 250,  2000, CALIBRATION_DATA)
# ll3 = mcmc.likelihood_func(1500, 50, 250,  2000, CALIBRATION_DATA)
# plt.hist(ll1[0], weights = ll1[1], bins=len(ll1[1])+1,
#            alpha=0.7, density=True)
# plt.hist(ll2[0], weights = ll2[1], bins=len(ll2[1]) +1,
#            alpha=0.7, density=True)
def test_func():
    oxcal = []
    n_list = []
    hel_dist = []
    bc_list = []
    kl_list = []
    for i in range(1000, 1400):
        print(i)
        ll1 = mcmc.likelihood_func(1000, 50, 250,  2000, CALIBRATION_DATA)
        ll2 = mcmc.likelihood_func(i, 50, 250,  2000, CALIBRATION_DATA)
        #oxcal agreement indicies
        a = np.sum(np.array(ll1[1])*np.array(ll2[1]))
        b = np.sum(np.array(ll2[1])*np.array(ll2[1]))
        oxcal.append(a/b)
        
        ###pastore and calgoni 2019
        min_probs = [min(ll2[1][i], j) for i,j in enumerate(ll1[1])]
        n = np.sum(np.array(min_probs))
        n_list.append(n)
        
        ### hellenger distance
        dist_probs = np.array([(np.sqrt(ll2[1][i])-np.sqrt(j))**2 for i,j in enumerate(ll1[1])])
        h = 1/np.sqrt(2)*(np.sqrt(np.sum(dist_probs)))
        hel_dist.append(1-h)
        
        #Bhattacharyya coeff
        bc_probs = np.array([np.sqrt(ll2[1][i]*j) for i,j in enumerate(ll1[1])])
        bc = np.sum(bc_probs)
        bc_list.append(bc)
        
        #KL distance
        KL_dist = np.array([j*np.log(j/ll2[1][i]) for i,j in enumerate(ll1[1])])
        kl = np.sum(KL_dist)
        kl_list.append(kl)
    return oxcal, n_list, hel_dist, bc_list, kl_list

oxcal, n_list, hel_dist, bc_list, kl_list = test_func()
    

#### earth movers distnce
#F_ll1 = np.cumsum(np.array(ll1[1]))
#F_ll2 = np.cumsum(np.array(ll2[1]))
#F_ll3 = np.cumsum(np.array(ll3[1]))


#emd = np.sum(np.abs(F_ll1 - F_ll2))
#print(emd)
dates = range(1000,1400)
plt.figure(figsize=(8,6))
ax = plt.subplot(111)
#plt.plot(dates, oxcal)
ax.plot(dates, n_list)
ax.plot(dates, hel_dist)
ax.plot(dates, bc_list)
#ax.plot(dates,kl_list)
#ax.set_xlim(1000, 1400)
plt.show()