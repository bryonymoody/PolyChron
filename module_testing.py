#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 10:09:37 2021

@author: bryony
"""


import automated_mcmc_ordering_coupling_copy as mcmc
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
TOPO_SORT = ['b_2', '1210', '813', '358', 'a_2 - b_1', '1235', '1168', '923', '493', '814', '925', '758', 'a_1'] 
TOPO_SORT.reverse() #becuase dates MUST be from oldest to youngest
CONT_TYPE = ['normal','normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal']




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

