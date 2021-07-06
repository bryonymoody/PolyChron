#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 20:54:35 2020
@author: bryony
"""
import time
import random
import math
from statistics import mean
import numpy as np
import matplotlib.pyplot as plt
import pymc3 as pc  
import pandas as pd




def HPD_interval(x_temp, probs = 0):
    if probs == 0:
        x_temp = np.array(x_temp)
        n = math.ceil((x_temp.max() - x_temp.min()))
        probs, x_temp, _ = plt.hist(x_temp, bins = n, density= 1)
    df = pd.DataFrame({'Theta':x_temp[1:], 'Posterior':probs})     
    hpd_vec = []
    theta_vec = []
    y = df.sort_values(by = ['Posterior'], ascending = False)
    posterior_x = np.array(y['Posterior'])    
    posterior_theta = np.array(y['Theta'])
    i = 0
    while sum(hpd_vec) <= 0.95:
        hpd_vec.append(posterior_x[i])
        theta_vec.append(posterior_theta[i])
        i = i + 1    
    theta_vec.sort()
    rangevec = []
    rangevec.append(min(theta_vec))
    for i in range(len(theta_vec)-1):
        if theta_vec[i+1] - theta_vec[i] > 15:
            rangevec.extend([theta_vec[i], theta_vec[i+1]])
    rangevec.append(max(theta_vec))
    return rangevec

#import pymc3 as pm3
############### TO DO LIST #######
# automate checking of thetas and phis
# output historgrams with associated trace plots
# output table of HPD intervals
#import the calibration curve
def theta_samp_func(GIBBS_THETAS, GIBBS_PHIS, KEY_REF, PHI_REF, RESULT_VEC, STRAT_VEC, CONTEXT_NO, TOPO_SORT, iter_num, GIBBS_DICT_1): #, PREV_IT):
    """GIVES A LIST OF INITAL THETA VALUES FOR MCMCM"""
    out_vec = [0]*len(KEY_REF)  
#    print(GIBBS_THETAS)     
    for date in range(0, len(PHI_REF)):
        t0_f = time.perf_counter()
        ref_vec = np.where(np.array(KEY_REF) == PHI_REF[date])[0].tolist()  
        phase_lab = PHI_REF[date]
        phase = [CONTEXT_NO[i] for i in ref_vec]        
        phase_topo = [i for i in TOPO_SORT if i in phase]  
        phase_upp_lim = GIBBS_DICT_1[phase_lab]['boundaries'][1] # needs to be less than this
        phase_low_lim = GIBBS_DICT_1[phase_lab]['boundaries'][0] # needs to be more than this
        t1 = time.perf_counter() - t0_f
        for i in phase_topo:
            t0_f = time.perf_counter()
            #print(i)
            a = np.where(np.array(CONTEXT_NO) == i)[0][0].item()
            below = STRAT_VEC[a][0] # should be less than this
         #   print(type(below))
            above = STRAT_VEC[a][1] # should be greater than this
            t0_f = time.perf_counter()
         #   print('inital part of loop ' + str(t1))
            
            if len(above) == 0:
                if len(below) == 0: 
                    t0_f = time.perf_counter()
                    dates = RESULT_VEC[a][0]
               #     aa = np.where(dates == round(phase_upp_lim, 1))[0].tolist()
              #      dates_new = dates[0:aa]
               #     b = np.where(dates_new == round(phase_low_lim, 1))[0].tolist()
               #     dates_new = dates_new[b]
               #     print([aa,b])
                    ind =  (dates < phase_upp_lim) & (dates > phase_low_lim)
               #     print([max(up), min(up)])
                    crop = time.perf_counter() - t0_f
                    t0_g = time.perf_counter()
                    SAMPLE_VEC, SAMPLE_VEC_PROB = dates[ind], RESULT_VEC[a][1][ind]               
                    crop2 = time.perf_counter() - t0_g
               #     print('crop vecs ' + str(crop))
              #      print('crop vecs 2 ' + str(crop2))
                    ta = time.perf_counter()
                    w = SAMPLE_VEC_PROB/np.sum(SAMPLE_VEC_PROB) 
                    out_vec[a] = SAMPLE_VEC[np.searchsorted(w.cumsum(), random.random())] 
                    tb = time.perf_counter() - ta     
              #      print('sampling ' + str(tb))
                    totfun = time.perf_counter() - t0_f
             #       print('totfun ' + str(totfun))
                   # print("t1, t2, t3" + str([t1_f, t2_f, totfun]))
                else:
                    maxstrat = max([GIBBS_THETAS[np.where(np.array(CONTEXT_NO) == j)[0][0].item()][iter_num] for j in below])
                 #   print('iter_num' + str(iter_num))
                  #  print('context' + str(i))
                   # print(type(maxstrat)) 
                    #print(maxstrat)
                    max_tot = max([maxstrat, phase_low_lim])                           
                    SAMPLE_VEC = RESULT_VEC[a][0][(RESULT_VEC[a][0] < phase_upp_lim) & (RESULT_VEC[a][0] > max_tot)]
                    SAMPLE_VEC_PROB = RESULT_VEC[a][1][(RESULT_VEC[a][0] < phase_upp_lim) & (RESULT_VEC[a][0] > max_tot)]                
                    out_vec[a] = random.choices(SAMPLE_VEC, weights=SAMPLE_VEC_PROB/sum(SAMPLE_VEC_PROB))[0]                          
            elif len(below) == 0:
                minstrat = min([out_vec[np.where(np.array(CONTEXT_NO) == j)[0][0].item()] for j in above])
                min_tot = min([minstrat, phase_upp_lim])
                SAMPLE_VEC = RESULT_VEC[a][0][(RESULT_VEC[a][0] < min_tot) & (RESULT_VEC[a][0] > phase_low_lim)]
                SAMPLE_VEC_PROB = RESULT_VEC[a][1][(RESULT_VEC[a][0] < min_tot) & (RESULT_VEC[a][0] > phase_low_lim)]                
                out_vec[a] = random.choices(SAMPLE_VEC, weights=SAMPLE_VEC_PROB/sum(SAMPLE_VEC_PROB))[0]
            else:
                maxstrat = max([GIBBS_THETAS[np.where(np.array(CONTEXT_NO) == j)[0][0].item()][iter_num] for j in below])
              #  [print(GIBBS_THETAS[np.where(np.array(CONTEXT_NO) == j)[0][0].item()][iter_num]) for j in below]
              #  print('context' + str(i))
              #  print('iter_num' + str(iter_num))
              #  print(type(maxstrat))
              #  print(maxstrat)
                max_tot = max([maxstrat, phase_low_lim])
                minstrat = min([out_vec[np.where(np.array(CONTEXT_NO) == j)[0][0].item()] for j in above])
                min_tot = min([minstrat, phase_upp_lim])
                SAMPLE_VEC = RESULT_VEC[a][0][(RESULT_VEC[a][0] < min_tot) & (RESULT_VEC[a][0] > max_tot)]
                SAMPLE_VEC_PROB = RESULT_VEC[a][1][(RESULT_VEC[a][0] < min_tot) & (RESULT_VEC[a][0] > max_tot)]                
                out_vec[a] = random.choices(SAMPLE_VEC, weights=SAMPLE_VEC_PROB/sum(SAMPLE_VEC_PROB))[0]
         #   print('sampling ' + str(tb))
            t2 = time.perf_counter() - t0_f - t1
   #         print('whole loop ' + str(t2) + '\n')
        t1_f = time.perf_counter() - t0_f
  #      print(len(SAMPLE_VEC))
 #       print(phase_topo)
   #     print(t1_f)
  #  print([[out_vec[0] > out_vec[1]], [out_vec[1] > out_vec[2]], [out_vec[2] > out_vec[7]], [out_vec[7] > out_vec[8]], [out_vec[8] > out_vec[9]], [ out_vec[3] > out_vec[7]], [ out_vec[5] > out_vec[7]], [out_vec[4] > out_vec[5]], [out_vec[6] > out_vec[7]]])
 #   print(out_vec)
    return(out_vec)  
    

def phase_samp_func(key_reff, phi_reff, theta_vals, prev_phases, A, P, iter_num):
    """GIVES A LIST OF INITAL PHASE BOUNDARY VALUES FOR MCMCM"""
    PHASE_INITS = [] 
    KEY_REF_1 = np.array(key_reff)
    PHASE_INITS.append(np.random.uniform(max([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[0])[0].tolist()]), P))
    for j in range(1, len(phi_reff)):
    #    print(max([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j])[0].tolist()]))
    #    print(min([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j-1])[0].tolist()]))
        a_temp = np.random.uniform(max([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j])[0].tolist()]),
                                             min([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j-1])[0].tolist()]))
        if prev_phases[j] != "abuting":
           # print("TS")
            a_temp = [a_temp, (np.random.uniform(max([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j])[0].tolist()]),
                                 min([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j-1])[0].tolist()])))]
            a_temp = sorted(a_temp, reverse = True)
        else:
            a_temp = [a_temp]
        [PHASE_INITS.append(ref_ind) for ref_ind in a_temp]
        #print(PHASE_INITS)
    PHASE_INITS.append(np.random.uniform(min([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[-1])[0].tolist()]), A))
    #print(min([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[-1])[0].tolist()]))
    PHASE_INITS1 = sorted(PHASE_INITS, reverse=True)
    return PHASE_INITS1 

def sampling_vec(post_phase_vec, prev_phase_vec):
    """ gives vectors to sample between"""
    track_phase = []
    track_vec = []
    for i_samp, j_samp in enumerate(post_phase_vec):
        h_temp = prev_phase_vec[i_samp]
        f_temp = j_samp
        if h_temp == "abuting":
            track_phase.append("combined")
        elif h_temp == "overlap":
            if prev_phase_vec[i_samp-1] == "overlap":
                track_phase.append("overlap_upper")
            else:
                track_phase.append("upper")
            track_vec.append(i_samp)
        else:
            track_phase.append("upper")
            track_vec.append(i_samp)
        if f_temp == "abuting":
            pass
        elif f_temp == "overlap":
            if post_phase_vec[i_samp+1] == "overlap":
                track_phase.append("overlap_beta")
            else:
                track_phase.append("lower")
        else:
            track_phase.append("lower")
        track_vec.append(i_samp)
    return [track_phase, track_vec]

def phase_limits(phases, POST_PHASE):
    "provides phase limits for a phase"""
    upper = []
    lower = []
    i_phase = 0
    for a_val in enumerate(POST_PHASE):
        upper.append(phases[i_phase])
        i_phase = i_phase + 1
        lower.append(phases[i_phase])
        if a_val[1] != "abuting":
            i_phase = i_phase + 1
    phase_bounds = [list(x) for x in zip(lower, upper)]
    return phase_bounds

