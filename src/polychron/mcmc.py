"""
Module for performing MCMC algorithm needed to obtain calibrated age estimates for the parameters within a chronological model.

`run_MCMC` is the primary method which should be used to invoke the MCMC algorithm.
"""

from __future__ import annotations

import math
import random
from statistics import mean

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .interfaces import Writable


def HPD_interval(x_temp, lim=0.95, probs=[]):
    """Get HPD interval for an array of phase/group lengths"""
    if len(probs) == 0:
        x_temp = np.array(x_temp)
        n = math.ceil((x_temp.max() - x_temp.min()))
        probs, x_vals = np.histogram(x_temp, bins=n, density=1)
    else:
        x_vals = x_temp
        probs = probs[1:]
    df = pd.DataFrame({"Theta": x_vals[1:], "Posterior": probs})
    hpd_vec = []
    theta_vec = []
    y = df.sort_values(by=["Posterior"], ascending=False)
    posterior_x = np.array(y["Posterior"])
    posterior_theta = np.array(y["Theta"])
    i = 0
    while sum(hpd_vec) <= lim:
        hpd_vec.append(posterior_x[i])
        theta_vec.append(posterior_theta[i])
        i = i + 1
    theta_vec.sort()
    rangevec = []
    rangevec.append(int(min(theta_vec)))
    for i in range(len(theta_vec) - 1):
        if theta_vec[i + 1] - theta_vec[i] > 5:
            rangevec.extend([int(theta_vec[i]), int(theta_vec[i + 1])])
    rangevec.append(int(max(theta_vec)))
    return rangevec


def theta_samp_func(
    GIBBS_THETAS, GIBBS_PHIS, KEY_REF, PHI_REF, RESULT_VEC, STRAT_VEC, CONTEXT_NO, TOPO_SORT, iter_num, GIBBS_DICT_1
):  # , PREV_IT):
    """Gives a list of initial theta values for MCMC"""
    out_vec = [0] * len(KEY_REF)
    for date in range(0, len(PHI_REF)):
        ref_vec = np.where(np.array(KEY_REF) == PHI_REF[date])[0].tolist()
        phase_lab = PHI_REF[date]
        phase = [CONTEXT_NO[i] for i in ref_vec]
        phase_topo = [i for i in TOPO_SORT if i in phase]
        phase_upp_lim = GIBBS_DICT_1[phase_lab]["boundaries"][1]  # needs to be less than this
        phase_low_lim = GIBBS_DICT_1[phase_lab]["boundaries"][0]  # needs to be more than this
        for i in phase_topo:
            a = np.where(np.array(CONTEXT_NO) == i)[0][0].item()
            below = STRAT_VEC[a][0]  # should be less than this
            above = STRAT_VEC[a][1]  # should be greater than this
            if len(above) == 0:
                if len(below) == 0:
                    dates = RESULT_VEC[a][0]
                    ind = (dates < phase_upp_lim) & (dates > phase_low_lim)
                    SAMPLE_VEC, SAMPLE_VEC_PROB = dates[ind], RESULT_VEC[a][1][ind]
                    w = SAMPLE_VEC_PROB / np.sum(SAMPLE_VEC_PROB)
                    out_vec[a] = SAMPLE_VEC[np.searchsorted(w.cumsum(), random.random())]
                else:
                    maxstrat = max(
                        [GIBBS_THETAS[np.where(np.array(CONTEXT_NO) == j)[0][0].item()][iter_num] for j in below]
                    )
                    max_tot = max([maxstrat, phase_low_lim])
                    SAMPLE_VEC = RESULT_VEC[a][0][(RESULT_VEC[a][0] < phase_upp_lim) & (RESULT_VEC[a][0] > max_tot)]
                    SAMPLE_VEC_PROB = RESULT_VEC[a][1][
                        (RESULT_VEC[a][0] < phase_upp_lim) & (RESULT_VEC[a][0] > max_tot)
                    ]
                    out_vec[a] = random.choices(SAMPLE_VEC, weights=SAMPLE_VEC_PROB / sum(SAMPLE_VEC_PROB))[0]
            elif len(below) == 0:
                minstrat = min([out_vec[np.where(np.array(CONTEXT_NO) == j)[0][0].item()] for j in above])
                min_tot = min([minstrat, phase_upp_lim])
                SAMPLE_VEC = RESULT_VEC[a][0][(RESULT_VEC[a][0] < min_tot) & (RESULT_VEC[a][0] > phase_low_lim)]
                SAMPLE_VEC_PROB = RESULT_VEC[a][1][(RESULT_VEC[a][0] < min_tot) & (RESULT_VEC[a][0] > phase_low_lim)]
                out_vec[a] = random.choices(SAMPLE_VEC, weights=SAMPLE_VEC_PROB / sum(SAMPLE_VEC_PROB))[0]
            else:
                maxstrat = max(
                    [GIBBS_THETAS[np.where(np.array(CONTEXT_NO) == j)[0][0].item()][iter_num] for j in below]
                )
                max_tot = max([maxstrat, phase_low_lim])
                minstrat = min([out_vec[np.where(np.array(CONTEXT_NO) == j)[0][0].item()] for j in above])
                min_tot = min([minstrat, phase_upp_lim])
                SAMPLE_VEC = RESULT_VEC[a][0][(RESULT_VEC[a][0] < min_tot) & (RESULT_VEC[a][0] > max_tot)]
                SAMPLE_VEC_PROB = RESULT_VEC[a][1][(RESULT_VEC[a][0] < min_tot) & (RESULT_VEC[a][0] > max_tot)]
                out_vec[a] = random.choices(SAMPLE_VEC, weights=SAMPLE_VEC_PROB / sum(SAMPLE_VEC_PROB))[0]
    return out_vec


def GR_conv_check(chain1, chain2):
    N = int(len(chain1) / 2)
    W = (chain1[-N:].std() ** 2 + chain2[-N:].std() ** 2) / 2
    mean1 = chain1[-N:].mean()
    mean2 = chain2[-N:].mean()
    mean = (mean1 + mean2) / 2
    B = N * ((mean1 - mean) ** 2 + (mean2 - mean) ** 2)
    var_theta = (1 - 1 / N) * W + 1 / N * B
    # print("Gelmen-Rubin Diagnostic: ", np.sqrt(var_theta/W))
    return np.sqrt(var_theta / W)


def phase_samp_func(key_reff, phi_reff, theta_vals, prev_phases, A, P, iter_num):
    """Gives a list of initial phase boundary values for mcmc"""
    PHASE_INITS = []
    KEY_REF_1 = np.array(key_reff)
    PHASE_INITS.append(
        np.random.uniform(max([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[0])[0].tolist()]), P)
    )
    for j in range(1, len(phi_reff)):
        a_temp = np.random.uniform(
            max([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j])[0].tolist()]),
            min([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j - 1])[0].tolist()]),
        )
        if prev_phases[j] != "abutting":
            a_temp = [
                a_temp,
                (
                    np.random.uniform(
                        max([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j])[0].tolist()]),
                        min([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[j - 1])[0].tolist()]),
                    )
                ),
            ]
            a_temp = sorted(a_temp, reverse=True)
        else:
            a_temp = [a_temp]
        [PHASE_INITS.append(ref_ind) for ref_ind in a_temp]
    PHASE_INITS.append(
        np.random.uniform(
            min([theta_vals[i][iter_num + 1] for i in np.where(KEY_REF_1 == phi_reff[-1])[0].tolist()]), A
        )
    )
    PHASE_INITS1 = sorted(PHASE_INITS, reverse=True)
    return PHASE_INITS1


