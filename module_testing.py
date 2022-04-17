#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 10:09:37 2021

@author: bryony
"""


import automated_mcmc_ordering_coupling_copy as mcmc
import automated_mcmc_ordering_coupling_grouping_prototype as mcmc1
import pandas as pd

CALIBRATION = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)
A = 450
P = 950
STRAT_VEC = [[[], []], [[], []], [[], []], [[], []], [[], []], [[], []], [[], []]]
#STRAT_VEC.reverse()
RCD_EST = [660, 630, 646, 670, 537, 600, 580]
#RCD_EST.reverse()
RCD_ERR = [46, 35, 47, 47, 44, 50, 47]
#RCD_ERR.reverse()
KEY_REF = ["6", "5", "5", "4", "3", "2", "1"]
#KEY_REF.reverse()
CONTEXT_NO = ["7771", "2589", "7755", "7756", "7757", "7761", "7758"]
PHI_REF = ["6", "5", "4", "3", "2", "1"]

PREV_PHASE = ["start", "abuting", "abuting", "abuting", "abuting", "abuting"]
POST_PHASE = ["abuting", "abuting", "abuting", "abuting", "abuting", "end"]
TOPO_SORT = CONTEXT_NO
mcmc.run_MCMC(CALIBRATION, STRAT_VEC, RCD_EST, RCD_ERR, KEY_REF, CONTEXT_NO, PHI_REF, PREV_PHASE, POST_PHASE, TOPO_SORT)


STRAT_VEC = [[[], []], [['463'], ['527', '509', '492']], [['528'], ['529']], [['494', '529', '531'], []], [[], ['464', '450']], [['463'], []], [['476'], ['477']], [[], ['472']], [['472'], ['478']], [['477'], ['485']], [['530'], []], [['478'], ['486']], [['485'], []], [[], []], [['450'], ['493']], [['492'], ['494']], [['493'], ['452']], [['450'], ['510']], [['509'], []], [['450'], ['528']], [['527'], ['451']], [['451'], ['452']], [[], ['483']], [[], ['452']]] 
RCD_EST = [1100, 1125, 1220, 1300, 1120, 1110, 1120, 1120, 1130, 1200, 1300, 1210, 1310, 1100, 1100, 1230, 1230, 1102, 1220, 1125, 1240, 1210, 1120, 1210] 
RCD_ERR =[50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50] 
KEY_REF = ['4', '4', '3', '2', '4', '4', '4', '4', '4', '3', '2', '3', '2', '4', '4', '3', '3', '4', '3', '4', '3', '3', '4', '3'] 
CONTEXT_NO = ['432', '450', '451', '452', '463', '464', '472', '476', '477', '478', '483', '485', '486', '487', '492', '493', '494', '509', '510', '527', '528', '529', '530', '531'] 
PHI_REF = ['2', '3', '4'] 
PREV_PHASE = ['start', 'gap', 'gap'] 
POST_PHASE = ['gap', 'gap', 'end']
TOPO_SORT = ['432', '464', '452', '529', '451', '528', '527', '510', '509', '494', '493', '492', '450', '463', '486', '485', '478', '477', '472', '476', '487', '483', '530', '531']
CONTEXT_NO, ACCEPT, PHI_ACCEPT, PHI_REF, A, P, ALL_SAMPS_CONT, ALL_SAMPS_PHI = mcmc.run_MCMC(CALIBRATION, STRAT_VEC, RCD_EST, RCD_ERR, KEY_REF, CONTEXT_NO, PHI_REF, PREV_PHASE, POST_PHASE, TOPO_SORT)

#nicholls and jones
CALIBRATION = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)
STRAT_VEC = [[[], []], [[], []], [[], []], [[], []], [[], []], [[], []], [[], []]]
RCD_EST = [660, 630, 646, 670, 537, 600, 580]
RCD_ERR = [46, 35, 47, 47, 44, 50, 47]
KEY_REF = ["1", "1", "1", "1", "1", "1", "1"]
CONTEXT_NO = ["7771", "2589", "7755", "7756", "7757", "7761", "7758"]
PHI_REF = ["1"]
PREV_PHASE = ["start"]
POST_PHASE = ["end"]
TOPO_SORT = CONTEXT_NO
CONT_TYPE = ['normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal']
mcmc.run_MCMC(CALIBRATION, STRAT_VEC, RCD_EST, RCD_ERR, KEY_REF, CONTEXT_NO, PHI_REF, PREV_PHASE, POST_PHASE, TOPO_SORT)



CALIBRATION = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)
STRAT_VEC = [[[], []], [['4'], []], [[], ['4']], [['1', '3'], ['6']], [['1'], []], [[], ['4', '2']]]
RCD_EST = [280, 400, 300, 350, 330, 270]
RCD_ERR = [59, 55, 50, 50, 50, 50]
KEY_REF = ['1', '1', '1', '1', '1', '1']
CONTEXT_NO = ['5', '6', '3', '4', '2', '1'] 
PHI_REF = ['1']
PREV_PHASE = ["start"]
POST_PHASE = ["end"]
TOPO_SORT = ['5', '6', '4', '2', '3', '1'] 

###st veit (in Bcal)
CALIBRATION = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)
STRAT_VEC = [[['814'], []], [['923'], []], [['1235'], ['758']], [['358'], []], [['358'], ['925']], [['358'], []], [['358'], ['814']], [['813'], ['1235', '493', '923', '1168']], [['1210'], ['358']], [[], ['813']]]
RCD_EST = [3275, 3420, 3270, 3160, 3435, 3190, 3400, 3340, 3270, 3200]
RCD_ERR = [75, 65, 80, 70, 60, 65, 75, 80, 75, 70]
KEY_REF = ['1', '1', '1', '1', '1', '1', '1', '2','2','2']
CONTEXT_NO = ['923', '1235', '925', '814', '358', '813', '493', '1210', '1168', '758'] 
PHI_REF = ['2', '1']
PREV_PHASE = ["start", 'abuting']
POST_PHASE = ["abuting", "end"]
TOPO_SORT = ['1210', '813', '358', '1168', '923', '493', '925', '1235', '814', '758'] 
TOPO_SORT.reverse() #becuase dates MUST be from oldest to youngest


CALIBRATION = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)
STRAT_VEC = [[[], ['814']], [['758'], ['1235']], [['814'], ['358']], [[], ['358']], [[], ['923']], [['925'], ['358']], [[], ['358']], [['1235', '493', '923', '1168'], ['813']], [['358'], ['1210']], [['813'], []]]
STRAT_VEC = [[i[1], i[0]] for i in STRAT_VEC ]
RCD_EST = [3275, 3270, 3400, 3190, 3420, 3435, 3160, 3340, 3270, 3200]
RCD_ERR = [75, 80, 75, 75, 65, 60, 70, 80, 75, 70]
KEY_REF = ['1', '1', '1', '1', '1', '1', '1', '2','2','2']
CONTEXT_NO = ['758', '814', '1235', '493', '925', '923', '1168', '358', '813', '1210'] 
PHI_REF = ['1', '2']
PREV_PHASE = ["start", 'abuting']
POST_PHASE = ["abuting", "end"]
TOPO_SORT = ['1210', '813', '358', '1168', '923', '493', '925', '1235', '814', '758'] 
TOPO_SORT.reverse()
CONT_TYPE = ['normal','normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal']
CONTEXT_NO, ACCEPT, PHI_ACCEPT, PHI_REF, A, P, ALL_SAMPS_CONT, ALL_SAMPS_PHI = mcmc.run_MCMC(CALIBRATION, STRAT_VEC, RCD_EST, RCD_ERR, KEY_REF, CONTEXT_NO, PHI_REF, PREV_PHASE, POST_PHASE, TOPO_SORT, CONT_TYPE)

CALIBRATION1 = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)
STRAT_VEC1 = [[[], ['814']], [['758'], ['1235']], [['814'], ['358']], [[], ['358']], [[], ['923']], [['925'], ['358']], [[], ['358']], [['1235', '493', '923', '1168'], ['813']], [['358'], ['1210']], [['813'], []]]
STRAT_VEC1 = [[i[1], i[0]] for i in STRAT_VEC ]
RCD_EST1 = [3275, 3270, 3400, 3190, 3420, 3435, 3160, 3340, 3270, 3200]
RCD_ERR1 = [75, 80, 75, 75, 65, 60, 70, 80, 75, 70]
KEY_REF1 = ['1', '1', '1', '1', '1', '1', '1', '2','2','2']
CONTEXT_NO1 = ['758', '814', '1235', '493', '925', '923', '1168', '358', '813', '1210'] 
PHI_REF1 = ['1', '2']
PREV_PHASE1 = {'1': None, '2':['abuting', '1']}
POST_PHASE1 = {'1': ['2', "abuting"], '2': None}
TOPO_SORT1 = ['b_2', '1210', '813', '358', 'a_2 - b_1', '1235', '1168', '923', '493', '814', '925', '758', 'a_1'] 
TOPO_SORT1.reverse() #becuase dates MUST be from oldest to youngest
CONT_TYPE1 = ['normal','normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal']
import automated_mcmc_ordering_coupling_grouping_prototype as mcmc1
CONTEXT_NO1, ACCEPT1, PHI_ACCEPT1, PHI_REF1, A1, P1, ALL_SAMPS_CONT1, ALL_SAMPS_PHI1 = mcmc1.run_MCMC(CALIBRATION1, STRAT_VEC1, RCD_EST1, RCD_ERR1, KEY_REF1, CONTEXT_NO1, PHI_REF1, PREV_PHASE1, POST_PHASE1, TOPO_SORT1, CONT_TYPE1, data = pd.DataFrame(columns=['group','contains']) )


test_dict = {}
test_dict['1'] = {'contains':[('start', '3'), ('end', '7'), ('within', '2')], 'dates' : [43, 4]}
test_dict['2'] = {'contains': None, 'dates' : [48, 4]}
test_dict['3'] = {'contains': [('start', '4')], 'dates' : [43, 4]}
test_dict['4'] = {'contains': [('start', '5'), ('start', '6')], 'dates' : [27, 4]}
test_dict['5'] = {'contains': [('wihin', '8')], 'dates' : [74, 4]}
test_dict['6'] = {'contains': [('start', '9'), ('within', '10')], 'dates' : [53, 4]}
test_dict['7'] = {'contains': None, 'dates' : [49, 4]}
test_dict['8'] = {'contains': None, 'dates' : [45, 4]}
test_dict['9'] = {'contains': None, 'dates' : [41, 4]}
test_dict['10'] = {'contains': None, 'dates' : [58, 4]}

        


def grps_start_end_outer(i, cond, test_dict):  
    list2 = []
    list_others = []
    if test_dict[i]['contains'] != None:      
        for string, number in test_dict[i]['contains']:
            if string == cond:
                list2.append(number)
            else: 
                list_others.append(number)
    return list2, list_others


def samplng_lims_alpha(phase, test_dict):
    #### inner groups #######
    list2 = [phase]
    master_list = list2
    master_alphas = []
    while len(list2) != 0:
        list3 = []
        for i in list2:
            grps = grps_start_end_outer(i, 'starts', test_dict)
            list3 = list3 + grps[0]
            master_alphas = master_alphas + grps[1]
        list2 = list3
        master_list = master_list + list2
        
    conts_1 = [test_dict[i]['dates'] for i in master_list]
    conts = [i[0] for i in conts_1]
    alphas = [test_dict[i]['boundaries'][1] for i in master_alphas]
    lowers = conts + alphas
    #### outer group# #####
    test_dict[phase]['within'] != None
    if test_dict[phase]['within'][1] == 'starts':
        outphase = test_dict[phase]['within'][0]
        up_outer = []
        for j in test_dict[outphase]['prev_phase']:
            up_outer = up_outer + grps_start_end_outer(j[1], 'ends', test_dict)
        else:
            up_outer = test_dict[phase]['boundaries'][1]
    ### between phase relationships ###
    upper = []
    lower = []
    for k in test_dict[phase]['prev_phase']:
        if k[0] == 'abuting':
            upper =  upper + grps_start_end_outer(k[1], 'ends', test_dict)
        elif k[0] == 'gap':
            upper.append(test_dict[k]['boundaries'][0])
        elif k[0] == 'overlap':
            upper.append(test_dict[k]['boundaries'][1])
            lower.append(test_dict[k]['boundaries'][0])
    for l in test_dict[phase]['post_phase']:
        if l[0] == 'overlap':
            lower.append(test_dict[k]['boundaries'][1])
    tot_lower = lowers + lower
    tot_upper= up_outer + upper        
    return [min(tot_upper), max(tot_lower)]    
        
            
        
            


#Amy site
#STRAT_VEC = [[['2'], []], [[], ['10']], [[], ['3']], [[], []], [[], ['8']], [['4'], []], [['5'], []], [[], ['7']], [['9'], []], [[], []]]
#RCD_EST = [1679, 1738, 1577, 1555, 1702, 1746, 1841, 1695, 1852, 1726] 
#RCD_ERR = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30] 
#KEY_REF = ['1', '3', '1', '1', '2', '2', '2', '2', '3', '2']
#CONTEXT_NO = ['3', '9', '2', '1', '5', '7', '8', '4', '10', '6']
#PHI_REF = ['3', '2', '1']
#PREV_PHASE = ['start', 'overlap', 'gap']
#POST_PHASE = ['overlap', 'gap', 'end'] 
#TOPO_SORT = ['10', '9', '3', '2', '1', '8', '5', '7', '4', '6']