def accept_prob(accept_vec, phi_accept_vec):
    """Checks the acceptance rate for MCMC code"""
    probs = []
    for i_accept in accept_vec:
        probs.append(len(i_accept)/30000)
    for j_accept in phi_accept_vec:
        probs.append(len(j_accept)/30000)
    return np.array(probs)

def likeli(x_val, s_err, theta, CALIBRATION_DATA):
    """ calculates likelihood for a single value"""
    value_theta = math.exp(-((x_val-CALIBRATION_DATA["Carbon_year"][theta])**2)/
                           (2*(s_err**2 + CALIBRATION_DATA["Carbon_error"][theta]**2)))
    return value_theta

def likelihood_func(x_val, s_err, a_val, p_val, CALIBRATION_DATA):
    """likelihood over a range"""
    likelihood_vec = []
    for theta in range(a_val, p_val):
        value = likeli(x_val, s_err, theta, CALIBRATION_DATA)
        likelihood_vec.append(value)
    theta = np.array(range(a_val, p_val))
    intep_theta = np.linspace(a_val, p_val, ((p_val-a_val)*10)+1)
    interp_prob = np.interp(intep_theta, theta, likelihood_vec)
    prob = interp_prob/sum(interp_prob)
    lhood_df = [intep_theta, prob]
    return lhood_df

def strat_rel(site_dict, key, i_index, THETAS, CONTEXT_NO):
    """ gives nodes above and below a date"""
    upstrat = site_dict[key]["dates"][i_index][3][0]
    lowstrat = site_dict[key]["dates"][i_index][3][1]
    a_strat = [CONTEXT_NO.index(i) for i in upstrat]
    b_strat = [CONTEXT_NO.index(i) for i in lowstrat]
    if len(a_strat) > 0:
        stratup = min([THETAS[i] for i in a_strat])
    else:
        stratup = site_dict[key]["boundaries"][0]
    if len(b_strat) > 0:
        stratlow = max([THETAS[i] for i in b_strat])
    else:
        stratlow = site_dict[key]["boundaries"][1]
    return [stratlow, stratup]