def sampling_vec(post_phase_vec, prev_phase_vec):
    """Gives vectors to sample between"""
    track_phase = []
    track_vec = []
    for i_samp, j_samp in enumerate(post_phase_vec):
        h_temp = prev_phase_vec[i_samp]
        f_temp = j_samp
        if h_temp == "abutting":
            track_phase.append("combined")
        elif h_temp == "overlap":
            if prev_phase_vec[i_samp - 1] == "overlap":
                track_phase.append("overlap_upper")
            else:
                track_phase.append("upper")
            track_vec.append(i_samp)
        else:
            track_phase.append("upper")
            track_vec.append(i_samp)
        if f_temp == "abutting":
            pass
        elif f_temp == "overlap":
            if post_phase_vec[i_samp + 1] == "overlap":
                track_phase.append("overlap_beta")
            else:
                track_phase.append("lower")
        else:
            track_phase.append("lower")
        track_vec.append(i_samp)
    return [track_phase, track_vec]


def gibbs_phis_gen(prev_phase, phi_ref):
    gibbs = [phi_ref[0], phi_ref[0]]
    for i in range(1, len(phi_ref)):
        if prev_phase[i] == "abutting":
            gibbs.append(phi_ref[i])
        else:
            gibbs.append(phi_ref[i])
            gibbs.append(phi_ref[i])
    return gibbs


def phase_limits(phases, POST_PHASE):
    "Provides phase limits for a phase"
    upper = []
    lower = []
    i_phase = 0
    for a_val in enumerate(POST_PHASE):
        upper.append(phases[i_phase])
        i_phase = i_phase + 1
        lower.append(phases[i_phase])
        if a_val[1] != "abutting":
            i_phase = i_phase + 1
    phase_bounds = [list(x) for x in zip(lower, upper)]
    return phase_bounds


def accept_prob(accept_vec, phi_accept_vec, i):
    """Checks the acceptance rate for MCMC code"""
    probs = []
    for i_accept in accept_vec:
        probs.append(len(i_accept) / i)
    for j_accept in phi_accept_vec:
        probs.append(len(j_accept) / i)
    return np.array(probs)


def likeli(x_val, s_err, theta, CALIBRATION_DATA):
    """Calculates likelihood for a single value"""
    value_theta = math.exp(
        -((x_val - CALIBRATION_DATA["Carbon_year"][theta]) ** 2)
        / (2 * (s_err**2 + CALIBRATION_DATA["Carbon_error"][theta] ** 2))
    )
    #   value_theta = value_theta/((2*3.14*(s_err**2 + CALIBRATION_DATA["Carbon_error"][theta]**2))**0.5)
    return value_theta


def likelihood_func(x_val, s_err, a_val, p_val, CALIBRATION_DATA):
    """Likelihood over a range"""
    likelihood_vec = []
    for theta in range(a_val, p_val):
        value = likeli(x_val, s_err, theta, CALIBRATION_DATA)
        likelihood_vec.append(value)
    theta = np.array(range(a_val, p_val))
    intep_theta = np.linspace(a_val, p_val, ((p_val - a_val) * 10) + 1)
    interp_prob = np.interp(intep_theta, theta, likelihood_vec)
    prob = interp_prob / sum(interp_prob)
    lhood_df = [intep_theta, prob]
    return lhood_df


def strat_rel(site_dict, key, i_index, THETAS, CONTEXT_NO):
    """Gives nodes above and below a date"""
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


def dict_seek_ordered_new(A, P, i_seek, key, site_dict, THETAS, CONTEXT_NO, RCD_ERR, RCD_EST, CALIBRATION):
    """Calc probability in a dictionary (new version)"""
    llhood = site_dict[key]["dates"][i_seek][1]
    phase_len = site_dict[key]["boundaries"][1] - site_dict[key]["boundaries"][0]  # phase length
    like1 = llhood[0:][0]
    cont = site_dict[key]["dates"][i_seek][2]
    alpha = site_dict[key]["boundaries"][1]
    beta = site_dict[key]["boundaries"][0]
    # residual/intrisive ref EDIT
    # MUST add A and P to this func
    # temp_vec = llhood[1:][0][(like1 <= alpha) & (like1 >= A)]
    # temp_vec_2 = llhood[1:][0][
    #     (like1 <= min(strat_rel(site_dict, key, i_seek, THETAS, CONTEXT_NO)[0], alpha)) & (like1 >= A)
    # ]
    # elif cont_type = 'normal':
    temp_vec = llhood[1:][0][(like1 <= alpha) & (like1 >= beta)]

    temp_vec_2 = llhood[1:][0][
        (like1 <= min(strat_rel(site_dict, key, i_seek, THETAS, CONTEXT_NO)[0], alpha))
        & (like1 >= max(strat_rel(site_dict, key, i_seek, THETAS, CONTEXT_NO)[1], beta))
    ]
    if len(temp_vec_2) == 0:
        ref = CONTEXT_NO.index(cont)
        temp_vec_2 = np.array(
            likeli(RCD_EST[ref], RCD_ERR[ref], float(int(site_dict[key]["dates"][i_seek][0])), CALIBRATION)
        )
    search = np.where(like1 == int(site_dict[key]["dates"][i_seek][0]))
    if len(search[0]) == 0:
        x_temp = 0
        x_len = 0
    else:
        ind_seek = search[0][0]
        v_seek = like1[ind_seek : ind_seek + 11]
        res = min(enumerate(v_seek), key=lambda x: abs(site_dict[key]["dates"][i_seek][0] - x[1]))
        c_ind = np.where(like1 == res[1])
        x_temp = llhood[1:][0][c_ind[0]][0]
        x_len = (x_temp / phase_len) * (temp_vec.sum() / temp_vec_2.sum())
    return x_temp, x_len


def dict_seek_ordered(A, P, i_seek, key, site_dict, THETAS, CONTEXT_NO, RCD_ERR, RCD_EST, CALIBRATION):
    """Calc probability in a dictionary"""
    llhood = site_dict[key]["dates"][i_seek][1]  # array of likelihood data for the context
    # phase_len = site_dict[key]["boundaries"][1] - site_dict[key]["boundaries"][0] #phase length
    like1 = llhood[0:][0]  # array of thetas
    like2 = llhood[1:][0]  # likehood for each theta
    cont = site_dict[key]["dates"][i_seek][2]  # context number
    alpha = site_dict[key]["boundaries"][1]  # alpha for the phase this context is in
    beta = site_dict[key]["boundaries"][0]  # beta for the phase that this context is in
    # get dates of contexts that are stratigraphically linked to the context in question
    strat_up, strat_low = strat_rel(site_dict, key, i_seek, THETAS, CONTEXT_NO)
    cont_type = site_dict[key]["dates"][i_seek][4]
    if cont_type == "residual":
        up = int((alpha - A + 0.05) * 10) + 1  # faster version on np.where
        low = 0  # as above
        vec_2_up = int(((min(strat_up, alpha) - A) + 0.05) * 10) + 1  # as in lines with up and low
        vec_2_low = 0  # see above
        phase_len = site_dict[key]["boundaries"][1] - like1[low] + 1  # phase length
    elif cont_type == "intrustive":
        up = len(like2) - 1  # faster version on np.where
        low = int((beta - A + 0.05) * 10)  # as above
        vec_2_up = len(like2) - 1  # as in lines with up and low
        vec_2_low = int(((max(strat_low, beta) - A) + 0.05) * 10)  # see above
        phase_len = P - site_dict[key]["boundaries"][0]  # phase length
    else:
        up = int((alpha - A + 0.05) * 10) + 1  # faster version on np.where
        low = int((beta - A + 0.05) * 10)  # as above
        vec_2_up = int(((min(strat_up, alpha) - A) + 0.05) * 10) + 1  # as in lines with up and low
        vec_2_low = int(((max(strat_low, beta) - A) + 0.05) * 10)  # see above
        phase_len = site_dict[key]["boundaries"][1] - site_dict[key]["boundaries"][0]  # phase length
    temp_vec = like2[low:up]  # two vectors of proablilities that need summing (this and the row below)
    temp_vec_2 = like2[vec_2_low:vec_2_up]
    if len(temp_vec_2) == 0:  # checking it's not too small that the likelihood func things it's prob 0
        ref = CONTEXT_NO.index(cont)
        temp_vec_2 = np.array(
            likeli(RCD_EST[ref], RCD_ERR[ref], float(int(site_dict[key]["dates"][i_seek][0])), CALIBRATION)
        )
    if len(temp_vec) == 0:  # checking it's not too small that the likelihood func things it's prob 0
        ref = CONTEXT_NO.index(cont)
        temp_vec = np.array(
            likeli(RCD_EST[ref], RCD_ERR[ref], float(int(site_dict[key]["dates"][i_seek][0])), CALIBRATION)
        )
    date = site_dict[key]["dates"][i_seek][0]
    date_ref = int((date - A + 0.05) * 10)
    if (
        date_ref >= len(like1) or phase_len == 0 or temp_vec_2.sum() == 0
    ):  # checking we haven't sampled outside the realms of the likelihood
        x_temp = 0
        x_len = 0
    else:
        x_temp = like2[date_ref]
        x_len = (x_temp / phase_len) * (temp_vec.sum() / temp_vec_2.sum())
    if math.isnan(x_len):
        x_temp = 0
        x_len = 0

    return x_temp, x_len