def dict_seek_ordered(i_seek, key, site_dict, THETAS, CONTEXT_NO):
    """ calc probability in a dictionary"""
    llhood = site_dict[key]["dates"][i_seek][1]
    phase_len = site_dict[key]["boundaries"][1] - site_dict[key]["boundaries"][0] #phase length
    like1 = llhood[0:][0]
    alpha = site_dict[key]["boundaries"][1]
    beta = site_dict[key]["boundaries"][0]
    temp_vec = llhood[1:][0][(like1 <= site_dict[key]["boundaries"][1]) &
                             (like1 > site_dict[key]["boundaries"][0])]
    temp_vec_2 = llhood[1:][0][(like1 <= min(strat_rel(site_dict, key, i_seek, THETAS, CONTEXT_NO)[0], alpha)) &
                               (like1 > max(strat_rel(site_dict, key, i_seek, THETAS, CONTEXT_NO)[1], beta))]
    search = np.where(like1 == int(site_dict[key]["dates"][i_seek][0]))
    if len(search[0]) == 0:
        x_temp = 0
    else:
        ind_seek = search[0][0]
        v_seek = like1[ind_seek:ind_seek+11]
        res = min(enumerate(v_seek), key=lambda x: abs(site_dict[key]["dates"][i_seek][0] - x[1]))
        c_ind = np.where(like1 == res[1])
        x_temp = llhood[1:][0][c_ind[0]][0]
    x_len = (x_temp/phase_len)*(np.sum(temp_vec)/np.sum(temp_vec_2))
    return x_temp, x_len

def post_h(site_dict, THETAS, CONTEXT_NO):
    """calculates acceptance probability"""
    h_vec = [dict_seek_ordered(j[0], i, site_dict, THETAS, CONTEXT_NO)
             for i in site_dict.keys()
             for j in enumerate(site_dict[i]["dates"])]
    hh_1 = [i[0] for i in h_vec]
    hh_2 = [i[1] for i in h_vec]
    return hh_1, hh_2

def dict_seek_4(i_dict, key, site_dict):
    """ finds probabilities for all paramters in sample"""
    phase_len = site_dict[key]["boundaries"][0] - site_dict[key]["boundaries"][1]
    theta = site_dict[key]["dates"][i_dict][0]
    llhood = site_dict[key]["dates"][i_dict][1]
    ind_dic = np.where(llhood[0:][0] == int(theta))[0][0]
    li_vec = llhood[0:][0][ind_dic:ind_dic+11]
    res = min(enumerate(li_vec), key=lambda x: abs(theta - x[1]))
    c_vec = np.where(llhood[0:][0] == res[1])
    x_temp = llhood[1:][0][c_vec[0]][0]
    x_tot = x_temp/phase_len
    return x_temp, x_tot

def post_h_theta_phi_4(site_dict):
    """calculates posterior prob for step 4"""
    h_vec = [dict_seek_4(j[0], i, site_dict)
             for i in site_dict.keys()
             for j in enumerate(site_dict[i]["dates"])]
    hj_1 = [i[0] for i in h_vec]
    hj_2 = [i[1] for i in h_vec]
    return hj_1, hj_2

def dict_update(test_dict_2, post_t, post_p, inter, inter2, POST_PHASE, PHI_REF):
    """ updates site dictionary"""
    count = 0
    count_1 = 0
    b_lst = phase_limits([phi[inter2] for phi in post_p], POST_PHASE)
    for i_2 in PHI_REF:
        test_dict_2[i_2]["boundaries"] = b_lst[count_1]
        count_1 = count_1 + 1
        for j_up in enumerate(test_dict_2[i_2]["dates"]):
            test_dict_2[i_2]["dates"][j_up[0]][0] = post_t[count][inter]
            count = count + 1
    return test_dict_2

def phase_bd_init_func(key_reff, phi_reff, theta_initt, prev_phases, A, P):
    """GIVES A LIST OF INITAL PHASE BOUNDARY VALUES FOR MCMCM"""
    PHASE_INITS = [] 
    KEY_REF_1 = np.array(key_reff)
    PHASE_INITS.append(np.random.uniform(max([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[0])[0].tolist()]), P))
    for j in range(1, len(phi_reff)):
        a_temp = np.random.uniform(max([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[j])[0].tolist()]),
                                             min([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[j-1])[0].tolist()]))
        if prev_phases[j] != "abuting":
            a_temp = [a_temp, (np.random.uniform(max([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[j])[0].tolist()]),
                                 min([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[j-1])[0].tolist()])))]
            a_temp = sorted(a_temp, reverse = True)
        else:
            a_temp = [a_temp]
        [PHASE_INITS.append(ref_ind) for ref_ind in a_temp]
    PHASE_INITS.append(np.random.uniform(min([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[-1])[0].tolist()]), A))
    PHASE_INITS1 = sorted(PHASE_INITS, reverse=True)
    return PHASE_INITS1

def theta_init_func(KEY_REF1, PHI_REF1, RESULT_VEC1):
    """GIVES A LIST OF INITAL THETA VALUES FOR MCMCM"""
    out_vec = [0]*len(KEY_REF1)
    uplimref = np.where(np.array(KEY_REF1) == PHI_REF1[0])[0].tolist()
    up_lim_vec = [np.random.choice(RESULT_VEC1[date][0], p=RESULT_VEC1[date][1]).item() for date in uplimref]
    for i, a in enumerate(uplimref):
        out_vec[a] = up_lim_vec[i]
    prev_min = min(up_lim_vec)
    for date in range(1, len(PHI_REF1)):
        ref_vec = np.where(np.array(KEY_REF1) == PHI_REF1[date])[0].tolist()
        theta, prob = RESULT_VEC1[date][0], RESULT_VEC1[date][1]
        theta_vals = [np.random.choice(theta[theta < prev_min], 
                                       p=prob[theta < prev_min]/sum(prob[theta < prev_min])) for date in ref_vec]
        prev_min = min(theta_vals)
        for i, a in enumerate(ref_vec):
            out_vec[a] = theta_vals[i]
    return(out_vec)   
    
def theta_init_func_n(KEY_REF1, PHI_REF1, RESULT_VEC1, STRAT_VEC, P, CONTEXT_NO, TOPO_SORT):
    """GIVES A LIST OF INITAL THETA VALUES FOR MCMCM"""
    out_vec = [0]*len(KEY_REF1)       
    prev_min = P
    for date in range(0, len(PHI_REF1)):
        ref_vec = np.where(np.array(KEY_REF1) == PHI_REF1[date])[0].tolist()    
        phase = [CONTEXT_NO[i] for i in ref_vec]        
        phase_topo = [i for i in TOPO_SORT if i in phase]   
        for i in phase_topo:
            a = np.where(np.array(CONTEXT_NO) == i)[0][0].item()
            low = STRAT_VEC[a][1]
            if len(low) == 0:
                SAMPLE_VEC = RESULT_VEC1[a][0][RESULT_VEC1[a][0] < prev_min]
                SAMPLE_VEC_PROB = RESULT_VEC1[a][1][RESULT_VEC1[a][0] < prev_min]                
                out_vec[a] = np.random.choice(SAMPLE_VEC, p=SAMPLE_VEC_PROB/sum(SAMPLE_VEC_PROB))            
            else:
                minstrat = min([out_vec[np.where(np.array(CONTEXT_NO) == j)[0][0].item()] for j in low])
                SAMPLE_VEC = RESULT_VEC1[a][0][RESULT_VEC1[a][0] < min(minstrat, prev_min)]
                SAMPLE_VEC_PROB = RESULT_VEC1[a][1][RESULT_VEC1[a][0] < min(minstrat, prev_min)]
                out_vec[a] = np.random.choice(SAMPLE_VEC, p=SAMPLE_VEC_PROB/sum(SAMPLE_VEC_PROB))
        prev_min = min([d for d in out_vec if d != 0])
    return(out_vec) 