def post_h(A, P, site_dict, THETAS, CONTEXT_NO, RCD_ERR, RCD_EST, CALIBRATION):
    """Calculates acceptance probability"""
    h_vec = [
        dict_seek_ordered(A, P, j[0], i, site_dict, THETAS, CONTEXT_NO, RCD_ERR, RCD_EST, CALIBRATION)
        for i in site_dict.keys()
        for j in enumerate(site_dict[i]["dates"])
    ]
    hh_1 = [i[0] for i in h_vec]
    hh_2 = [i[1] for i in h_vec]
    return hh_1, hh_2


def dict_seek_4(i_dict, key, site_dict):
    """Finds probabilities for all paramters in sample"""
    phase_len = site_dict[key]["boundaries"][0] - site_dict[key]["boundaries"][1]
    theta = site_dict[key]["dates"][i_dict][0]
    llhood = site_dict[key]["dates"][i_dict][1]
    ind_dic = np.where(llhood[0:][0] == int(theta))[0][0]
    li_vec = llhood[0:][0][ind_dic : ind_dic + 11]
    res = min(enumerate(li_vec), key=lambda x: abs(theta - x[1]))
    c_vec = np.where(llhood[0:][0] == res[1])
    x_temp = llhood[1:][0][c_vec[0]][0]
    x_tot = x_temp / phase_len
    return x_temp, x_tot


def post_h_theta_phi_4(site_dict):
    """Calculates posterior prob for step 4"""
    h_vec = [dict_seek_4(j[0], i, site_dict) for i in site_dict.keys() for j in enumerate(site_dict[i]["dates"])]
    hj_1 = [i[0] for i in h_vec]
    hj_2 = [i[1] for i in h_vec]
    return hj_1, hj_2


def dict_update(test_dict_2, post_t, post_p, inter, inter2, POST_PHASE, PHI_REF):
    """Updates the site dictionary"""
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
    """Gives a list of inital phase boundary values for MCMC"""
    PHASE_INITS = []
    KEY_REF_1 = np.array(key_reff)
    PHASE_INITS.append(
        np.random.uniform(max([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[0])[0].tolist()]), P)
    )
    for j in range(1, len(phi_reff)):
        a_temp = np.random.uniform(
            max([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[j])[0].tolist()]),
            min([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[j - 1])[0].tolist()]),
        )
        if prev_phases[j] != "abutting":
            a_temp = [
                a_temp,
                (
                    np.random.uniform(
                        max([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[j])[0].tolist()]),
                        min([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[j - 1])[0].tolist()]),
                    )
                ),
            ]
            a_temp = sorted(a_temp, reverse=True)
        else:
            a_temp = [a_temp]
        [PHASE_INITS.append(ref_ind) for ref_ind in a_temp]
    PHASE_INITS.append(
        np.random.uniform(min([theta_initt[i] for i in np.where(KEY_REF_1 == phi_reff[-1])[0].tolist()]), A)
    )
    PHASE_INITS1 = sorted(PHASE_INITS, reverse=True)
    return PHASE_INITS1


def theta_init_func(KEY_REF1, PHI_REF1, RESULT_VEC1):
    """Gives a list of inital theta values for MCMC"""
    out_vec = [0] * len(KEY_REF1)
    uplimref = np.where(np.array(KEY_REF1) == PHI_REF1[0])[0].tolist()
    up_lim_vec = [np.random.choice(RESULT_VEC1[date][0], p=RESULT_VEC1[date][1]).item() for date in uplimref]
    for i, a in enumerate(uplimref):
        out_vec[a] = up_lim_vec[i]
    prev_min = min(up_lim_vec)
    for date in range(1, len(PHI_REF1)):
        ref_vec = np.where(np.array(KEY_REF1) == PHI_REF1[date])[0].tolist()
        theta, prob = RESULT_VEC1[date][0], RESULT_VEC1[date][1]
        theta_vals = [
            np.random.choice(theta[theta < prev_min], p=prob[theta < prev_min] / sum(prob[theta < prev_min]))
            for date in ref_vec
        ]
        prev_min = min(theta_vals)
        for i, a in enumerate(ref_vec):
            out_vec[a] = theta_vals[i]
    return out_vec


def theta_init_func_n(KEY_REF1, PHI_REF1, RESULT_VEC1, STRAT_VEC, P, CONTEXT_NO, TOPO_SORT):
    """Gives a list of inital theta values for MCMC"""
    out_vec = [0] * len(KEY_REF1)
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
                out_vec[a] = np.random.choice(SAMPLE_VEC, p=SAMPLE_VEC_PROB / sum(SAMPLE_VEC_PROB))
            else:
                minstrat = min([out_vec[np.where(np.array(CONTEXT_NO) == j)[0][0].item()] for j in low])
                SAMPLE_VEC = RESULT_VEC1[a][0][RESULT_VEC1[a][0] < min(minstrat, prev_min)]
                SAMPLE_VEC_PROB = RESULT_VEC1[a][1][RESULT_VEC1[a][0] < min(minstrat, prev_min)]
                out_vec[a] = np.random.choice(SAMPLE_VEC, p=SAMPLE_VEC_PROB / sum(SAMPLE_VEC_PROB))
        prev_min = min([d for d in out_vec if d != 0])
    return out_vec


# sampling functions
def upp_samp_1(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Upper sample 1 - oldest phase and next phase abutting or gap"""
    limits = [
        max(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m + 1]]
        ),
        P,
    ]
    _ = phis_samp
    return limits


def upp_samp_2(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Upper sample 2 - oldest phase and next phase is overlapping"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m + 2])
    limits = [max(in_phase_dates), P]
    _ = phis_samp
    return limits


def upp_samp_3(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Upper sample 3 - phase with prev phase abbuting and next phase abbuting or gap"""
    limits = [
        max(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m + 1]]
        ),
        min(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m - 1]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m - 2]]
        ),
    ]
    _ = phis_samp
    return limits


def upp_samp_4(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Upper sample 4 - phase with prev phase abbuting and next phase overlap"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m - 1]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m + 2])
    limits = [
        max(in_phase_dates),
        min(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m - 2]]
        ),
    ]
    return limits


def upp_samp_5(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Upper sample 5 - phase with prev phase overlap, next phase can be any relationship"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m - 1])
    limits = [max(in_phase_dates), phis_samp[m - 2]]
    return limits


def upp_samp_6(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Upper sample 6 - phase with prev phase gap next phase abbuting or gap"""
    limits = [
        max(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m + 1]]
        ),
        phis_samp[m - 1],
    ]
    return limits


def upp_samp_7(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Upper sample 7 - phase with previous phase gap and next phase overlap"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m + 2])
    limits = [max(in_phase_dates), phis_samp[m - 1]]
    return limits


def upp_samp_8(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Upper sample 8 - phase with previous 2 overlapping, same as overlap samp_2, should delete"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m - 1])
    limits = [max(in_phase_dates), phis_samp[m - 3]]
    return limits


def low_samp_1(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Lower sample 1 prev phase start, abbuting or gap and next phase abbuting"""
    limits = [
        max(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m + 1]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m + 1]]
        ),
        min(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m - 1]]
        ),
    ]
    _ = phis_samp
    return limits