#sampling functions
def upp_samp_1(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """ upper sample 1"""
    limits = [max([theta_samp[i] for i, j in enumerate(KEY_REF) if
                   j == PHI_REF[SAMP_VEC_TRACK[m]]]), P]
    _ = phis_samp
    return limits

def upp_samp_2(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """ upper sample 2"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m+2])
    limits = [max(in_phase_dates), P]
    _ = phis_samp
    return limits

def upp_samp_3(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """ upper sample 3"""
    limits = [max([theta_samp[i] for i, j in enumerate(KEY_REF) if
                   j == PHI_REF[SAMP_VEC_TRACK[m]]]),
              min([theta_samp[i] for i, j in enumerate(KEY_REF)
                   if j == PHI_REF[SAMP_VEC_TRACK[m-1]]])]
    _ = phis_samp
    return limits

def upp_samp_4(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """ upper sample 4"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m-1]]]
    in_phase_dates.append(phis_samp[m+2])
    limits = [max(in_phase_dates),
              min([theta_samp[i] for i, j in enumerate(KEY_REF) if
                   j == PHI_REF[SAMP_VEC_TRACK[m]]])]
    return limits

def upp_samp_5(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """ upper sample 5"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m-1])
    limits = [max(in_phase_dates), phis_samp[m-2]]
    return limits

def upp_samp_6(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """ upper sample 6"""
    limits = [max([theta_samp[i] for i, j in enumerate(KEY_REF) if
                   j == PHI_REF[SAMP_VEC_TRACK[m]]]), phis_samp[m-1]]
    return limits

def upp_samp_7(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """ upper sample 7"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m+2])
    limits = [max(in_phase_dates), phis_samp[m-1]]
    return limits

def upp_samp_8(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """ upper sample 8"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m-1])
    limits = [max(in_phase_dates), phis_samp[m-3]]
    return limits

def low_samp_1(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """lower sample 1"""
    limits = [max([theta_samp[i] for i, j in enumerate(KEY_REF) if
                   j == PHI_REF[SAMP_VEC_TRACK[m+1]]]),
              min([theta_samp[i] for i, j in enumerate(KEY_REF) if j
                   == PHI_REF[SAMP_VEC_TRACK[m]]])]
    _ = phis_samp
    return limits

def low_samp_2(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """lower sample 2"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m-2])
    limits = [max([theta_samp[i] for i, j in enumerate(KEY_REF) if
                   j == PHI_REF[SAMP_VEC_TRACK[m+1]]]),
              min(in_phase_dates)]
    return limits

def low_samp_3(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """lower sample 3"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m+1])
    limits = [phis_samp[m+2], min(in_phase_dates)]
    return limits

def low_samp_4(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """lower sample 4"""
    limits = [phis_samp[m+1],
              min([theta_samp[i] for i, j in enumerate(KEY_REF) if
                   j == PHI_REF[SAMP_VEC_TRACK[m]]])]
    return limits

def low_samp_5(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """lower sample 5"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m-2])
    limits = [phis_samp[m+1], min(in_phase_dates)]
    return limits

def low_samp_6(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """lower sample 6"""
    limits = [A, min([theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]])]
    _ = phis_samp
    return limits

def low_samp_7(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """lower sample 7"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m-2])
    limits = [A, min(in_phase_dates)]
    return limits

def overlap_samp_1(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """overlap sample 1"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m-1])
    limits = [max(in_phase_dates), phis_samp[m-3]]
    return limits

def overlap_samp_2(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF):
    """overlap sample 2"""
    in_phase_dates = [theta_samp[i] for i, j in enumerate(KEY_REF) if
                      j == PHI_REF[SAMP_VEC_TRACK[m]]]
    in_phase_dates.append(phis_samp[m+1])
    limits = [phis_samp[m+3], min(in_phase_dates)]
    return limits

#sampling dictionary




#inputs to the code
#             [[], []], [[], []], [[], []], [[], []],
            # [[], []], [[], []], [[], []], [[], []], [[], []],
           #  [[], []]

##NOT SURE WHERE THIS DATA ARE FROM
#A = 18000
#P = 27000
#
#RCD_EST = [19320, 19380, 19050, 19510, 19410, 19150, 19280, 18920, 18860, 18590,
#           19020, 19180, 18730, 18620, 18660, 18640, 18730]
#RCD_ERR = [100, 100, 100, 110, 100, 110, 120, 110, 110,110, 110, 110, 110, 100, 100, 70, 110]
#
#THETA_INITS = [22050, 22150, 22100, 22200, 22400, 22300, 22600, 22850, 23100,23200,23300,23650,
#               23930,23950,23800,23850,23900]
#PHASE_BOUNDARY_INITS = [24000, 23750, 23500, 23250, 23000, 22750, 22500, 22250, 22000]
#
#KEY_REF = [8, 8, 8, 8, 8, 7, 6, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1]
#PHI_REF = [8, 7, 6, 5 ,4, 3, 2, 1]
#CONTEXT_NO =[1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11, 12,13,14,15,16,17]
#
#PREV_PHASE = ["start", "abuting", "abuting", "abuting", "abuting", "abuting", "abuting", "abuting"]
#POST_PHASE = ["abuting", "abuting", "abuting", "abuting", "abuting", "abuting", "abuting", "end"]
#########SHAG RIVER MOUTH
#np.random.seed(99999)


def run_MCMC(CALIBRATION, STRAT_VEC, RCD_EST, RCD_ERR, KEY_REF, CONTEXT_NO, PHI_REF, PREV_PHASE, POST_PHASE, TOPO_SORT):
  t0 = time.perf_counter()
  PHI_SAMP_DICT = {
            'upper' : {
                'start':{
                    'abuting':upp_samp_1,
                    'overlap':upp_samp_2,
                    'gap':upp_samp_1,
                    'end':upp_samp_1,
                    },
                'abuting':{
                    'abuting':upp_samp_3,
                    'overlap':upp_samp_4,
                    'gap':upp_samp_3,
                    'end':upp_samp_3
                    },
                'overlap':{
                    'abuting':upp_samp_5,
                    'overlap':upp_samp_5,
                    'gap':upp_samp_5,
                    'end':upp_samp_5
                    },
                'gap':{
                    'abuting':upp_samp_6,
                    'overlap':upp_samp_7,
                    'gap':upp_samp_6,
                    'end':upp_samp_6}
                    },
            'lower' :  {
                'start':{
                    'abuting':low_samp_1,
                    'overlap':low_samp_3,
                    'gap':low_samp_4,
                    'end':low_samp_6
                    },
                'abuting':{
                    'abuting':low_samp_1,
                    'overlap':low_samp_3,
                    'gap':low_samp_4,
                    'end':low_samp_6
                    },
                'overlap':{
                    'abuting':low_samp_2,
                    'overlap':low_samp_3,
                    'gap':low_samp_5,
                    'end':low_samp_7
                    },
                'gap':{
                    'abuting':low_samp_1,
                    'overlap':low_samp_3,
                    'gap':low_samp_4,
                    'end':low_samp_6
                    }
                },
            'combined' :  {
                'start':{
                    'abuting':low_samp_1,
                    'overlap':low_samp_3,
                    'gap':low_samp_4,
                    'end':low_samp_6
                    },
                'abuting':{
                    'abuting':low_samp_1,
                    'overlap':low_samp_3,
                    'gap':low_samp_4,
                    'end':low_samp_6
                    },
                'overlap':{
                    'abuting':low_samp_2,
                    'overlap':low_samp_3,
                    'gap':low_samp_5,
                    'end':low_samp_7
                    },
                'gap':{
                    'abuting':low_samp_1,
                    'overlap':low_samp_3,
                    'gap':low_samp_4,
                    'end':low_samp_6
                    }
                },
            'overlap_upper' :  {
                'start':{
                    'abuting':overlap_samp_1,
                    'overlap':overlap_samp_1,
                    'gap':overlap_samp_1,
                    'end':overlap_samp_1,
                    },
                'abuting':{
                    'abuting':overlap_samp_1,
                    'overlap':overlap_samp_1,
                    'gap':overlap_samp_1,
                    'end':overlap_samp_1,
                    },
                'overlap':{
                    'abuting':overlap_samp_1,
                    'overlap':overlap_samp_1,
                    'gap':overlap_samp_1,
                    'end':overlap_samp_1,
                    },
                'gap':{
                    'abuting':overlap_samp_1,
                    'overlap':overlap_samp_1,
                    'gap':overlap_samp_1,
                    'end':overlap_samp_1,
                    }
                },
            'overlap_beta' :  {
                'start':{
                    'abuting':overlap_samp_2,
                    'overlap':overlap_samp_2,
                    'gap':overlap_samp_2,
                    'end':overlap_samp_2,
                    },
                'abuting':{
                    'abuting':overlap_samp_2,
                    'overlap':overlap_samp_2,
                    'gap':overlap_samp_2,
                    'end':overlap_samp_2,
                    },    
                'overlap':{
                    'abuting':overlap_samp_2,
                    'overlap':overlap_samp_2,
                    'gap':overlap_samp_2,
                    'end':overlap_samp_2,
                    },
                'gap':{
                    'abuting':overlap_samp_2,
                    'overlap':overlap_samp_2,
                    'gap':overlap_samp_2,
                    'end':overlap_samp_2,
                    }
                }
            }
    
#    PROB_FUNC_DICT = {
#            'unordered' : post_h_theta_phi_4,
#            'ordered' : post_h
#            }
  #random.seed(100)
  method  = 'gibbs'
  CALIBRATION_DATA = CALIBRATION.to_dict()
  x_min = min(RCD_EST)
  s = max(RCD_ERR)
  x_max = max(RCD_EST)
  mydict = CALIBRATION_DATA['Carbon_year']
  a = list(mydict.values())
  p = min(range(len(a)), key=lambda i: abs(a[i]-x_min))
  l = min(range(len(a)), key=lambda i: abs(a[i]-x_max))
  A = max(p - 10*s, 0)
  P = min(l + 10*s, 50000)
  
  ##############################################
  ##initiating  likelihoods
  RCD_S = [list(x) for x in zip(RCD_EST, RCD_ERR)]
  RESULT_VEC = [likelihood_func(date[0], date[1], A, P, CALIBRATION_DATA) for date in RCD_S]
  acept_prob = 1
#  tot_i = 0
  while acept_prob > 0:
      THETA_INITS = theta_init_func_n(KEY_REF, PHI_REF, RESULT_VEC, STRAT_VEC, P, CONTEXT_NO, TOPO_SORT)
      PHASE_BOUNDARY_INITS = phase_bd_init_func(KEY_REF, PHI_REF, THETA_INITS, PREV_PHASE, A, P)
      
      #initiating the inital dict
      NEW_LST = [list(x) for x in zip(THETA_INITS, RESULT_VEC, CONTEXT_NO, STRAT_VEC)]
      CV_B = phase_limits(PHASE_BOUNDARY_INITS, POST_PHASE)
      PHIS_VEC = PHASE_BOUNDARY_INITS
      THETAS = THETA_INITS
      TRACK_VEC = []
      KEYS_TRACK = []
      for d in PHI_REF:
          ind = [index for index, element in enumerate(KEY_REF) if element == d]
          test_lst = [NEW_LST[d] for d in ind]
          bound = CV_B[PHI_REF.index(d)]
          TRACK_VEC.append({'dates': test_lst,
                            'boundaries': bound,
                            'prev_phase_rel': PREV_PHASE[PHI_REF.index(d)],
                            'post_phase_rel': POST_PHASE[PHI_REF.index(d)]})
          KEYS_TRACK.append(d)
      
      TEST_DICT_1 = dict(zip(KEYS_TRACK, TRACK_VEC))
      SITE_DICT_TEST_1 = TEST_DICT_1
      
      
      ########################### figures out how to sample based on phase relationships
      K = len(THETAS)
      M = len(PHIS_VEC)
      S = s
      R = P - A
      POST_S = []
      STEP_1 = sampling_vec(POST_PHASE, PREV_PHASE)[0]
      SAMP_VEC_TRACK = sampling_vec(POST_PHASE, PREV_PHASE)[1]
      STEP_2 = [PREV_PHASE[i] for i in SAMP_VEC_TRACK]
      STEP_3 = [POST_PHASE[i] for i in SAMP_VEC_TRACK]
      
      ########################################
      
      #set up empty post vectors
      POST_THETAS = [[] for _ in range(len(THETAS))]
      POST_PHIS = [[] for _ in range(len(PHIS_VEC))]   
      for p, a in enumerate(THETA_INITS):
          POST_THETAS[p].append(a)
      for j, b in enumerate(PHASE_BOUNDARY_INITS):
          POST_PHIS[j].append(b)
      
      if method == 'sqeeze':
          PREV_PROB_TEST = post_h(SITE_DICT_TEST_1, THETAS, CONTEXT_NO)[1]       
          SITE_DICT_TEST_2 = TEST_DICT_1
          SITE_DICT_TEST_3 = TEST_DICT_1
          SITE_DICT_TEST_4 = TEST_DICT_1
          SITE_DICT_TEST_5 = TEST_DICT_1   
          ACCEPT = [[] for _ in range(len(THETAS))]
          PHI_ACCEPT = [[] for _ in range(len(PHIS_VEC))] 
          
          i = 0
          ###START OF MCMC ALGORITHM###############
          while min([len(i) for i in ACCEPT]) < 50000:
              for l in np.linspace(0, 10002, 3335):
                  t0 = time.perf_counter()
                  print("i " + str(i) + "\n")
                  SITE_DICT_TEST_1 = dict_update(SITE_DICT_TEST_1, POST_THETAS, POST_PHIS, i, i, POST_PHASE, PHI_REF)
                 #step 1 #####################
                  k = int(random.sample(range(0, K), 1)[0])
                  oldtheta = THETAS[k]
                  key = KEY_REF[k]
                  a = [CONTEXT_NO[k] in i for i in SITE_DICT_TEST_1[key]["dates"]].index(True)
                  strat_single = strat_rel(SITE_DICT_TEST_1, key, a, THETAS, CONTEXT_NO)
                  THETAS[k] = np.random.uniform(max(SITE_DICT_TEST_1[key]["boundaries"][0], strat_single[1]),
                                                min(SITE_DICT_TEST_1[key]["boundaries"][1], strat_single[0]))
                  
                  for g_1 in enumerate(THETAS):
                      POST_THETAS[g_1[0]].append(THETAS[g_1[0]])
                  SITE_DICT_TEST_2 = dict_update(SITE_DICT_TEST_2, POST_THETAS, POST_PHIS, i+1, i, POST_PHASE, PHI_REF)
                  prob_1_test = post_h(SITE_DICT_TEST_2, THETAS, CONTEXT_NO)[1]
                  
                  c_test = []
                  for j_1, a_1 in enumerate(prob_1_test):
                      c_test.append(a_1/PREV_PROB_TEST[j_1])
                  h_1 = np.prod(c_test)
                  if h_1 >= 1:
                      ACCEPT[k].append(THETAS[k])
                      print("step 1 accept")
                  else:
                      u = np.random.uniform(0, 1)
                      if h_1 > u:
                          ACCEPT[k].append(THETAS[k])
                          print("step 1 accept")
                      else:
                          THETAS[k] = oldtheta
                          for g2 in range(len(THETAS)):
                              POST_THETAS[g2][i+1] = POST_THETAS[g2][i]
                          prob_1_test = PREV_PROB_TEST
                  #step 2 #############################
                  
                  m = int(random.sample(range(0, M), 1)[0])
                  s1 = max(PHIS_VEC) - min(PHIS_VEC)
                  f_phi1 = (s1**(1-M))/(R-s1)
                  oldphi = PHIS_VEC[m]
                  lims = PHI_SAMP_DICT[STEP_1[m]][STEP_2[m]][STEP_3[m]](THETAS, PHIS_VEC, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF)
                  PHIS_VEC[m] = np.random.uniform(lims[0], lims[1])
                  for v1, a_2 in enumerate(PHIS_VEC):
                      POST_PHIS[v1].append(a_2)
                  s2 = max(PHIS_VEC) - min(PHIS_VEC)
                  f_phi2 = (s2**(1-M))/(R-s2)
                  SITE_DICT_TEST_3 = dict_update(SITE_DICT_TEST_3, POST_THETAS, POST_PHIS, i+1, i+1, POST_PHASE, PHI_REF)
                  step_2_prob = post_h(SITE_DICT_TEST_3, THETAS, CONTEXT_NO)
                  prob_2_test = step_2_prob[1]
                  backup_b_test = step_2_prob[0]
                  c_test = []
                  for k_2, b_2 in enumerate(prob_2_test):
                      c_test.append(b_2/prob_1_test[k_2])
                  h_2 = np.prod(c_test)*(f_phi2/f_phi1)
                  if h_2 >= 1:
                      PHI_ACCEPT[m].append(PHIS_VEC[m])
                      print("step 2 accept")
                      if m == M-1:
                          POST_S.append(max(PHIS_VEC) - PHIS_VEC[m])
                      elif m == 0:
                          POST_S.append(PHIS_VEC[m]-min(PHIS_VEC))
                  else:
                      u = np.random.uniform(0, 1)
                      if h_2 > u:
                          print("step 2 accept")
                          PHI_ACCEPT[m].append(PHIS_VEC[m])
                          if m == M-1:
                              POST_S.append(max(PHIS_VEC) - PHIS_VEC[m])
                          elif m == 0:
                              POST_S.append(PHIS_VEC[m]- min(PHIS_VEC))
                      else:
                          for v2 in enumerate(PHIS_VEC):
                              POST_PHIS[v2[0]][i+1] = POST_PHIS[v2[0]][i]
                          PHIS_VEC[m] = oldphi
                          prob_2_test = prob_1_test
              
              ###DONT NEED ANYTHING FROM HERE FOR DIFFERENT MODELS SINCE IT'S JUST A SCALE AND SHIFT #
                # step3 ################
                  step = np.random.uniform(-1*S, S)
                  THETAS = [x + step for x in THETAS]
                  PHIS_VEC = [x + step for x in PHIS_VEC]
                  for g2, a_3 in enumerate(THETAS):
                      POST_THETAS[g2].append(a_3)
                  for v2, b_3 in enumerate(PHIS_VEC):
                      POST_PHIS[v2].append(b_3)
                  SITE_DICT_TEST_4 = dict_update(SITE_DICT_TEST_4, POST_THETAS, POST_PHIS, i+2, i+2, POST_PHASE, PHI_REF)
                  temp = post_h(SITE_DICT_TEST_4, THETAS, CONTEXT_NO)
                  prob_3_test = temp[1]
                  b_test = temp[0]
                  c_test = []
                  for f, c_3 in enumerate(prob_3_test):
                      c_test.append(c_3/prob_2_test[f])
                  h_3 = np.prod(c_test)
                  if h_3 >= 1:
                      print("step 3 accept")
                      for j_3, d_3 in enumerate(PHIS_VEC):
                          PHI_ACCEPT[j_3].append(d_3)
                      for k_3, e_3 in enumerate(THETAS):
                          ACCEPT[k_3].append(e_3)
                      POST_S.append(max(PHIS_VEC) - min(PHIS_VEC))
                  else:
                      u = np.random.uniform(0, 1)
                      if h_3 > u:
                          print("step 3 accept")
                          for j_3, f_3 in enumerate(PHIS_VEC):
                              PHI_ACCEPT[j_3].append(f_3)
                          for k_3, i_3 in enumerate(THETAS):
                              ACCEPT[k_3].append(i_3)
                          POST_S.append(max(PHIS_VEC) - min(PHIS_VEC))
                      else:
                          for g_3 in enumerate(THETAS):
                              POST_THETAS[g_3[0]][i+2] = POST_THETAS[g_3[0]][i+1]
                          for v_3 in enumerate(PHIS_VEC):
                              POST_PHIS[v_3[0]][i+2] = POST_PHIS[v_3[0]][i+1]
                          THETAS = [x - step for x in THETAS]
                          PHIS_VEC = [x - step for x in PHIS_VEC]
                          prob_3_test = prob_2_test  
                          b_test = backup_b_test
              
              ##step 4 #########
                #  print("step4")
                  rho = np.random.uniform(2/3, 3/2)
                  constant = (rho-1)*mean(np.concatebelownate([PHIS_VEC, THETAS])).item()
                  THETAS = [x*rho - constant for x in THETAS]
                  PHIS_VEC = [x*rho - constant for x in PHIS_VEC]
                  for s_4, a_4 in enumerate(THETAS):
                      POST_THETAS[s_4].append(a_4)
                  for e_4, b_4 in enumerate(PHIS_VEC):
                      POST_PHIS[e_4].append(b_4)
                  SITE_DICT_TEST_5 = dict_update(SITE_DICT_TEST_5, POST_THETAS, POST_PHIS, i+3, i+3, POST_PHASE, PHI_REF)
                  s = max(PHIS_VEC) - min(PHIS_VEC)
                  const = (R - s)/((R-(rho*s))*rho)
                  temp_2 = post_h(SITE_DICT_TEST_5, THETAS, CONTEXT_NO)
                  a_test = temp_2[0]
                  PREV_PROB_TEST = temp_2[1]
                  c_test = []
                  for q_4, k_4 in enumerate(a_test):
                      c_test.append(k_4/b_test[q_4])
                  h_temp_test = np.prod(c_test)
                  h_4 = h_temp_test*const
                  if h_4 >= 1:
                      print("step 4 accept")
                      for j_4, c_4 in enumerate(PHIS_VEC):
                          PHI_ACCEPT[j_4].append(c_4)
                      for k_4, f_4 in enumerate(THETAS):
                          ACCEPT[k_4].append(f_4)
                      POST_S.append(max(PHIS_VEC) - min(PHIS_VEC))
                  else:
                      u = np.random.uniform(0, 1)
                      if h_4 > u:
                          print("step 4 accept")
                          for j_4, g_4 in enumerate(PHIS_VEC):
                              PHI_ACCEPT[j_4].append(g_4)
                          for k_4, i_4 in enumerate(THETAS):
                              ACCEPT[k_4].append(i_4)
                          POST_S.append(max(PHIS_VEC) - min(PHIS_VEC))
                      else:
                          for g_4 in range(len(THETAS)):
                              POST_THETAS[g_4][i+3] = POST_THETAS[g_4][i+2]
                          for v_4 in range(len(PHIS_VEC)):
                              POST_PHIS[v_4][i+3] = POST_PHIS[v_4][i+2]
                          THETAS = [(x + constant)/rho for x in THETAS]
                          PHIS_VEC = [(x + constant)/rho for x in PHIS_VEC]
                          PREV_PROB_TEST = prob_3_test
                  i = i + 3
              CHECK_ACCEPT = accept_prob(ACCEPT, PHI_ACCEPT, i)
              acept_prob = len(CHECK_ACCEPT[(CHECK_ACCEPT <= 0.01) | (CHECK_ACCEPT >= 0.7)])
              print(acept_prob)
              if acept_prob > 0:
                  print("oh no")
                  break
      #plot code
          CHECK_ACCEPT = accept_prob(ACCEPT, PHI_ACCEPT, i)
          print(len(CHECK_ACCEPT[(CHECK_ACCEPT <= 0.1) | (CHECK_ACCEPT >= 0.7)]))
      elif method == 'gibbs': 
          acept_prob = 0
          POST_S = []
          for i in range(0, 5000):
                t0 = time.perf_counter()
                print("i " + str(i) + "\n")
                thetas =  theta_samp_func(POST_THETAS, POST_PHIS, KEY_REF, PHI_REF, RESULT_VEC, STRAT_VEC, CONTEXT_NO, TOPO_SORT, i, TEST_DICT_1)
                t1 = time.perf_counter() - t0 
                print('theta_samps ' + str(t1))
                for g, j in enumerate(thetas):    
                    POST_THETAS[g].append(j)
                phis = phase_samp_func(KEY_REF, PHI_REF, POST_THETAS, PREV_PHASE, A, P, i)
                for k, l in enumerate(phis):
                    POST_PHIS[k].append(l)
                TEST_DICT_1 = dict_update(TEST_DICT_1, POST_THETAS, POST_PHIS, i+1, i+1, POST_PHASE, PHI_REF)
                POST_S.append(phis[0] - phis[M-1])
                tottime = time.perf_counter() - t0
                print('t2 ' + str(tottime))
  PHI_ACCEPT, ACCEPT = POST_PHIS, POST_THETAS
  hpd_dict = {}
  for i, j in enumerate(CONTEXT_NO):
        hpd_dict[j] = list(HPD_interval(np.array(ACCEPT[i][1000:])))
  hpd_df = pd.DataFrame.from_dict(hpd_dict, orient='index')
  hpd_df.to_csv("hpd_intervals_thetas")    
  hpd_dict = {}
  for k, l in enumerate(PHI_REF):
        hpd_dict[l] = list(HPD_interval(PHI_ACCEPT[k][1000:]))
  hpd_df = pd.DataFrame.from_dict(hpd_dict, orient='index')
  hpd_df.to_csv("hpd_intervals_phis") 
            
    #    print(pc.stats.hpd(np.array(POST_S)))
    #    plt.savefig("trace_sim_4.png")
    #    tot = time.perf_counter() - t0
    #    print(tot)
    #    
    #    for i in ACCEPT:
    #        plt.plot(i)
            
  for n, m in enumerate(CONTEXT_NO): 
        plt.figure()
        plt.xlim(A, P)
        k, bins, patches = plt.hist(ACCEPT[n], bins='auto', color='#0504aa',
                        alpha=0.7, rwidth=0.85, density = True )
        plt.gca().invert_xaxis()
        plt.ioff()
        file_name = str('Posterior_density_context_' + str(m))
        plt.savefig(file_name)
  plt.close('all')      
  for q, w in enumerate(PHI_REF):
        plt.figure()
        plt.xlim(A, P)
        k, bins, patches = plt.hist(PHI_ACCEPT[q], bins='auto', color='#0504aa',
                        alpha=0.7, rwidth=0.85, density = True )
        plt.gca().invert_xaxis()
        plt.ioff()
        file_name = str('Posterior_density_phase_' + str(w))
        plt.savefig(file_name)
  plt.close('all')

  
#PHI_ACCEPT, ACCEPT, POST_S = run_MCMC(CALIBRATION, STRAT_VEC, RCD_EST, RCD_ERR, KEY_REF, CONTEXT_NO, PHI_REF, PREV_PHASE, POST_PHASE, TOPO_SORT)
#    k, BINS, PATCHES = plt.hist(POST_S[100:], bins="auto", color='#0504aa',
#                                alpha=0.7, rwidth=0.85, density=True)
#    plt.title('Shag River Mouth data using the Alpha-beta \'squeezing\' model')
#    plt.xlabel('Phase length (calendar years)')
#    plt.ylabel('Frequency')
#    #plt.ylim(0,0.0043)
##    #plt.xlim(0, 2000)
#    plt.savefig("hist_sim_4.png")
#    plt.plot(POST_S)
#    plt.show()
#    hpd_dict = {}

#x_temp is dataframe of theta with posterior, e.g. gibbs_test[0] or gibbs_test[1]


    #k, bins, patches = plt.hist(accept[10], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(accept[9], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(accept[8], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(accept[7], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(accept[6], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #%%
    #k, bins, patches = plt.hist(accept[5], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(accept[4], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(accept[3], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(accept[2], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(accept[1], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(accept[0], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    
    #k, bins, patches = plt.hist(phi_accept[3], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(phi_accept[3], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(phi_accept[2], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(phi_accept[1], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(phi_accept[1], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
    #k, bins, patches = plt.hist(phi_accept[0], bins='auto', color='#0504aa',
    #                      alpha=0.7, rwidth=0.85, density = True )
#    print(len(ACCEPT))
#    PLOT_INDEX = [i for i in range(len(ACCEPT))]
#    type(PLOT_INDEX)
#    FIGURE, AXES = plt.subplots(nrows=4, ncols=int(K/4), sharex=True, sharey=True, figsize=[14, 6])
#    plotcoords = []
#    for i in range(AXES.shape[1]):
#        for j in range(AXES.shape[0]):
#            plotcoords.append((j, i))
#            
# #   plt.xlim(700, 1300)
#    plt.ylim(0, 0.15)
#    #for j in range(len(axes.ravel())):
#    for i, j in zip(PLOT_INDEX, plotcoords):
#        AXES[j].hist(ACCEPT[i], bins='auto', color='#0504aa',
#                     alpha=0.7, rwidth=0.85, density=True)
#        AXES[j].set_xlabel(str(CONTEXT_NO[i]))
#    
#    #plt.xlabel(CONTEXT_NO[i])
##    #for i in range(len(THETAS)):
##    #    print(pm3.stats.hpd(np.array(ACCEPT[i])))
#    plt.title('Theta Histograms')
#    
#    plt.ylabel('Probability density')
#    plt.savefig("hist_thetas.png")