def low_samp_2(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Lower sample 2 next phase abbuting and prev phase overlapping"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m - 2])
    limits = [
        max(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m + 1]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m + 1]]
        ),
        min(in_phase_dates),
    ]
    return limits


def low_samp_3(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Lower sample 3: next phase overlapping and prev phase can be any relationship"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m + 1])
    limits = [phis_samp[m + 2], min(in_phase_dates)]
    return limits


def low_samp_4(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Lower sample 4 next phase gap and prev phase can be any relationship except overlap"""
    limits = [
        phis_samp[m + 1],
        min(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m - 1]]
        ),
    ]
    return limits


def low_samp_5(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Lower sample 5"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m - 2])
    limits = [phis_samp[m + 1], min(in_phase_dates)]
    return limits


def low_samp_6(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Lower sample 6"""
    limits = [
        A,
        min(
            [
                theta_samp[i]
                for i, j in enumerate(KEY_REF)
                if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
            ]
            + [phis_samp[m - 1]]
        ),
    ]
    _ = phis_samp
    return limits


def low_samp_7(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Lower sample 7"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m - 2])
    limits = [A, min(in_phase_dates)]
    return limits


def overlap_samp_1(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Overlap sample 1 - if previous two samples are overlapping and next phase can be any relationship"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m - 1])
    limits = [max(in_phase_dates), phis_samp[m - 3]]
    return limits


def overlap_samp_2(theta_samp, phis_samp, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE):
    """Overlap sample 2"""
    in_phase_dates = [
        theta_samp[i] for i, j in enumerate(KEY_REF) if j == PHI_REF[SAMP_VEC_TRACK[m]] and CONT_TYPE[i] == "normal"
    ]
    in_phase_dates.append(phis_samp[m + 1])
    limits = [phis_samp[m + 3], min(in_phase_dates)]
    return limits


def initialise(CALIBRATION, RCD_EST, RCD_ERR):
    #  method  = 'squeeze'
    CALIBRATION_DATA = CALIBRATION.to_dict()
    x_min = min(RCD_EST)
    s = max(RCD_ERR)
    x_max = max(RCD_EST)
    mydict = CALIBRATION_DATA["Carbon_year"]
    a = list(mydict.values())
    p = min(range(len(a)), key=lambda i: abs(a[i] - x_min))
    l = min(range(len(a)), key=lambda i: abs(a[i] - x_max))
    A = max(p - 20 * s, 0)
    P = min(l + 20 * s, 50000)
    # initiating  likelihoods
    RCD_S = [list(x) for x in zip(RCD_EST, RCD_ERR)]
    RESULT_VEC = [likelihood_func(date[0], date[1], A, P, CALIBRATION_DATA) for date in RCD_S]
    return A, P, RESULT_VEC


def dict_form_func(
    THETA_INITS,
    RESULT_VEC,
    CONTEXT_NO,
    STRAT_VEC,
    PHASE_BOUNDARY_INITS,
    POST_PHASE,
    PHI_REF,
    PREV_PHASE,
    KEY_REF,
    CONT_TYPE,
):
    """Initiating the inital dict"""
    NEW_LST = [list(x) for x in zip(THETA_INITS, RESULT_VEC, CONTEXT_NO, STRAT_VEC, CONT_TYPE)]
    CV_B = phase_limits(PHASE_BOUNDARY_INITS, POST_PHASE)
    PHIS_VEC = PHASE_BOUNDARY_INITS
    THETAS = THETA_INITS
    TRACK_VEC = []
    KEYS_TRACK = []
    for d in PHI_REF:
        ind = [index for index, element in enumerate(KEY_REF) if element == d]
        test_lst = [NEW_LST[d] for d in ind]
        bound = CV_B[PHI_REF.index(d)]
        TRACK_VEC.append(
            {
                "dates": test_lst,
                "boundaries": bound,
                "prev_phase_rel": PREV_PHASE[PHI_REF.index(d)],
                "post_phase_rel": POST_PHASE[PHI_REF.index(d)],
            }
        )
        KEYS_TRACK.append(d)

    TEST_DICT_1 = dict(zip(KEYS_TRACK, TRACK_VEC))
    SITE_DICT_TEST_1 = TEST_DICT_1
    return SITE_DICT_TEST_1, THETAS, PHIS_VEC, TEST_DICT_1


def how_to_phase_samp(POST_PHASE, PREV_PHASE):
    STEP_1 = sampling_vec(POST_PHASE, PREV_PHASE)[0]
    SAMP_VEC_TRACK = sampling_vec(POST_PHASE, PREV_PHASE)[1]
    STEP_2 = [PREV_PHASE[i] for i in SAMP_VEC_TRACK]
    STEP_3 = [POST_PHASE[i] for i in SAMP_VEC_TRACK]
    return STEP_1, STEP_2, STEP_3, SAMP_VEC_TRACK


def set_up_post_arrays(THETAS, PHIS_VEC, THETA_INITS, PHASE_BOUNDARY_INITS):
    POST_THETAS = [[] for _ in range(len(THETAS))]
    POST_PHIS = [[] for _ in range(len(PHIS_VEC))]
    for p, a in enumerate(THETA_INITS):
        POST_THETAS[p].append(a)
    for j, b in enumerate(PHASE_BOUNDARY_INITS):
        POST_PHIS[j].append(b)
    POST_S = [max(PHASE_BOUNDARY_INITS) - min(PHASE_BOUNDARY_INITS) + 50]
    return POST_THETAS, POST_PHIS, POST_S


def posterior_plots(ACCEPT, CONTEXT_NO, PHI_REF, PHI_ACCEPT, A, P):
    for n, m in enumerate(CONTEXT_NO):
        plt.figure()
        k, bins, patches = plt.hist(ACCEPT[n], bins="auto", color="#0504aa", alpha=0.7, rwidth=0.85, density=True)
        plt.gca().invert_xaxis()
        plt.ioff()
        file_name = str("Posterior_density_context_" + str(m))
        plt.savefig(file_name)
    plt.close("all")
    for q, w in enumerate(PHI_ACCEPT):
        plt.figure()
        k, bins, patches = plt.hist(PHI_ACCEPT[q], bins="auto", color="#0504aa", alpha=0.7, rwidth=0.85, density=True)
        plt.title("Posterior distributions \n for phase boundary estimates")
        plt.xlabel("Estimate for upper most phase boundary in Cal BP")
        plt.ylabel("Probability")
        plt.gca().invert_xaxis()
        plt.ioff()
        file_name = str("Posterior_density_phase_" + str(q))
        plt.savefig(file_name)
        plt.close("all")


def get_hpd_intervals(CONTEXT_NO, ACCEPT, PHI_ACCEPT):
    hpd_dict = {}
    for i, j in enumerate(CONTEXT_NO):
        hpd_dict[j] = list(HPD_interval(np.array(ACCEPT[i][1000:])))
    hpd_df = pd.DataFrame.from_dict(hpd_dict, orient="index")
    hpd_df.to_csv("resid_hpd_intervals_thetas_correct", index=False)
    hpd_dict = {}
    for k, l in enumerate(PHI_ACCEPT):
        hpd_dict[k] = list(HPD_interval(PHI_ACCEPT[k][1000:]))
    hpd_df = pd.DataFrame.from_dict(hpd_dict, orient="index")
    hpd_df.to_csv("resid_hpd_intervals_phis_correct", index=False)


def gibbs_code(
    iter_num,
    RESULT_VEC,
    A,
    P,
    KEY_REF,
    PHI_REF,
    STRAT_VEC,
    CONTEXT_NO,
    TOPO_SORT,
    PREV_PHASE,
    POST_PHASE,
    PHI_SAMP_DICT,
    CONT_TYPE,
    PROGRESS_IO: Writable | None = None,
):
    THETA_INITS = theta_init_func_n(KEY_REF, PHI_REF, RESULT_VEC, STRAT_VEC, P, CONTEXT_NO, TOPO_SORT)
    PHASE_BOUNDARY_INITS = phase_bd_init_func(KEY_REF, PHI_REF, THETA_INITS, PREV_PHASE, A, P)
    TEST_DICT_1, POST_THETAS, POST_PHIS, SITE_DICT_TEST_1 = dict_form_func(
        THETA_INITS, RESULT_VEC, CONTEXT_NO, STRAT_VEC, PHASE_BOUNDARY_INITS, POST_PHASE, PHI_REF, PREV_PHASE, CONT_TYPE
    )
    STEP_1, STEP_2, STEP_3, SAMP_VEC_TRACK = how_to_phase_samp(POST_PHASE, PREV_PHASE)
    PHIS_VEC = PHASE_BOUNDARY_INITS
    THETAS = THETA_INITS.copy()
    ########################### figures out how to sample based on phase relationships
    M = len(POST_PHIS)
    P = 4000
    POST_THETAS, POST_PHIS, POST_S = set_up_post_arrays(POST_THETAS, POST_PHIS, THETA_INITS, PHASE_BOUNDARY_INITS)
    POST_S = []
    for i in range(0, iter_num):
        for k in range(len(THETA_INITS)):
            SITE_DICT_TEST_1 = dict_update(SITE_DICT_TEST_1, POST_THETAS, POST_PHIS, i, i, POST_PHASE, PHI_REF)
            key = KEY_REF[k]
            a = [CONTEXT_NO[k] in d for d in SITE_DICT_TEST_1[key]["dates"]].index(True)
            strat_single = strat_rel(SITE_DICT_TEST_1, key, a, THETAS, CONTEXT_NO)
            low_bound = max(SITE_DICT_TEST_1[key]["boundaries"][0], strat_single[1])
            up_bound = min(SITE_DICT_TEST_1[key]["boundaries"][1], strat_single[0])
            SAMPLE_VEC = RESULT_VEC[k][0][(RESULT_VEC[k][0] < up_bound) & (RESULT_VEC[k][0] > low_bound)]
            SAMPLE_VEC_PROB = RESULT_VEC[k][1][(RESULT_VEC[k][0] < up_bound) & (RESULT_VEC[k][0] > low_bound)]
            THETAS[k] = random.choices(SAMPLE_VEC, weights=SAMPLE_VEC_PROB / sum(SAMPLE_VEC_PROB))[0]
            POST_THETAS[k].append(THETAS[k])
        for j in range(len(PHASE_BOUNDARY_INITS)):
            k = gibbs_phis_gen(PREV_PHASE, PHI_REF)[j]
            lims = PHI_SAMP_DICT[STEP_1[j]][STEP_2[j]][STEP_3[j]](
                THETAS, PHIS_VEC, j, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE
            )
            bounds = SITE_DICT_TEST_1[str(k)]["boundaries"]
            phi_vals = np.linspace(lims[0] + 0.1, lims[1] - 0.1, num=int((lims[1] - lims[0]) * 20))
            length = len(SITE_DICT_TEST_1[k]["dates"])
            if j == 0:
                phase_samps = np.array([1 / ((i - bounds[0]) ** length) for i in phi_vals])
            else:
                phase_samps = np.array([1 / ((bounds[1] - i) ** length) for i in phi_vals])
            weights = phase_samps / sum(phase_samps)
            PHIS_VEC[j] = random.choices(phi_vals, weights)[0]
            POST_PHIS[j].append(PHIS_VEC[j])
        POST_S.append(PHIS_VEC[0] - PHIS_VEC[M - 1])
    PHI_ACCEPT, ACCEPT = POST_PHIS, POST_THETAS
    return PHI_ACCEPT, ACCEPT, POST_S


def step_1_squeeze(
    A,
    P,
    i,
    PREV_PROB_TEST,
    K,
    ACCEPT,
    SITE_DICT_TEST_1,
    SITE_DICT_TEST_2,
    THETAS,
    POST_THETAS,
    POST_PHIS,
    KEY_REF,
    CONTEXT_NO,
    POST_PHASE,
    PHI_REF,
    RCD_ERR,
    RCD_EST,
    CALIBRATION,
    ALL_SAMPS_CONT,
    ALL_SAMPS_PHI,
    PHIS_VEC,
    CONT_TYPE,
):
    k = int(random.sample(range(0, K), 1)[0])
    oldtheta = THETAS[k]
    cont_type = CONT_TYPE[k]
    key = KEY_REF[k]
    a = [CONTEXT_NO[k] in i for i in SITE_DICT_TEST_1[key]["dates"]].index(True)
    strat_single = strat_rel(SITE_DICT_TEST_1, key, a, THETAS, CONTEXT_NO)
    if cont_type == "normal":
        THETAS[k] = np.random.uniform(
            max(SITE_DICT_TEST_1[key]["boundaries"][0], strat_single[1]),
            min(SITE_DICT_TEST_1[key]["boundaries"][1], strat_single[0]),
        )
    elif cont_type == "intrusive":
        THETAS[k] = np.random.uniform(A, min(SITE_DICT_TEST_1[key]["boundaries"][1], strat_single[0]))
    elif cont_type == "residual":
        THETAS[k] = np.random.uniform(max(SITE_DICT_TEST_1[key]["boundaries"][0], strat_single[1]), P)
    for g_1 in enumerate(THETAS):
        POST_THETAS[g_1[0]].append(THETAS[g_1[0]])
    SITE_DICT_TEST_2 = dict_update(SITE_DICT_TEST_2, POST_THETAS, POST_PHIS, i + 1, i, POST_PHASE, PHI_REF)
    prob_1_test = post_h(A, P, SITE_DICT_TEST_2, THETAS, CONTEXT_NO, RCD_ERR, RCD_EST, CALIBRATION)[1]
    c_test = []
    for j_1, a_1 in enumerate(prob_1_test):
        if PREV_PROB_TEST[j_1] == 0:
            c_test.append(0)
        else:
            c_test.append(a_1 / PREV_PROB_TEST[j_1])
    h_1 = np.prod(c_test)
    if h_1 >= 1:
        ACCEPT[k].append(THETAS[k])
        [ALL_SAMPS_CONT[j].append(THETAS[j]) for j in range(len(THETAS))]
        [ALL_SAMPS_PHI[j].append(PHIS_VEC[j]) for j in range(len(PHIS_VEC))]
    else:
        u = np.random.uniform(0, 1)
        if h_1 > u:
            ACCEPT[k].append(THETAS[k])
            [ALL_SAMPS_CONT[j].append(THETAS[j]) for j in range(len(THETAS))]
            [ALL_SAMPS_PHI[j].append(PHIS_VEC[j]) for j in range(len(PHIS_VEC))]
        else:
            THETAS[k] = oldtheta
            for g2 in range(len(THETAS)):
                POST_THETAS[g2][i + 1] = POST_THETAS[g2][i]
            prob_1_test = PREV_PROB_TEST
    return prob_1_test, ACCEPT, SITE_DICT_TEST_1, SITE_DICT_TEST_2, THETAS, POST_THETAS, POST_PHIS, ALL_SAMPS_CONT


def step_2_squeeze(
    i,
    prob_1_test,
    M,
    PHI_SAMP_DICT,
    POST_S,
    R,
    PHIS_VEC,
    SITE_DICT_TEST_3,
    THETAS,
    POST_THETAS,
    POST_PHIS,
    STEP_1,
    STEP_2,
    STEP_3,
    A,
    P,
    SAMP_VEC_TRACK,
    PHI_ACCEPT,
    KEY_REF,
    PHI_REF,
    CONTEXT_NO,
    RCD_ERR,
    POST_PHASE,
    RCD_EST,
    CALIBRATION,
    ALL_SAMPS_CONT,
    ALL_SAMPS_PHI,
    CONT_TYPE,
):
    m = int(random.sample(range(0, M), 1)[0])
    s1 = max(PHIS_VEC) - min(PHIS_VEC)
    f_phi1 = (s1 ** (2 - M)) / (R - s1)
    oldphi = PHIS_VEC[m]
    lims = PHI_SAMP_DICT[STEP_1[m]][STEP_2[m]][STEP_3[m]](
        THETAS, PHIS_VEC, m, A, P, SAMP_VEC_TRACK, KEY_REF, PHI_REF, CONT_TYPE
    )
    PHIS_VEC[m] = np.random.uniform(lims[0], lims[1])
    for v1, a_2 in enumerate(PHIS_VEC):
        POST_PHIS[v1].append(a_2)
    s2 = max(PHIS_VEC) - min(PHIS_VEC)
    f_phi2 = (s2 ** (2 - M)) / (R - s2)
    SITE_DICT_TEST_3 = dict_update(SITE_DICT_TEST_3, POST_THETAS, POST_PHIS, i + 1, i + 1, POST_PHASE, PHI_REF)
    step_2_prob = post_h(A, P, SITE_DICT_TEST_3, THETAS, CONTEXT_NO, RCD_ERR, RCD_EST, CALIBRATION)
    prob_2_test = step_2_prob[1]
    backup_b_test = step_2_prob[0]
    c_test = []
    for k_2, b_2 in enumerate(prob_2_test):
        if prob_1_test[k_2] == 0:
            c_test.append(0)
        else:
            c_test.append(b_2 / prob_1_test[k_2])
    h_2 = np.prod(c_test) * (f_phi2 / f_phi1)
    if h_2 >= 1:
        PHI_ACCEPT[m].append(PHIS_VEC[m])
        [ALL_SAMPS_PHI[j].append(PHIS_VEC[j]) for j in range(len(PHIS_VEC))]
        [ALL_SAMPS_CONT[j].append(THETAS[j]) for j in range(len(THETAS))]
        if m == M - 1:
            POST_S.append(max(PHIS_VEC) - PHIS_VEC[m])
        elif m == 0:
            POST_S.append(PHIS_VEC[m] - min(PHIS_VEC))
    else:
        u = np.random.uniform(0, 1)
        if h_2 > u:
            PHI_ACCEPT[m].append(PHIS_VEC[m])
            [ALL_SAMPS_CONT[j].append(THETAS[j]) for j in range(len(THETAS))]
            [ALL_SAMPS_PHI[j].append(PHIS_VEC[j]) for j in range(len(PHIS_VEC))]
            if m == M - 1:
                POST_S.append(max(PHIS_VEC) - PHIS_VEC[m])
            elif m == 0:
                POST_S.append(PHIS_VEC[m] - min(PHIS_VEC))
        else:
            for v2 in enumerate(PHIS_VEC):
                POST_PHIS[v2[0]][i + 1] = POST_PHIS[v2[0]][i]
            PHIS_VEC[m] = oldphi
            prob_2_test = prob_1_test
    return (
        backup_b_test,
        prob_2_test,
        POST_S,
        PHIS_VEC,
        SITE_DICT_TEST_3,
        THETAS,
        POST_THETAS,
        POST_PHIS,
        PHI_ACCEPT,
        ALL_SAMPS_PHI,
    )


def step_3_squeeze(
    A,
    P,
    i,
    backup_b_test,
    prob_2_test,
    S,
    ACCEPT,
    POST_S,
    PHIS_VEC,
    SITE_DICT_TEST_4,
    THETAS,
    POST_THETAS,
    POST_PHIS,
    PHI_ACCEPT,
    POST_PHASE,
    PHI_REF,
    CONTEXT_NO,
    RCD_ERR,
    RCD_EST,
    CALIBRATION,
    ALL_SAMPS_CONT,
    ALL_SAMPS_PHI,
):
    step = np.random.uniform(max(-1 * S, A - min(PHIS_VEC)), 1 * S)
    THETAS = [x + step for x in THETAS]
    PHIS_VEC = [x + step for x in PHIS_VEC]
    for g2, a_3 in enumerate(THETAS):
        POST_THETAS[g2].append(a_3)
    for v2, b_3 in enumerate(PHIS_VEC):
        POST_PHIS[v2].append(b_3)
    SITE_DICT_TEST_4 = dict_update(SITE_DICT_TEST_4, POST_THETAS, POST_PHIS, i + 2, i + 2, POST_PHASE, PHI_REF)
    temp = post_h(A, P, SITE_DICT_TEST_4, THETAS, CONTEXT_NO, RCD_ERR, RCD_EST, CALIBRATION)
    prob_3_test = temp[1]
    b_test = temp[0]
    c_test = []
    for f, c_3 in enumerate(prob_3_test):
        if prob_2_test[f] == 0:
            c_test.append(0)
        else:
            c_test.append(c_3 / prob_2_test[f])
    h_3 = np.prod(c_test)
    if h_3 >= 1:
        for j_3, d_3 in enumerate(PHIS_VEC):
            PHI_ACCEPT[j_3].append(d_3)
            ALL_SAMPS_PHI[j_3].append(d_3)
        for k_3, e_3 in enumerate(THETAS):
            ACCEPT[k_3].append(e_3)
            ALL_SAMPS_CONT[k_3].append(e_3)
        POST_S.append(max(PHIS_VEC) - min(PHIS_VEC))
    else:
        u = np.random.uniform(0, 1)
        if h_3 > u:
            for j_3, f_3 in enumerate(PHIS_VEC):
                PHI_ACCEPT[j_3].append(f_3)
                ALL_SAMPS_PHI[j_3].append(f_3)
            for k_3, i_3 in enumerate(THETAS):
                ACCEPT[k_3].append(i_3)
                ALL_SAMPS_CONT[k_3].append(i_3)
            POST_S.append(max(PHIS_VEC) - min(PHIS_VEC))
        else:
            for g_3 in enumerate(THETAS):
                POST_THETAS[g_3[0]][i + 2] = POST_THETAS[g_3[0]][i + 1]
            for v_3 in enumerate(PHIS_VEC):
                POST_PHIS[v_3[0]][i + 2] = POST_PHIS[v_3[0]][i + 1]
            THETAS = [x - step for x in THETAS]
            PHIS_VEC = [x - step for x in PHIS_VEC]
            prob_3_test = prob_2_test
            b_test = backup_b_test
    return (
        b_test,
        prob_3_test,
        ACCEPT,
        POST_S,
        PHIS_VEC,
        SITE_DICT_TEST_4,
        THETAS,
        POST_THETAS,
        POST_PHIS,
        PHI_ACCEPT,
        ALL_SAMPS_CONT,
        ALL_SAMPS_PHI,
    )


def step_4_squeeze(
    A,
    P,
    i,
    b_test,
    prob_3_test,
    ACCEPT,
    POST_S,
    R,
    PHIS_VEC,
    SITE_DICT_TEST_5,
    THETAS,
    POST_THETAS,
    POST_PHIS,
    PHI_ACCEPT,
    POST_PHASE,
    PHI_REF,
    CONTEXT_NO,
    RCD_ERR,
    RCD_EST,
    CALIBRATION,
    ALL_SAMPS_CONT,
    ALL_SAMPS_PHI,
):
    m = mean(np.concatenate([PHIS_VEC, THETAS])).item()
    scale_limit = m / (m - min(PHIS_VEC))
    rho = np.random.uniform(2 / 3, scale_limit)
    constant = (rho - 1) * m
    THETAS = [x * rho - constant for x in THETAS]
    PHIS_VEC = [x * rho - constant for x in PHIS_VEC]
    for s_4, a_4 in enumerate(THETAS):
        POST_THETAS[s_4].append(a_4)
    for e_4, b_4 in enumerate(PHIS_VEC):
        POST_PHIS[e_4].append(b_4)
    SITE_DICT_TEST_5 = dict_update(SITE_DICT_TEST_5, POST_THETAS, POST_PHIS, i + 3, i + 3, POST_PHASE, PHI_REF)
    s = max(PHIS_VEC) - min(PHIS_VEC)
    const = (R - s) / ((R - (rho * s)) * rho)
    temp_2 = post_h(A, P, SITE_DICT_TEST_5, THETAS, CONTEXT_NO, RCD_ERR, RCD_EST, CALIBRATION)
    a_test = temp_2[0]
    PREV_PROB_TEST = temp_2[1]
    c_test = []
    for q_4, k_4 in enumerate(a_test):
        if b_test[q_4] == 0:
            c_test.append(0)
        else:
            c_test.append(k_4 / b_test[q_4])
    h_temp_test = np.prod(c_test)
    h_4 = h_temp_test * const
    if h_4 >= 1:
        for j_4, c_4 in enumerate(PHIS_VEC):
            PHI_ACCEPT[j_4].append(c_4)
            ALL_SAMPS_PHI[j_4].append(c_4)
        for k_4, f_4 in enumerate(THETAS):
            ACCEPT[k_4].append(f_4)
            ALL_SAMPS_CONT[k_4].append(f_4)
        POST_S.append(max(PHIS_VEC) - min(PHIS_VEC))
    else:
        u = np.random.uniform(0, 1)
        if h_4 > u:
            for j_4, g_4 in enumerate(PHIS_VEC):
                PHI_ACCEPT[j_4].append(g_4)
                ALL_SAMPS_PHI[j_4].append(g_4)
            for k_4, i_4 in enumerate(THETAS):
                ACCEPT[k_4].append(i_4)
                ALL_SAMPS_CONT[k_4].append(i_4)
            POST_S.append(max(PHIS_VEC) - min(PHIS_VEC))
        else:
            for g_4 in range(len(THETAS)):
                POST_THETAS[g_4][i + 3] = POST_THETAS[g_4][i + 2]
            for v_4 in range(len(PHIS_VEC)):
                POST_PHIS[v_4][i + 3] = POST_PHIS[v_4][i + 2]
            THETAS = [(x + constant) / rho for x in THETAS]
            PHIS_VEC = [(x + constant) / rho for x in PHIS_VEC]
            PREV_PROB_TEST = prob_3_test
    return (
        PREV_PROB_TEST,
        ACCEPT,
        POST_S,
        PHIS_VEC,
        SITE_DICT_TEST_5,
        THETAS,
        POST_THETAS,
        POST_PHIS,
        PHI_ACCEPT,
        ALL_SAMPS_CONT,
        ALL_SAMPS_PHI,
    )


def squeeze_model(
    PHI_SAMP_DICT,
    RESULT_VEC,
    A,
    P,
    RCD_ERR,
    KEY_REF,
    STRAT_VEC,
    CONTEXT_NO,
    TOPO_SORT,
    PREV_PHASE,
    POST_PHASE,
    PHI_REF,
    RCD_EST,
    CALIBRATION,
    CONT_TYPE,
    PROGRESS_IO: Writable | None = None,
):
    acept_prob = 1
    while acept_prob > 0:
        THETA_INITS = theta_init_func_n(KEY_REF, PHI_REF, RESULT_VEC, STRAT_VEC, P, CONTEXT_NO, TOPO_SORT)
        PHASE_BOUNDARY_INITS = phase_bd_init_func(KEY_REF, PHI_REF, THETA_INITS, PREV_PHASE, A, P)
        SITE_DICT_TEST_1, THETAS, PHIS_VEC, TEST_DICT_1 = dict_form_func(
            THETA_INITS,
            RESULT_VEC,
            CONTEXT_NO,
            STRAT_VEC,
            PHASE_BOUNDARY_INITS,
            POST_PHASE,
            PHI_REF,
            PREV_PHASE,
            KEY_REF,
            CONT_TYPE,
        )
        STEP_1, STEP_2, STEP_3, SAMP_VEC_TRACK = how_to_phase_samp(POST_PHASE, PREV_PHASE)
        ########################### figures out how to sample based on phase relationships
        K = len(THETAS)
        M = len(PHIS_VEC)
        S = max(RCD_ERR)
        R = P - A
        POST_THETAS, POST_PHIS, POST_S = set_up_post_arrays(THETAS, PHIS_VEC, THETA_INITS, PHASE_BOUNDARY_INITS)
        PREV_PROB_TEST = post_h(A, P, SITE_DICT_TEST_1, THETAS, CONTEXT_NO, RCD_ERR, RCD_EST, CALIBRATION)[1]
        SITE_DICT_TEST_2 = TEST_DICT_1
        SITE_DICT_TEST_3 = TEST_DICT_1
        SITE_DICT_TEST_4 = TEST_DICT_1
        SITE_DICT_TEST_5 = TEST_DICT_1
        ACCEPT = [[] for _ in range(len(THETAS))]
        PHI_ACCEPT = [[] for _ in range(len(PHIS_VEC))]
        ALL_SAMPS_CONT = [[] for _ in range(len(THETAS))]
        ALL_SAMPS_PHI = [[] for _ in range(len(PHIS_VEC))]
        i = 0
        ###START OF MCMC ALGORITHM###############
        while min([len(i) for i in ACCEPT]) < 60000:
            progress_percent = int((min([len(i) for i in ACCEPT]) / 60000) * 100)
            print(progress_percent, file=PROGRESS_IO)
            for l in np.linspace(0, 10002, 3335):
                SITE_DICT_TEST_1 = dict_update(SITE_DICT_TEST_1, POST_THETAS, POST_PHIS, i, i, POST_PHASE, PHI_REF)
                # step 1
                (
                    prob_1_test,
                    ACCEPT,
                    SITE_DICT_TEST_1,
                    SITE_DICT_TEST_2,
                    THETAS,
                    POST_THETAS,
                    POST_PHIS,
                    ALL_SAMPS_CONT,
                ) = step_1_squeeze(
                    A,
                    P,
                    i,
                    PREV_PROB_TEST,
                    K,
                    ACCEPT,
                    SITE_DICT_TEST_1,
                    SITE_DICT_TEST_2,
                    THETAS,
                    POST_THETAS,
                    POST_PHIS,
                    KEY_REF,
                    CONTEXT_NO,
                    POST_PHASE,
                    PHI_REF,
                    RCD_ERR,
                    RCD_EST,
                    CALIBRATION,
                    ALL_SAMPS_CONT,
                    ALL_SAMPS_PHI,
                    PHIS_VEC,
                    CONT_TYPE,
                )
                # step 2
                (
                    backup_b_test,
                    prob_2_test,
                    POST_S,
                    PHIS_VEC,
                    SITE_DICT_TEST_3,
                    THETAS,
                    POST_THETAS,
                    POST_PHIS,
                    PHI_ACCEPT,
                    ALL_SAMPS_PHI,
                ) = step_2_squeeze(
                    i,
                    prob_1_test,
                    M,
                    PHI_SAMP_DICT,
                    POST_S,
                    R,
                    PHIS_VEC,
                    SITE_DICT_TEST_3,
                    THETAS,
                    POST_THETAS,
                    POST_PHIS,
                    STEP_1,
                    STEP_2,
                    STEP_3,
                    A,
                    P,
                    SAMP_VEC_TRACK,
                    PHI_ACCEPT,
                    KEY_REF,
                    PHI_REF,
                    CONTEXT_NO,
                    RCD_ERR,
                    POST_PHASE,
                    RCD_EST,
                    CALIBRATION,
                    ALL_SAMPS_CONT,
                    ALL_SAMPS_PHI,
                    CONT_TYPE,
                )
                # step3
                (
                    b_test,
                    prob_3_test,
                    ACCEPT,
                    POST_S,
                    PHIS_VEC,
                    SITE_DICT_TEST_4,
                    THETAS,
                    POST_THETAS,
                    POST_PHIS,
                    PHI_ACCEPT,
                    ALL_SAMPS_CONT,
                    ALL_SAMPS_PHI,
                ) = step_3_squeeze(
                    A,
                    P,
                    i,
                    backup_b_test,
                    prob_2_test,
                    S,
                    ACCEPT,
                    POST_S,
                    PHIS_VEC,
                    SITE_DICT_TEST_4,
                    THETAS,
                    POST_THETAS,
                    POST_PHIS,
                    PHI_ACCEPT,
                    POST_PHASE,
                    PHI_REF,
                    CONTEXT_NO,
                    RCD_ERR,
                    RCD_EST,
                    CALIBRATION,
                    ALL_SAMPS_CONT,
                    ALL_SAMPS_PHI,
                )
                # step 4
                (
                    PREV_PROB_TEST,
                    ACCEPT,
                    POST_S,
                    PHIS_VEC,
                    SITE_DICT_TEST_5,
                    THETAS,
                    POST_THETAS,
                    POST_PHIS,
                    PHI_ACCEPT,
                    ALL_SAMPS_CONT,
                    ALL_SAMPS_PHI,
                ) = step_4_squeeze(
                    A,
                    P,
                    i,
                    b_test,
                    prob_3_test,
                    ACCEPT,
                    POST_S,
                    R,
                    PHIS_VEC,
                    SITE_DICT_TEST_5,
                    THETAS,
                    POST_THETAS,
                    POST_PHIS,
                    PHI_ACCEPT,
                    POST_PHASE,
                    PHI_REF,
                    CONTEXT_NO,
                    RCD_ERR,
                    RCD_EST,
                    CALIBRATION,
                    ALL_SAMPS_CONT,
                    ALL_SAMPS_PHI,
                )
                i = i + 3
                # CHECK_ACCEPT = accept_prob(ACCEPT, PHI_ACCEPT, i)
                # acept_prob = len(CHECK_ACCEPT[(CHECK_ACCEPT <= 0.01) | (CHECK_ACCEPT >= 0.7)])
                # if acept_prob > 0:
                #     break
        # plot code
        #  CHECK_ACCEPT = accept_prob(ACCEPT, PHI_ACCEPT, i)
        return PHI_ACCEPT, ACCEPT, POST_S, ALL_SAMPS_CONT, ALL_SAMPS_PHI


def run_MCMC(
    CALIBRATION,
    STRAT_VEC,
    RCD_EST,
    RCD_ERR,
    KEY_REF,
    CONTEXT_NO,
    PHI_REF,
    PREV_PHASE,
    POST_PHASE,
    TOPO_SORT,
    CONT_TYPE,
    PROGRESS_IO: Writable | None = None,
):
    """Run the MCMC algorithm for a set of input data from a Model, returning the tuple of results"""
    #  t0 = time.perf_counter()
    PHI_SAMP_DICT = {
        "upper": {
            "start": {
                "abutting": upp_samp_1,
                "overlap": upp_samp_2,
                "gap": upp_samp_1,
                "end": upp_samp_1,
            },
            "abutting": {"abutting": upp_samp_3, "overlap": upp_samp_4, "gap": upp_samp_3, "end": upp_samp_3},
            "overlap": {"abutting": upp_samp_5, "overlap": upp_samp_5, "gap": upp_samp_5, "end": upp_samp_5},
            "gap": {"abutting": upp_samp_6, "overlap": upp_samp_7, "gap": upp_samp_6, "end": upp_samp_6},
        },
        "lower": {
            "start": {"abutting": low_samp_1, "overlap": low_samp_3, "gap": low_samp_4, "end": low_samp_6},
            "abutting": {"abutting": low_samp_1, "overlap": low_samp_3, "gap": low_samp_4, "end": low_samp_6},
            "overlap": {"abutting": low_samp_2, "overlap": low_samp_3, "gap": low_samp_5, "end": low_samp_7},
            "gap": {"abutting": low_samp_1, "overlap": low_samp_3, "gap": low_samp_4, "end": low_samp_6},
        },
        "combined": {
            "start": {"abutting": low_samp_1, "overlap": low_samp_3, "gap": low_samp_4, "end": low_samp_6},
            "abutting": {"abutting": low_samp_1, "overlap": low_samp_3, "gap": low_samp_4, "end": low_samp_6},
            "overlap": {"abutting": low_samp_2, "overlap": low_samp_3, "gap": low_samp_5, "end": low_samp_7},
            "gap": {"abutting": low_samp_1, "overlap": low_samp_3, "gap": low_samp_4, "end": low_samp_6},
        },
        "overlap_upper": {
            "start": {
                "abutting": overlap_samp_1,
                "overlap": overlap_samp_1,
                "gap": overlap_samp_1,
                "end": overlap_samp_1,
            },
            "abutting": {
                "abutting": overlap_samp_1,
                "overlap": overlap_samp_1,
                "gap": overlap_samp_1,
                "end": overlap_samp_1,
            },
            "overlap": {
                "abutting": overlap_samp_1,
                "overlap": overlap_samp_1,
                "gap": overlap_samp_1,
                "end": overlap_samp_1,
            },
            "gap": {
                "abutting": overlap_samp_1,
                "overlap": overlap_samp_1,
                "gap": overlap_samp_1,
                "end": overlap_samp_1,
            },
        },
        "overlap_beta": {
            "start": {
                "abutting": overlap_samp_2,
                "overlap": overlap_samp_2,
                "gap": overlap_samp_2,
                "end": overlap_samp_2,
            },
            "abutting": {
                "abutting": overlap_samp_2,
                "overlap": overlap_samp_2,
                "gap": overlap_samp_2,
                "end": overlap_samp_2,
            },
            "overlap": {
                "abutting": overlap_samp_2,
                "overlap": overlap_samp_2,
                "gap": overlap_samp_2,
                "end": overlap_samp_2,
            },
            "gap": {
                "abutting": overlap_samp_2,
                "overlap": overlap_samp_2,
                "gap": overlap_samp_2,
                "end": overlap_samp_2,
            },
        },
    }
    method = "squeeze"
    A, P, RESULT_VEC = initialise(CALIBRATION, RCD_EST, RCD_ERR)  #  tot_i = 0
    if method == "squeeze":
        PHI_ACCEPT, ACCEPT, POST_S, ALL_SAMPS_CONT, ALL_SAMPS_PHI = squeeze_model(
            PHI_SAMP_DICT,
            RESULT_VEC,
            A,
            P,
            RCD_ERR,
            KEY_REF,
            STRAT_VEC,
            CONTEXT_NO,
            TOPO_SORT,
            PREV_PHASE,
            POST_PHASE,
            PHI_REF,
            RCD_EST,
            CALIBRATION,
            CONT_TYPE,
            PROGRESS_IO,
        )
        _, ACCEPT_test_1, _, _, _ = squeeze_model(
            PHI_SAMP_DICT,
            RESULT_VEC,
            A,
            P,
            RCD_ERR,
            KEY_REF,
            STRAT_VEC,
            CONTEXT_NO,
            TOPO_SORT,
            PREV_PHASE,
            POST_PHASE,
            PHI_REF,
            RCD_EST,
            CALIBRATION,
            CONT_TYPE,
            PROGRESS_IO,
        )
        # checks = [GR_conv_check(np.array(j), np.array(ACCEPT_test_1[i])) for i,j in enumerate(ACCEPT)]
        # print(min(checks))
        # print(max(checks))
    elif method == "gibbs":
        PHI_ACCEPT, ACCEPT, POST_S, ALL_SAMPS_CONT, ALL_SAMPS_PHI = gibbs_code(
            5000,
            RESULT_VEC,
            A,
            P,
            KEY_REF,
            PHI_REF,
            STRAT_VEC,
            CONTEXT_NO,
            TOPO_SORT,
            PREV_PHASE,
            POST_PHASE,
            PHI_SAMP_DICT,
            CONT_TYPE,
            PROGRESS_IO,
        )

    return CONTEXT_NO, ACCEPT, PHI_ACCEPT, PHI_REF, A, P, ALL_SAMPS_CONT, ALL_SAMPS_PHI
