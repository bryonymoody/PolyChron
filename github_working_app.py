#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 17:43:25 2021

@author: bryony
"""


 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 12:35:28 2020
@author: bryony
"""
import tkinter as tk
from tkinter import ttk
#import tabulate
import copy
#from tabulate import tabulate
import re
import ast
import time
import matplotlib as plt
#import threading
from PIL import Image, ImageTk, ImageChops
from networkx.drawing.nx_pydot import read_dot, write_dot
import networkx as nx
import pydot
import numpy as np
import pandas as pd
from tkinter.filedialog import askopenfile
from graphviz import render
import automated_mcmc_ordering_coupling_copy as mcmc
from ttkthemes import ThemedStyle
from tkinter.font import BOLD
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import pickle
from html2text import html2text 
from tkinter import simpledialog
#from ttkbootstrap import Style
#from networkx.readwrite import json_graph

old_stdout = sys.stdout
FILENAME = "save.pickle"


class StdoutRedirector(object):

    def __init__(self, text_area):
        self.text_area = text_area

    def write(self, str):
        self.text_area.update_idletasks()
        self.text_area.insert(tk.END, str)
        self.text_area.see(tk.END)

phase_true = 0
load_check = 'not_loaded'
mcmc_check = 'mcmc_notloaded'
CALIBRATION = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)    
def trim(im_trim):
    # t0 = time.time()
    """Trims images down"""
    bg_trim = Image.new(im_trim.mode, im_trim.size)
    diff = ImageChops.difference(im_trim, bg_trim)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()    
    return im_trim.crop(bbox)

def polygonfunc(i):
    x = re.findall(r'points="(.*?)"', i)[0].replace(' ', ',')
    a = x.split(",")
    if -1*float(a[7]) == -1*float(a[3]):
        coords_converted = [float(a[2]), float(a[6]), -1*float(a[5]), -1*float(a[1])]
    else:
        coords_converted = [float(a[2]), float(a[6]), -1*float(a[7]), -1*float(a[3])]
    return(coords_converted)

def ellipsefunc(i):
    x = re.findall(r'cx=(.*?)/>', i)[0].replace(' ', ',')
    x = x.replace('cy=', '').replace('rx=', '').replace('ry=','').replace('"', '')
    a = x.split(",")
    coords_converted = [float(a[0]) - float(a[2]), float(a[0]) + float(a[2]), -1*float(a[1]) - float(a[3]), -1*float(a[1]) + float(a[3])]
    return(coords_converted)


def node_coords_fromjson(graph):
    """Gets coordinates of each node"""
    graphs = nx.nx_pydot.to_pydot(graph)    
    svg_string = str(graphs.create_svg())
    scale_info = re.search('points=(.*?)/>', svg_string).group(1).replace(' ', ',')
    scale_info = scale_info.split(",")
    scale = [float(scale_info[4]), -1*float(scale_info[3])]
    coords_x = re.findall(r'id="node(.*?)</text>', svg_string)  
    coords_temp = [polygonfunc(i) if "points" in i else ellipsefunc(i) for i in coords_x]
    node_test = re.findall(r'node">\\n<title>(.*?)</title>', svg_string)
    node_list = [i.replace('&#45;', '-') for i in node_test]
                        
    new_pos = dict(zip(node_list, coords_temp))
    df = pd.DataFrame.from_dict(new_pos, orient='index', columns=['x_lower', 'x_upper', 'y_lower', 'y_upper'])
    return df, scale

def all_node_info(node_list, x_image, node_info):
  #  t0 = time.time()
    """obtains node attributes from original dot file"""
    for i in node_list:
        for j in x_image:
            b_string = re.search("\"(.*)\" ", j)
            if b_string is not None:
                if i == b_string.group(1):
                    if i in j and '->' not in j:
                        tset = j[(j.index('[')+1):(len(j)-1)]
                        atr_new = tset.replace('] [', '\',\'')
                        atr_new = atr_new.replace('=', '\':\' ')
                        atr_new = atr_new.replace('\' \"', '\"')
                        atr_new = atr_new.replace('\"\'', '\"')
                        atr_new = atr_new.replace('\' ', '\'')
                        atr_newer = str('{\''+atr_new+'}')
                        dicc = ast.literal_eval(atr_newer)
                        node_info.append(dicc)
    return node_info

def phase_length_finder(con_1, con_2, ALL_SAMPS_CONT, CONTEXT_NO, resultsdict):
    phase_lengths = []
    x_3 = resultsdict[con_1]
    x_4 = resultsdict[con_2]
 #   sampl_list = [len(i) for i in ALL_SAMPS_CONT]
    for i in range(len(x_3)):
       phase_lengths.append(np.abs(x_3[i] - x_4[i]))
    un_phase_lens = []
    for i in range(len(phase_lengths)-1):
        if phase_lengths[i] != phase_lengths[i+1]:
            un_phase_lens.append(phase_lengths[i])
    return phase_lengths
        
def imagefunc(dotfile):
 #   t0 = time.time()
    """Sets note attributes to a dot string"""
    file = read_dot(dotfile)
 ####code to get colours####
    f_string = open(str(dotfile), "r")
    dotstr = f_string.read()
    dotstr = dotstr.replace(";<", "@<") 
    dotstr = dotstr.replace("14.0", "50.0")
#change any ';>' to '@>' then back again after
    x_image = dotstr.rsplit(";")
    for i in enumerate(x_image):
        x_image[i[0]] = x_image[i[0]].replace("@<", ";<")
    node_list = list(file.nodes)
    node_info_init = list()
    node_info = all_node_info(node_list, x_image, node_info_init)
    for k in enumerate(node_list):
        node_info[k[0]].update({"Date":"None", "Find_Type":"None", "Phase":node_info[k[0]]['fillcolor'], 'color' : 'black'})
    individ_attrs = zip(node_list, node_info)
    attrs = dict(individ_attrs)#add the dictionary of attributed to a node
    nx.set_node_attributes(file, attrs)
    return file
def phase_relabel(graph):
    label_dict = {}
    for i in graph.nodes():
        if str(i)[0] == 'a':
            label_str = '<&alpha;<SUB>' + str(i[2:]) + '</SUB>>'
            label_dict[i] = label_str
        elif str(i)[0] == 'b':
            label_str = '<&beta;<SUB>' + str(i[2:]) + '</SUB>>'
            label_dict[i] = label_str
        else: 
            label_str = str(i)
            label_dict[i] = label_str
    nx.set_node_attributes(graph, label_dict, 'label')
    return graph

def chrono_edge_remov(file_graph):
    xs, ys = [], []
    for x, y in list(file_graph.edges):
        xs.append(x)
        ys.append(y)
    graph_data = phase_info_func(file_graph)
    phase_list = list(graph_data[1][2])
    phase_dic = graph_data[3]
    if len(phase_list) != 1:
        if len(graph_data[1][3]) == 0:
            file_graph.add_edge(phase_dic[phase_list[0]][0], phase_dic[phase_list[1]][0])
            graph_data = phase_info_func(file_graph)
        x_l, y_l = graph_data[2][0], graph_data[2][1]        
        evenlist, oddlist, elist, olist = [], [], [], []
        for i in range(len(x_l)): 
          if (i % 2 == 0): 
             evenlist.append(x_l[i])
             elist.append(y_l[i]) 
          else: 
             oddlist.append(x_l[i])
             olist.append(y_l[i])
             
        for j in range(len(evenlist)):     
             file_graph.remove_edge(oddlist[j], evenlist[j])
             
        for node in phase_list:
            alp_beta_node_add(node, file_graph)
        file_graph = phase_relabel(file_graph)
        
        for i, j in enumerate(elist):
            file_graph.add_edge("b_" + str(j), evenlist[i], arrows=False)    
        for i, j in enumerate(olist):
            file_graph.add_edge(oddlist[i], "a_" + str(j.replace("_below", "")), arrows=False)
    elif len(phase_list) == 1:
        evenlist = []
        oddlist = []
        for nd in graph_data[1][1]:
            if len(list(file_graph.predecessors(nd))) == 0:
                evenlist.append(nd)
            if len(list(file_graph.edges(nd))) == 0:
                oddlist.append(nd)
        for node in list(phase_list):
            alp_beta_node_add(node, file_graph)
        for node in list(phase_list):
            alp_beta_node_add(node, file_graph)
        phase_lab = phase_list[0]   
        for z in evenlist:
            file_graph.add_edge("b_" + str(phase_lab), z, arrows=False)
                
        for m in oddlist:
            file_graph.add_edge(m, "a_" + str(phase_lab), arrows=False)
    return graph_data, [xs, ys], phase_list


def phase_labels(phi_ref, POST_PHASE, phi_accept, all_samps_phi):
    "provides phase limits for a phase"""
    labels = ['a_' + str(phi_ref[0])]
    i = 0
    results_dict = {labels[0]: phi_accept[i]}
    all_results_dict = {labels[0]: all_samps_phi[i]}
    for a_val in enumerate(POST_PHASE):
        i = i + 1
        if a_val[1] == "abuting":
            labels.append('b_' + str(phi_ref[a_val[0]]) + ' = a_' + str(phi_ref[a_val[0]+1]))
            results_dict['a_' + str(phi_ref[a_val[0]+1])  + ' = b_' + str(phi_ref[a_val[0]])] =  phi_accept[i]
            all_results_dict['a_' + str(phi_ref[a_val[0]+1])  + ' = b_' + str(phi_ref[a_val[0]])] =  all_samps_phi[i]            
           # results_dict['a_' + str(phi_ref[a_val[0]+1])] = phi_accept[i]
        elif a_val[1] == 'end':
            labels.append('b_' + str(phi_ref[-1]))
            results_dict['b_' + str(phi_ref[a_val[0]])] =  phi_accept[i]
            all_results_dict['b_' + str(phi_ref[a_val[0]])] =  all_samps_phi[i]
        elif a_val == 'gap':
            labels.append('b_' + str(phi_ref[a_val[0]]))
            labels.append('a_' + str(phi_ref[a_val[0]+1]))
            results_dict['b_' + str(phi_ref[a_val[0]])] = phi_accept[i]
            all_results_dict['b_' + str(phi_ref[a_val[0]])] = all_samps_phi[i]
            i = i + 1
            results_dict['a_' + str(phi_ref[a_val[0]+1])] = phi_accept[i]
            all_results_dict['a_' + str(phi_ref[a_val[0]+1])] = all_samps_phi[i]
        else:
            labels.append('a_' + str(phi_ref[a_val[0]+1]))
            labels.append('b_' + str(phi_ref[a_val[0]]))
            results_dict['a_' + str(phi_ref[a_val[0]+1])] = phi_accept[i]
            all_results_dict['a_' + str(phi_ref[a_val[0]+1])] = all_samps_phi[i]
            i = i + 1
            results_dict['b_' + str(phi_ref[a_val[0]])] = phi_accept[i]
            all_results_dict['b_' + str(phi_ref[a_val[0]])] = all_samps_phi[i]
    return labels, results_dict, all_results_dict


def chrono_edge_add(file_graph, graph_data, xs_ys, phasedict, phase_trck):
    xs = xs_ys[0]
    ys = xs_ys[1]
    phase_nodes = []
    phase_norm, node_list = graph_data[1][0], graph_data[1][1]
    all_node_phase = dict(zip(node_list, phase_norm))
    label_dict = {}     
    for i in node_list:
        if (i in xs) == False:
            if (i in ys) == False:
                file_graph.add_edge("b_" + str(all_node_phase[i]), i, arrows=False)
                file_graph.add_edge(i, "a_" + str(all_node_phase[i]), arrows=False)
            else:
                file_graph.add_edge(i, "a_" + str(all_node_phase[i]), arrows=False)
        elif (i in xs) == True:
            if (i in ys) == False:
                file_graph.add_edge("b_" + str(all_node_phase[i]), i, arrows=False)
    if phasedict != None:
        p_list = list(set(phase_trck))
        null_phases = []
        phase_nodes.append('a_'+ str(p_list[0][0]))
        up_phase = [i[0] for i in p_list]
        low_phase = [i[1] for i in p_list]
        act_phases = set(up_phase + low_phase)
        del_phase = act_phases - set(graph_data[1][2])
        del_phase_dict_1 = {}
        for j in del_phase:
            del_phase_dict = {}
            rels_list = [i for i in phasedict.keys() if j in i]
            for rels in rels_list:
                if rels[0] == j:
                    del_phase_dict['lower'] = rels[1]
                if rels[1] == j:
                    del_phase_dict['upper'] = rels[0]
            del_phase_dict_1[j] = del_phase_dict
          
        for j in del_phase:
            rels_list = [i for i in phasedict.keys() if j in i]
            for rels in rels_list:
                if rels[0] == j:
                    if (rels[1] in del_phase) == True:
                        print(j, rels[1])
                        del_phase_dict_1[j]['lower'] = del_phase_dict_1[rels[1]]['lower']
                if rels[1] == j:
                    if (rels[0] in del_phase) == True:
                        del_phase_dict_1[j]['upper'] = del_phase_dict_1[rels[0]]['upper']
        new_phase_rels = set([[del_phase_dict_1[l]['upper'], del_phase_dict_1[l]['lower']] for l in del_phase_dict_1.keys()])
        print(new_phase_rels)
 #       print(graph_data[1][2])
#        print(act_phases)
        for s in graph_data[1][2]:
                file_graph.add_node("a_" + str(s), shape="diamond", fontsize="20.0",
                                   fontname="Ubuntu", penwidth="1.0")
                file_graph.add_node("b_" + str(s), shape="diamond", fontsize="20.0",
                                   fontname="Ubuntu", penwidth="1.0")
                file_graph.add_edge("b_" + str(s), "a_" + str(s))
                phase_relabel(file_graph)
#        for p in p_list:
#            if (p[0] in graph_data[1][2]) == False:
#                file_graph.add_node("a_" + str(p[0]), shape="diamond", fontsize="20.0",
#                                   fontname="Ubuntu", penwidth="1.0")
#                file_graph.add_node("b_" + str(p[0]), shape="diamond", fontsize="20.0",
#                                   fontname="Ubuntu", penwidth="1.0")
#                file_graph.add_edge("b_" + str(p[0]), "a_" + str(p[0]))
#                phase_relabel(file_graph)
#            if (p[1] in graph_data[1][2]) == False:
#                file_graph.add_node("a_" + str(p[1]), shape="diamond", fontsize="20.0",
#                                   fontname="Ubuntu", penwidth="1.0")
#                file_graph.add_node("b_" + str(p[1]), shape="diamond", fontsize="20.0",
#                                   fontname="Ubuntu", penwidth="1.0")
#                file_graph.add_edge("b_" + str(p[1]), "a_" + str(p[1]))
#                phase_relabel(file_graph)
                
        for p in p_list:
            relation = phasedict[p]
            if relation == 'gap':
                if (p[0] in graph_data[1][2]) == False:
                 #   file_graph = nx.contracted_nodes(file_graph, "b_" + str(p[1]), "a_" + str(p[0]))
                    phasedict.pop[p]
                    null_phases.append(p)
                elif (p[1] in graph_data[1][2]) == False:
                  #  file_graph = nx.contracted_nodes(file_graph, "a_" + str(p[0]), "b_" + str(p[1]))
                    null_phases.append(p)
                else:
                    file_graph.add_edge("a_" + str(p[0]), "b_" + str(p[1]))
            if relation == 'overlap':
                if (p[0] in graph_data[1][2]) == False:
                   # file_graph = nx.contracted_nodes(file_graph, "b_" + str(p[1]), "a_" + str(p[0]))
                    null_phases.append(p)
                elif (p[1] in graph_data[1][2]) == False:
                    #file_graph = nx.contracted_nodes(file_graph, "a_" + str(p[0]), "b_" + str(p[1]))
                    null_phases.append(p)
                else:
                    file_graph.add_edge("b_" + str(p[1]), "a_" + str(p[0]))
            if relation == "abuting":
                
                if (p[0] in graph_data[1][2]) == False:
                  #  file_graph = nx.contracted_nodes(file_graph, "b_" + str(p[1]), "a_" + str(p[0]))
                    null_phases.append(p)
                elif (p[1] in graph_data[1][2]) == False:
                   # file_graph = nx.contracted_nodes(file_graph, "a_" + str(p[0]), "b_" + str(p[1]))
                    null_phases.append(p)
                else:
                    file_graph = nx.contracted_nodes(file_graph, "a_" + str(p[0]), "b_" + str(p[1]))
                    x_nod = list(file_graph)
                    newnode = str("a_" + str(p[0]) + " = " +"b_" + str(p[1]))
                    label_str = '<&alpha;<SUB>' + str(p[0]) + '</SUB> = &beta;<SUB>' + str(p[1]) + '</SUB>>'
                    label_dict[newnode] =  label_str
                    phase_nodes.append("a_" + str(p[0]) + " = " +"b_" + str(p[1]))
                    y_nod = [newnode if i=="a_" + str(p[0]) else i for i in x_nod]
                    mapping = dict(zip(x_nod, y_nod))
                    file_graph = nx.relabel_nodes(file_graph, mapping)
        phase_nodes.append('b_' + str(p_list[len(p_list)-1][0]))        
    graph = nx.DiGraph()
    if len(phase_trck) != 0:
        graph.add_edges_from(phase_trck)
        phi_ref = list(reversed(list(nx.topological_sort(graph))))
        graph_temp = nx.transitive_reduction(graph)    
        a = set(graph.edges())
        b = set(graph_temp.edges())
        if len(list(a-b)) != 0:
            rem = list(a-b)[0]
            file_graph.remove_edge(rem[0], rem[1])     
    nx.set_node_attributes(file_graph, label_dict, 'label')
    return(file_graph, phi_ref, null_phases)



def imgrender(file):
    """renders png from dotfile"""
    write_dot(file, 'fi_new')
    render('dot', 'png', 'fi_new')    
    inp = Image.open("fi_new.png")
    inp = trim(inp)
    inp.save("testdag.png")
    outp = Image.open("testdag.png")
    return outp



def imgrender2(load_check):
    """renders png from dotfile"""
    if load_check == 'loaded':
        render('dot', 'png', 'fi_new_chrono')
        inp = Image.open("fi_new_chrono.png")
        inp = trim(inp)
        inp.save("testdag_chrono.png")
        outp = Image.open("testdag_chrono.png")
    else: 
        outp = 'No_image'
    return outp


def edge_of_phase(test1, pset, node_list, node_info):
#    t0 = time.time()
    """find nodes on edge of each phase"""
    x_l = []
    y_l = []
    mydict = {}
    phase_tracker = []
    if FILE_INPUT != None:
        for i in enumerate(pset):
            temp_nodes_list = []
            for j in enumerate(node_list):
                if node_info[j[0]]["fillcolor"] == pset[i[0]]:
                    temp_nodes_list.append(node_list[j[0]])
                    p_phase = str(pset[i[0]][pset[i[0]].rfind("/")+1:len(pset[i[0]])])
                    node_info[j[0]].update({"Phase":p_phase})
                mydict[str(pset[i[0]][pset[i[0]].rfind("/")+1:len(pset[i[0]])])] = temp_nodes_list
    else:
        for i in enumerate(pset):
            temp_nodes_list = []
            for j in enumerate(node_list):
                if node_info[j[0]]["Phase"] == pset[i[0]]:
                    temp_nodes_list.append(node_list[j[0]])
                mydict[pset[i[0]]] = temp_nodes_list
    for i in enumerate(test1):        
        for key in mydict:
            if test1[i[0]][1] in mydict[key] and test1[i[0]][0] not in mydict[key]:
                x_l.append(test1[i[0]][1])
                y_l.append(key)
                phase_lst = [list(mydict.values()).index(j) for j in list(mydict.values()) if
                             test1[i[0]][0] in j]
                key_1 = (list(mydict.keys())[phase_lst[0]]) #trying to find phase of other value
                x_l.append(test1[i[0]][0])
                y_l.append(str(key_1 + "_below"))
                phase_tracker.append((key_1, key))
    return x_l, y_l, mydict.keys(), phase_tracker, mydict



def edge_of_phase_new(test1, pset, node_list, node_info):
#    t0 = time.time()
    """find nodes on edge of each phase"""
    x_l = []
    y_l = []
    mydict = {}
    phase_tracker = []
    for i in enumerate(pset):
        temp_nodes_list = []
        for j in enumerate(node_list):
            if node_info[j[0]]["fillcolor"] == pset[i[0]]:
                temp_nodes_list.append(node_list[j[0]])
                p_phase = "Phase " + str(pset[i[0]][pset[i[0]].rfind("/")+1:len(pset[i[0]])])
                node_info[j[0]].update({"Phase":p_phase})
                mydict[str(pset[i[0]][pset[i[0]].rfind("/")+1:len(pset[i[0]])])] = temp_nodes_list
    for i in enumerate(test1):
        for key in mydict:
            if test1[i[0]][1] in mydict[key] and test1[i[0]][0] not in mydict[key]:
                x_l.append(test1[i[0]][1])
                y_l.append(key)
                phase_lst = [list(mydict.values()).index(j) for j in list(mydict.values()) if
                             test1[i[0]][0] in j]
                key_1 = (list(mydict.keys())[phase_lst[0]]) #trying to find phase of other value
                x_l.append(test1[i[0]][0])
                y_l.append(str(key_1 + "_below"))
                phase_tracker.append((key_1, key))
    return x_l, y_l, mydict.keys(), phase_tracker


def phase_info_func(file_graph):
   # t0 = time.time()
    """returns a dictionary of phases and nodes in each phase"""
    
    res = []
    node_list = list(file_graph.nodes)
    nd = dict(file_graph.nodes(data = True))   
    node_info = [nd[i] for i in node_list]    
    if FILE_INPUT != None:
        phase = nx.get_node_attributes(file_graph, "fillcolor")
        phase_norm = [phase[ph][phase[ph].rfind("/")+1:len(phase[ph])] for ph in phase]
# ####code to get colours####
        f_str = open(str(FILE_INPUT), "r")
        dotstr = f_str.read()
        dotstr = dotstr.replace(";<", "@<")
        dotstr = dotstr.replace("14.0", "50.0")
##change any ';>' to '@>' then back again after
        x_phaseinf = dotstr.rsplit(";")
        for i in enumerate(x_phaseinf):
            x_phaseinf[i[0]] = x_phaseinf[i[0]].replace("@<", ";<")
        for key in phase.keys():
            res.append(phase[key])
    else:        
        phase1 =  nx.get_node_attributes(file_graph, "Phase")
        for key in phase1.keys():
            res.append(phase1[key])
        phase_norm = res           
    x_l, y_l, phase_list, phase_trck, phase_dic = edge_of_phase(list(nx.line_graph(file_graph)), list(set(res)), node_list, node_info)
    reversed_dict = {}
    if len(phase_list) > 1:
        testdic = dict(zip(x_l, y_l))
        for key, value in testdic.items():
            reversed_dict.setdefault(value, [])
            reversed_dict[value].append(key)       
    return reversed_dict, [phase_norm, node_list, phase_list, phase_trck], [x_l, y_l], phase_dic

def alp_beta_node_add(x, graph):
    graph.add_node("a_" + str(x), shape="diamond", fontsize="20.0",
                                   fontname="Ubuntu", penwidth="1.0")
    graph.add_node("b_" + str(x), shape="diamond", fontsize="20.0",
                                   fontname="Ubuntu", penwidth="1.0")


def rank_func(tes, file_content):
  #  t0 = time.time()
    """adds strings into dot string to make nodes of the same phase the same rank"""
    rank_same = []
    for key in tes.keys():
        x_rank = tes[key]
        y_1 = str(x_rank)
        y_2 = y_1.replace("[", "")
        y_3 = y_2.replace("]", "")
        y_4 = y_3.replace("'", "")
        y_5 = y_4.replace(",", ";")
        x_2 = "{rank = same; "+y_5+";}\n"
        rank_same.append(x_2)
    rank_string = ''.join(rank_same)[:-1]
    new_string = file_content[:-2] + rank_string + file_content[-2]
    return new_string

def imgrender_phase(file):
  #  t0 = time.time()
    """Renders image from dot file with all nodes of the same phase collected together"""
    write_dot(file, 'fi_new.txt')
    my_file = open("fi_new.txt")
    file_content = my_file.read()
    new_string = rank_func(phase_info_func(file)[0], file_content)
    textfile = open('fi_new.txt', 'w')
    textfile.write(new_string)
    textfile.close()
    (graph,) = pydot.graph_from_dot_file('fi_new.txt')
    graph.write_png('test.png')
    inp = Image.open("test.png")
    inp = trim(inp)  
            # Call the real .tkraise
    inp.save("testdag.png")
    outp = Image.open("testdag.png")
    return outp



class popupWindow(object):
    def __init__(self,master):
        self.top=tk.Toplevel(master)
        self.l=tk.Label(self.top,text="Context Number")
        self.l.pack()
        self.e=tk.Entry(self.top)
        self.e.pack()
        self.b=tk.Button(self.top,text='Ok',command=self.cleanup)
        self.b.pack()
    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()
        
class popupWindow2(object):
    def __init__(self,master, graph, canvas):
        top=tk.Toplevel(master)
        top.geometry("300x300")
        self.graph = graph
        self.metacanvas = canvas
        self.canvas2 = tk.Canvas(top, bg = 'white')
        self.canvas2.place(relx=0, rely=0, relwidth=1, relheight=1)
        #canvas to hold the metadata

#        #making node add section
#        #entry box for adding metadata
        self.entry3 = ttk.Entry(self.canvas2)
        self.button3 = ttk.Button(top, text='Add Metadata to node', command=lambda:self.testcom())#need to add command
        self.label3 = tk.Label(self.canvas2, text='Node', bg = 'white')
        self.canvas2.create_window(40, 60, window=self.entry3, width=50)
        self.canvas2.create_window(40, 35, window=self.label3)
        self.dict = {'Find_Type': ['Find1', 'Find2', 'Find3'],
                     'Date': ['None', 'Input date'],
                     'Phase': ['None', 'Input phase']}
#               
        self.variable_a = tk.StringVar(top)
        self.variable_b = tk.StringVar(top)
        self.variable_c = tk.StringVar(top)
        self.variable_d = tk.StringVar(top)
        self.variable_a.trace('w', self.update_options)
        self.variable_b.trace('w', self.testdate_input)
        self.variable_c.trace('w', self.update_options)
        self.variable_d.trace('w', self.update_options)
        self.optionmenu_a = ttk.OptionMenu(top, self.variable_a, self.dict.keys()[0], *self.dict.keys())
        self.optionmenu_b = ttk.OptionMenu(top, self.variable_b,'None',  'None')
        self.variable_a.set('Date')
        self.optionmenu_a.place(relx=0.3, rely=0.15)
        self.optionmenu_b.place(relx=0.6, rely=0.15)
        self.button3.place(relx = 0.1, rely = 0.7)
        
    def testdate_input(self, *args):
        if self.variable_b.get() == "Input date":          
            self.label4 = tk.Label(self.canvas2, text='Radiocarbon Date', bg = 'white')
            self.entry4 = tk.Entry(self.canvas2)
            self.canvas2.create_window(90, 130, window=self.entry4, width=50)
            self.canvas2.create_window(90, 90, window=self.label4)
            self.label5 = ttk.Label(self.canvas2, text='Error')
            self.entry5 = tk.Entry(self.canvas2)
            self.canvas2.create_window(200, 130, window=self.entry5, width=50)
            self.canvas2.create_window(200, 90, window=self.label5)
        if self.variable_b.get() == "Input phase":          
            self.label6 = ttk.Label(self.canvas2, text='Phase')
            self.entry6 = tk.Entry(self.canvas2)
            self.canvas2.create_window(90, 130, window=self.entry6, width=50)
            self.canvas2.create_window(90, 90, window=self.label6)
     
        
    def testcom(self):
  #      t0 = time.time()
        """metadata menu 2 update"""
        if self.variable_a.get() == "Phase":  
            if self.variable_b.get() == "Input phase":
                self.graph.nodes()[str(self.entry3.get())].update({"Phase":self.entry6.get()})
                self.label6.destroy()
                self.entry6.destroy()
            else:
                self.graph.nodes()[str(self.entry3.get())].update({"Phase":self.variable_b.get()})
        elif self.variable_a.get() == "Date":
            if self.variable_b.get() == "Input date":
                self.graph.nodes()[str(self.entry3.get())].update({"Date": [self.entry4.get(), self.entry5.get()]})
                self.label4.destroy()
                self.entry4.destroy()
                self.label5.destroy()
                self.entry5.destroy()  
            else:
                self.graph.nodes()[str(self.entry3.get())].update({"Date":self.variable_b.get()})
        elif self.variable_a.get() == "Find_Type":
            self.graph.nodes()[str(self.entry3.get())].update({"Find_Type":self.variable_b.get()})
        self.metatext = tk.Text(self.metacanvas, width=120, height=40)
        self.metacanvas.create_window((0, 0), window=self.metatext, anchor='nw')
        self.meta1 = pd.DataFrame.from_dict(self.graph.nodes()[str(self.entry3.get())],
                                            orient='index')
        self.meta2 = self.meta1.loc["Date":"Phase",]
        self.meta2.columns = ["Data"]
        if self.meta2.loc["Date"][0] != "None":
           self.meta2.loc["Date"][0] = str(self.meta2.loc["Date"][0][0]) + " +- " + str(self.meta2.loc["Date"][0][1]) + " Carbon BP"
        self.metatext.insert('end', 'Metadata of node ' +
                             str(self.entry3.get()) + ':\n')
        cols = list(self.meta2.columns)
        tree = ttk.Treeview(self.metacanvas)
        tree["columns"] = cols
        tree.place(relx=0, rely=0.25)
        tree.column("Data", anchor="w")
        tree.heading("Data", text="Data", anchor='w')        
        for index, row in self.meta2.iterrows():
            tree.insert("",0,text=index,values=list(row))
        self.metatext.configure(state='disabled')

    def update_options(self, *args):
  #      t0 = time.time()
        """updates metadata drop down menu 1"""
        meta_data = self.dict[self.variable_a.get()]
        self.variable_b.set(meta_data[0])
        menu = self.optionmenu_b['menu']
        menu.delete(0, 'end')
        for meta in meta_data:
            menu.add_command(label=meta,
                             command=lambda nation=meta: self.variable_b.set(nation))  

                
    def cleanup(self):
        self.value=self.canvas2.get()
        self.top.destroy()
        
class popupWindow3_backup(object):
    def __init__(self, master, controller):
        self.graphcopy = None        
        
class popupWindow3(object):
    def __init__(self, master, controller, graph, canvas, phase_rels, dropdown_ns = [], dropdown_intru = [], resid_list = [], intru_list = []):
        self.littlecanvas2 = canvas
        self.top=tk.Toplevel(master)
        self.top.geometry("1000x400")
        self.graph = graph
        self.graphcopy = copy.deepcopy(self.graph)
        phasedict = nx.get_node_attributes(self.graphcopy, 'Phase')
        datadict = nx.get_node_attributes(self.graphcopy, 'Date')
        nodes = self.graphcopy.nodes()
        self.node_del_tracker = []
        for i in nodes:
            if phasedict[i] == None:
                self.node_del_tracker.append(i)
            elif datadict[i] == [None, None]:
                self.node_del_tracker.append(i)
        for j in self.node_del_tracker:
            self.graphcopy.remove_node(j)
        self.context_no = [x for x in list(self.graph.nodes()) if x not in self.node_del_tracker] 
        self.CONT_TYPE = ['normal' for i in self.context_no]
        self.variable_1 = tk.StringVar(self.top)
        self.variable_2 = tk.StringVar(self.top)
        self.phases = phase_rels        
        self.menu_list1 = []
        self.menudict = {}
        self.prev_dict = {}
        self.post_dict = {}
        self.menu_list2 = ["abuting", "gap", "overlap"]            
        self.resid_list3 = resid_list
        self.intru_list3 = intru_list
        self.dropdown_ns = dropdown_ns
        self.dropdown_intru = dropdown_intru
    #   self.dropdown_ns[self.resid_list3[i].get()] 
        for i in range(len(self.resid_list3)):
            if self.dropdown_ns[self.resid_list3[i]].get() == "Treat as TPQ":
                self.CONT_TYPE[np.where(np.array(self.context_no) == self.resid_list3[i])[0][0]] = "residual"
            elif self.dropdown_ns[self.resid_list3[i]].get() == "Exclude from modelling":
                print('del')
                self.graphcopy.remove_node(self.resid_list3[i])
                self.CONT_TYPE.pop(np.where(np.array(self.context_no) == self.resid_list3[i])[0][0])
                self.context_no.remove(self.resid_list3[i])
        for j in range(len(self.intru_list3)):
            if self.dropdown_intru[self.intru_list3[j]].get() == "Treat as TAQ":
                self.CONT_TYPE[np.where(np.array(self.context_no) == self.intru_list3[j])[0][0]] = "intrusive"
            elif self.dropdown_intru[self.intru_list3[j]].get() == "Exclude from modelling":
                print('del1')
                self.graphcopy.remove_node(self.intru_list3[j])
                self.CONT_TYPE.pop(np.where(np.array(self.context_no) == self.intru_list3[j])[0][0])
                self.context_no.remove(self.intru_list3[j])
        self.button_b = ttk.Button(self.top, text='Render Chronological graph', command=lambda:self.full_chronograph_func())         
        

        
        self.step_1 = chrono_edge_remov(self.graphcopy)
        self.button_b.place(relx=0.4, rely=0.55)
        if self.phases != None: 
            for i in self.phases:
                self.menu_list1.append("Relationship between start of phase " + str(i[0]) + " and end of phase " + str(i[1]))    
            self.button_a = ttk.Button(self.top, text='Add Phase Relationship', command=lambda:self.phase_rel_func())
            self.optionmenu_b = ttk.OptionMenu(self.top, self.variable_2, self.menu_list2[0], *self.menu_list2)
            self.optionmenu_a = ttk.OptionMenu(self.top, self.variable_1, self.menu_list1[0], *self.menu_list1)
            self.optionmenu_a.place(relx=0.1, rely=0.15)
            self.optionmenu_b.place(relx=0.6, rely=0.15)
            self.button_a.place(relx=0.7, rely=0.15)
        else: 
            self.menudict = None
        master.wait_window(self.top)
        
        
    def phase_rel_func(self):
        n = re.search('start of phase (.+?) and end', self.variable_1.get()).group(1)
        m = re.search('and end of phase (.+?)', self.variable_1.get()).group(1)
        
        self.menudict[(n, m)] = self.variable_2.get()
        self.prev_dict[n] = self.variable_2.get()
        self.post_dict[m] = self.variable_2.get()
        self.menu_list1.remove(self.variable_1.get())
        self.optionmenu_a['menu'].delete(self.variable_1.get())
        if len(self.menu_list1) > 0:
            self.variable_1.set(self.menu_list1[0])
        else:
            self.variable_1.set("No Phases Left")
        
    def full_chronograph_func(self):
        self.prev_phase = ["start"]
        self.post_phase = []
        phase_list = self.step_1[2]
        if len(self.step_1[0][1][3]) != 0:
            self.graphcopy, self.phi_ref, self.null_phases = chrono_edge_add(self.graphcopy, self.step_1[0], self.step_1[1], self.menudict, self.phases)
            self.post_phase.append(self.post_dict[self.phi_ref[0]])
            for i in range(1,len(self.phi_ref)-1):
                    self.prev_phase.append(self.prev_dict[self.phi_ref[i]])
                    self.post_phase.append(self.post_dict[self.phi_ref[i]])
            self.prev_phase.append(self.prev_dict[self.phi_ref[len(self.phi_ref)-1]])
        else:
            self.phi_ref = list(self.step_1[0][1][2])
        self.post_phase.append("end")
        del_phases =  [i for i in self.phi_ref if (i in phase_list) == False]
        ref_list = []
        for i in del_phases:
            ref = np.where(np.array(self.phi_ref) == i)[0][0]
            ref_list.append(ref)
        for index in sorted(ref_list, reverse=True):
            del self.phi_ref[index]
#change to new phase rels
        for i in ref_list:
            self.prev_phase[i] = 'gap' 
            self.post_phase[i] = 'gap'
        for index in sorted(ref_list, reverse=True):
            del self.prev_phase[index+1]
        for index in sorted(ref_list, reverse=True):
            del self.post_phase[index-1]

        write_dot(self.graphcopy, 'fi_new_chrono')
        self.top.destroy()

class MainFrame(tk.Tk):
    """ Main frame for tkinter app"""
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
        
        
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        frame.config()
        
    def get_page(self, page_class):
            return self.frames[page_class] 

class popupWindow4(object):
    def __init__(self, master, controller, resid_list, intru_list, node_track, graph):
        self.top=tk.Toplevel(controller)
        self.top.geometry("1000x400")
        self.node_del_tracker = node_track
        self.controller = controller
        self.resid_list = resid_list
        self.intru_list = intru_list
  #      self.button2 = tk.Button (self.top, text='Exit Application',command=ExitApplication,bg='brown',fg='white')
        self.button = ttk.Button(self.top, text='Go back', command=lambda:self.top.destroy())
        self.button.grid(column = 30, row = 4)
        self.button = ttk.Button(self.top, text='Proceed to render chronological DAG', command=lambda:self.move_to_graph())
        self.button.grid(column = 30, row = 6)
        self.test(resid_list, intru_list)
  #      self.graphcopy = graph
       
        controller.wait_window(self.top) 

    def move_to_graph(self):
        startpage = self.controller.get_page('StartPage')
     #   self.chronograph = startpage.chrono_dag
        self.controller.show_frame("StartPage")  
      #  startpage.popup3.graphcopy = self.chronograph
        self.popup3 = popupWindow3(startpage, startpage.controller, startpage.graph, startpage.littlecanvas2, startpage.phase_rels, self.dropdown_ns, self.dropdown_intru, self.resid_list, self.intru_list) 
        self.CONT_TYPE = self.popup3.CONT_TYPE
        self.prev_phase = self.popup3.prev_phase
        self.post_phase = self.popup3.post_phase
        self.phi_ref = self.popup3.phi_ref
        #DELETE ALPHA AND BETA NODE FOR EMPTY PHASES HERE CHECK HOW I DID IT BEFORE
        self.context_no = self.popup3.context_no
        self.graphcopy = self.popup3.graphcopy
        self.top.destroy()
        
    
    def test(self,  resid_list, intru_list):
        self.dropdowns = {}
        self.dropdown_ns = {}
        self.dropdown_intru = {}
        self.nodetype2 = {}
            
        # Label
#        x = ['123', '134a', '1543gfs', '123b', '134b', '1543gfsc', '123a', '134f', '1543g', '123qqq', '134q', '1543dfs']
        for i, j in enumerate(resid_list):
            ttk.Label(self.top, text = str(j), 
                    font = ("Times New Roman", 10)).grid(column = 0, 
                    row = i, padx = 30, pady = 25)
              
            self.dropdown_ns[j] = tk.StringVar()
            self.dropdowns[j] =  ttk.Combobox(self.top, width = 27, 
                                        textvariable = self.dropdown_ns[j], state = "readonly")
              
            # Adding combobox drop down list
            self.dropdowns[j]['values'] = ('Exclude from modelling',
                                      'Treat as TPQ')
       #     dropdowns[j].current(0) 
            self.dropdowns[j]["background"] = '#ff0000'
            self.dropdowns[j].grid(column = 1, row = i)
        for k, l in enumerate(intru_list):         
            ttk.Label(self.top, text = str(l), 
                    font = ("Times New Roman", 10)).grid(column = 21, 
                    row = k, padx = 30, pady = 25)
              
            self.dropdown_intru[l] = tk.StringVar()
            self.nodetype2[l] = ttk.Combobox(self.top, width = 27, 
                                        textvariable = self.dropdown_intru[l], state = "readonly")
              
            # Adding combobox drop down list
            self.nodetype2[l]['values'] = ('Exclude from modelling',
                                      'Treat as TAQ')
            self.nodetype2[l].current(0)
        #    nodetype2.current(0) 
            self.nodetype2[l].grid(column = 22, row = k)
            
class StartPage(tk.Frame):
    """ Main frame for tkinter app"""
    def __init__(self, parent, controller):
        global load_check, mcmc_check
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        
 #       super().__init__(*args, **kwargs)
        #define all variables that are used
        self.h_1 = 0
        self.w_1 = 0
        self.transx = 0
        self.transy = 0
        self.meta1 = ""
        self.metatext = ""
        self.rad_sel = ""
        self.mode = ""
        ##### intial values for all the functions
        self.delnodes = []
        self.edge_nodes = []
        self.comb_nodes = []
        self.edges_del = []
        self.temp = []
        self.x_1 = 1
        self.image = "noimage"
        self.phase_rels = None 
        self.chrono_dag = None
        self.imscale = 0
        self.graph = None
        self.littlecanvas_img = None
        self.width = 0
        self.height = 0
        self.delta = 0
        self.container = None
        self.datefile = None
        self.phasefile = None
        self.CONTEXT_NO = 0
        self.PHI_REF = None
        self.prev_phase = []
        self.post_phase = []
        self.ACCEPT = None
        self.PHI_ACCEPT = None
        self.resultsdict = None
        self.ALL_SAMPS_CONT = None
        self.ALL_SAMPS_PHI = None
        self.A = 0
        self.P = 0
        self.variable = 0
        self.image2 = 'noimage'
        self.resultsdict = {}
        self.all_results_dict = {}
        #forming and placing canvas and little canvas
        
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.canvas.update()
        self.littlecanvas = tk.Canvas(self.canvas, bd=0, bg = 'white',
                                      selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas.place(relx=0.02, rely=0.05, relwidth=0.35, relheight=0.9)
        self.littlecanvas2 = tk.Canvas(self.canvas, bd=0, bg = 'white',
                                      selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas2.place(relx=0.39, rely=0.05, relwidth=0.35, relheight=0.9)        
        self.littlecanvas.bind("<MouseWheel>", self.wheel)
        self.littlecanvas.bind('<Button-4>', self.wheel)# only with Linux, wheel scroll down
        self.littlecanvas.bind('<Button-5>', self.wheel)
        self.littlecanvas.bind('<Button-1>', self.move_from)
        self.littlecanvas.bind('<B1-Motion>', self.move_to)
        
        self.littlecanvas2.bind("<MouseWheel>", self.wheel2)
        self.littlecanvas2.bind('<Button-4>', self.wheel2)# only with Linux, wheel scroll down
        self.littlecanvas2.bind('<Button-5>', self.wheel2)
        self.littlecanvas2.bind('<Button-1>', self.move_from2)
        self.littlecanvas2.bind('<B1-Motion>', self.move_to2)
        #placing image on littlecanvas from graph
        self.littlecanvas.rowconfigure(0, weight=1)
        self.littlecanvas.columnconfigure(0, weight=1)
        self.littlecanvas.update()
        self.littlecanvas2.rowconfigure(0, weight=1)
        self.littlecanvas2.columnconfigure(0, weight=1)
        self.littlecanvas2.update()
        #### bind comands to canvas and little canvas ######
        self.dotbutton = ttk.Button(self.canvas, text ='Open dot file', command = lambda:self.open_file1())
        self.dotbutton.place(relx=0.05, rely=0.01, relwidth=0.1, relheight=0.03)
        self.stratbutton = ttk.Button(self.canvas, text ='Open strat text file', command = lambda:self.open_file2())
        self.stratbutton.place(relx=0.15, rely=0.01, relwidth=0.1, relheight=0.03)
        self.datebutton = ttk.Button(self.canvas, text ='Open date file', command = lambda:self.open_file3())
        self.datebutton.place(relx=0.25, rely=0.01, relwidth=0.1, relheight=0.03)
        self.phasebutton = ttk.Button(self.canvas, text ='Open phase file', command = lambda:self.open_file4())
        self.phasebutton.place(relx=0.35, rely=0.01, relwidth=0.1, relheight=0.03)
        self.phaserelbutton = ttk.Button(self.canvas, text ='Open phase rel file', command = lambda:self.open_file5())
        self.phaserelbutton.place(relx=0.45, rely=0.01, relwidth=0.1, relheight=0.03)
        self.eqrelbutton = ttk.Button(self.canvas, text ='Open equality file', command = lambda:self.open_file6())
        self.eqrelbutton.place(relx=0.55, rely=0.01, relwidth=0.1, relheight=0.03)
        self.phaselevsbutton = ttk.Button(self.canvas, text ='Display in phases', command = lambda:self.phasing())
        self.phaselevsbutton.place(relx=0.65, rely=0.01, relwidth=0.1, relheight=0.03)               
        self.mcmcbutton = ttk.Button(self.canvas, text ='Run MCMC', command = lambda: self.load_mcmc())
        
        self.mcmcbutton.place(relx=0.88, rely=0.01, relwidth=0.1, relheight=0.03)  
        self.button1 = ttk.Button(self.canvas, text="Go to Page One", command=lambda: controller.show_frame("PageOne"))
        self.button1.place(relx=0.78, rely=0.04, relwidth=0.1, relheight=0.03) 
        self.save_button = ttk.Button(self.canvas, text = "Save", command = self.save_state)
        self.save_button.place(relx=0.78, rely=0.94, relwidth=0.1, relheight=0.03) 
        self.load_button = ttk.Button(self.canvas, text = "Reload", command = self.restore_state)
        self.load_button.place(relx=0.58, rely=0.94, relwidth=0.1, relheight=0.03) 
  #      self.button2 = ttk.Button(self.canvas, text="Go to Page Two", command=lambda: controller.show_frame("PageTwo"))
   #     self.button2.place(relx=0.78, rely=0.03, relwidth=0.1, relheight=0.03) 
        
        #########deleted nodes##################
        self.nodescanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0)
        self.nodescanvas.place(relx=0.75, rely=0.05, relwidth=0.35, relheight=0.2)
        self.text = tk.Text(self.nodescanvas, font = ('arial', 12, BOLD), bg = '#e8fdff')
        self.nodescanvas.create_window((0, 0), window=self.text, anchor='nw')
        self.text.insert('end', 'Deleted Contexts:\n' + str(self.delnodes)[1:-1])
        self.text.configure(state='disabled')
        ###########deleted edges###############################
        self.edgescanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0)
        self.edgescanvas.place(relx=0.75, rely=0.27, relwidth=0.35, relheight=0.2)
        self.text = tk.Text(self.edgescanvas, width=120, height=40, bg =  '#e8fdff' )
        self.edgescanvas.create_window((0, 0), window=self.text, anchor='nw')
        self.text.insert('end', 'Deleted Edges:\n') #+ str(self.edges_del[1:-1]))
        self.text.configure(state='disabled')
      #  pagetwo = self.controller.get_('PageTwo')
      #  self.popup3 = pagetwo.popup4
        ##########radiobutton for edge delete node delete##########

        self.OptionList = [
            "Delete Node",
            "Delete Edge",
            "Get Metadata",
            "Combine Node",
            "Place Above Other Context",
            "Add Nodes",
            "Metadata Menu",
            "Get stratigraphic information"
            ]
        self.variable = tk.StringVar(self.littlecanvas)
        self.variable.set("Node Action")
        self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable,self.OptionList[0], *self.OptionList, command = self.nodes)

    def resid_check(self):
        global load_check
        MsgBox = tk.messagebox.askquestion ('Residual and Intrusive Contexts','Do you suspect any of your samples are residual or intrusive?',icon = 'warning')
        if MsgBox == 'yes':
        #    pagetwo = self.controller.get_page('PageTwo')
         #   self.popup3 = pagetwo.popup4
           # self.controller.show_frame("PageTwo")
            pagetwo = PageTwo(self, self.controller)
            self.popup3 = pagetwo.popup4 

        else:            
            self.popup3 = popupWindow3(self, self.controller, self.graph, self.littlecanvas2, self.phase_rels, {}) 

            
        def destroy(self):
            self.testmenu.place_forget()
    #    # This is the function that removes the selected item when the label is clicked.
        def delete(self, *args):
            self.destroy()  
            self.testmenu.place_forget()
            self.variable.set("Node Action")
        self.metacanvas = tk.Canvas(self.canvas, bg="white")
        self.metacanvas.place(relx=0.75, rely=0.52, relwidth=0.35, relheight=0.2)
        self.abovebelowcanvas = tk.Canvas(self.canvas, bg="white")
        self.abovebelowcanvas.place(relx=0.75, rely=0.75, relwidth=0.35, relheight=0.2)
    



    def save_state(self):
        global mcmc_check, load_check
        try:
            data = {
                "h_1": self.h_1, 
                "w_1": self.w_1,
                "transx": self.transx,
                "transy":self.transy,
                "meta1": self.meta1,
                "metatext": self.metatext, 
                "rad_sel": self.rad_sel,
                "mode": self.mode,
                "del_nodes": self.delnodes, 
                "edge_nodes": self.edge_nodes, 
                "comb_nodes": self.comb_nodes,
                "edges_del": self.edges_del,
                "temp": self.temp,
                "x_1": self.x_1,
                "image": self.image, 
                "phase_rels": self.phase_rels, 
                "chrono_dag": self.chrono_dag, 
                "imscale": self.imscale,
#                "variable": self.variable,
                "graph": self.graph,
                "littlecanvas_img": self.littlecanvas_img,
                "width" : self.width,
                "height" : self.height,
                "delta" : self.delta,
                "container" : self.container,
                "datefile" : self.datefile,
                "context_no" : self.CONTEXT_NO,
                "accept" : self.ACCEPT,
                "phi_accept": self.PHI_ACCEPT,
                "A" : self.A,
                "P" : self.P,
                'all_samps_cont' : self.ALL_SAMPS_CONT,
                'all_samps_phi' : self.ALL_SAMPS_PHI,
                'load_check': load_check,
                'mcmc_check' : mcmc_check,
                'phasefile' : self.phasefile,
                'phi_ref': self.PHI_REF, 
                'prev_phase' : self.prev_phase, 
                'post_phase' : self.post_phase,
                'resultsdict' : self.resultsdict,
                'all_results_dict' : self.all_results_dict
            }
            with open(FILENAME, "wb") as f:
                pickle.dump(data, f)

        except Exception as e:
            print
            "error saving state:", str(e)

    def restore_state(self): 
        global load_check, mcmc_check, FILE_INPUT
        try:
            with open(FILENAME, "rb") as f:
                data = pickle.load(f)
            
            self.h_1 = data["h_1"]
            self.w_1 = data["w_1"]
            self.transx = data["transx"]
            self.transy = data["transy"]
            self.meta1 = data["meta1"]
            self.metatext = data["metatext"] 
            self.rad_sel = data["rad_sel"]
            self.mode = data["mode"]
            self.delnodes = data["del_nodes"] 
            self.edge_nodes = data["edge_nodes"] 
            self.comb_nodes = data["comb_nodes"]
            self.edges_del = data["edges_del"]
            self.temp = data["temp"]
            self.x_1 = data["x_1"]
            self.image = data["image"]
            self.phase_rels = data["phase_rels"] 
            self.chrono_dag = data["chrono_dag"] 
            self.imscale = data["imscale"]
#            self.variable = data["variable"]
            self.graph = data["graph"]
            self.littlecanvas_img = data["littlecanvas_img"]
            self.width = data["width"]
            self.height = data["height"]
            self.delta = data["delta"]
            self.container = data["container"]
            self.datefile = data["datefile"]
            self.CONTEXT_NO = data["context_no"]
            self.ACCEPT = data["accept"]
            self.ALL_SAMPS_CONT = data['all_samps_cont']
            self.ALL_SAMPS_PHI = data['all_samps_phi']
            self.PHI_ACCEPT = data["phi_accept"]
            self.A = data["A"]
            self.P = data["P"]
            load_check = data['load_check']
            mcmc_check = data['mcmc_check']
            self.resultsdict = data['resultsdict']
            self.phasefile = data['phasefile']
            self.phi_ref = data['phi_ref']
            self.prev_phase = data['prev_phase'] 
            self.post_phase = data['post_phase']
            self.all_results_dict = data['all_results_dict']
            if type(self.graph) != 'NoneType':
                self.rerender_stratdag()
            if load_check == 'loaded':
                FILE_INPUT = None
                self.chronograph_render_wrap()
            
        
        except Exception as e:
            print
            "error loading saved state:", str(e)
            
              
    def onRight(self, *args):
        '''makes test menu appear after right click '''
        self.littlecanvas.unbind("Button-1>")
        self.littlecanvas.bind("<Button-1>", self.onLeft)
        # Here we fetch our X and Y coordinates of the cursor RELATIVE to the window
        self.cursorx = int(self.littlecanvas.winfo_pointerx() - self.littlecanvas.winfo_rootx())
        self.cursory = int(self.littlecanvas.winfo_pointery() - self.littlecanvas.winfo_rooty())
        if self.image != "noimage":
            x_scal = self.cursorx + self.transx
            y_scal = self.cursory + self.transy
            self.node = self.nodecheck(x_scal, y_scal)
        # Now we define our right click menu canvas
        # And here is where we use our X and Y variables, to place the menu where our cursor is,
        # That's how right click menus should be placed.           
        self.testmenu.place(x=self.cursorx, y=self.cursory)
        # This is for packing our options onto the canvas, to prevent the canvas from resizing.
        # This is extremely useful if you split your program into multiple canvases or frames
        # and the pack method is forcing them to resize.
        self.testmenu.pack_propagate(0)
        # Here is our label on the right click menu for deleting a row, notice the cursor
        # value, which will give us a pointy finger when you hover over the option.
        self.testmenu.config(width=10)        
        # This function is for removing the canvas when an option is clicked.
  
    def preClick(self, *args):
        '''makes test menu appear and removes any previous test menu'''
        try:
            self.testmenu.place_forget()
            self.onRight()
        except Exception:  
            self.onRight()

    # Hide menu when left clicking
    def onLeft(self, *args):
        '''hides menu when left clicking'''
        try:
            self.testmenu.place_forget()
        except Exception:
            pass

    def open_file1(self): 
        '''opens dot file'''
        global node_df
     #   t0 = time.time()
        global FILE_INPUT
        file = askopenfile(mode ='r', filetypes =[('Python Files', '*.dot')])             
        FILE_INPUT = file.name
        self.graph = nx.DiGraph(imagefunc(file.name))
        if phase_true == 1:
                self.image = imgrender_phase(self.graph)
        else:
            self.image = imgrender(self.graph)
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw",
                                                               image=self.littlecanvas.img)

        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.canvas.bind("<Configure>", self.resize)
        self.littlecanvas.bind("<Configure>", self.resize)
        self.nodescanvas.bind("<Configure>", self.resize)
        self.edgescanvas.bind("<Configure>", self.resize)
        self.delnodes = []
        self.text.delete("1.0", "end")
        self.text = tk.Text(self.nodescanvas, width=120, height=40,  font = ('arial', 12, BOLD), bg = '#e8fdff')
        self.nodescanvas.create_window((0, 0), window=self.text, anchor='nw')
        self.text.insert('end', 'Deleted Contexts:\n' + str(self.delnodes)[1:-1])
        self.text.configure(state='disabled')
        self.testbutton = ttk.Button(self.canvas, text ='Render Chronological DAG', command = lambda:self.chronograph_render_wrap()) #popupWindow3(self, self.graph, self.littlecanvas2))
        self.testbutton.place(relx=0.75, rely=0.01, relwidth=0.15, relheight=0.03) 
        self.littlecanvas.bind("<Button-3>", self.preClick)

    def rerender_stratdag(self):
        if phase_true == 1:
                self.image = imgrender_phase(self.graph)
        else:
            self.image = imgrender(self.graph)
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw",
                                                               image=self.littlecanvas.img)

        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.canvas.bind("<Configure>", self.resize)
        self.littlecanvas.bind("<Configure>", self.resize)
        self.nodescanvas.bind("<Configure>", self.resize)
        self.edgescanvas.bind("<Configure>", self.resize)
        self.delnodes = []
        self.text.delete("1.0", "end")
        self.text = tk.Text(self.nodescanvas, width=120, height=40,  font = ('arial', 12, BOLD), bg = '#e8fdff')
        self.nodescanvas.create_window((0, 0), window=self.text, anchor='nw')
        self.text.insert('end', 'Deleted Contexts:\n' + str(self.delnodes)[1:-1])
        self.text.configure(state='disabled')
        self.testbutton = ttk.Button(self.canvas, text ='Render Chronological DAG', command = lambda:self.chronograph_render_wrap()) #popupWindow3(self, self.graph, self.littlecanvas2))
        self.testbutton.place(relx=0.75, rely=0.01, relwidth=0.15, relheight=0.03) 
        self.littlecanvas.bind("<Button-3>", self.preClick)
    
    def chronograph_render_wrap(self):
        self.chrono_dag = self.chronograph_render()
        
    def open_file2(self): 
        '''opens plain text strat file'''
   #     t0 = time.time()
        global FILE_INPUT
        file = askopenfile(mode ='r', filetypes =[('Python Files', '*.csv')]) 
        if file is not None: 
            FILE_INPUT = None
            self.stratfile = pd.read_csv(file, dtype = str)
            G = nx.DiGraph()
            for i in set(self.stratfile.iloc[:,0]):
                G.add_node(i, shape="box", fontname="Helvetica", fontsize="30.0", penwidth="1.0", color = 'black')
                G.nodes()[i].update({"Date": [None, None]})
                G.nodes()[i].update({"Phase": None})
            edges = []
            for i in range(len(self.stratfile)):
                a = tuple(self.stratfile.iloc[i,:])
                if pd.isna(a[1]) == False:
                    edges.append(a)                
            G.add_edges_from(edges, arrowhead="none")
            self.graph = G
            if phase_true == 1:
                self.image = imgrender_phase(self.graph)
            else:
                self.image = imgrender(self.graph)
                self.littlecanvas.img = ImageTk.PhotoImage(self.image)
                self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw",
                                                                       image=self.littlecanvas.img)
    
                self.width, self.height = self.image.size
                self.imscale = 1.0  # scale for the canvaas image
                self.delta = 1.1  # zoom magnitude
                # Put image into container rectangle and use it to set proper coordinates to the image
                self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
                self.canvas.bind("<Configure>", self.resize)
                self.littlecanvas.bind("<Configure>", self.resize)
                self.nodescanvas.bind("<Configure>", self.resize)
                self.edgescanvas.bind("<Configure>", self.resize)
                self.delnodes = []
                self.text.delete("1.0", "end")
                self.text = tk.Text(self.nodescanvas, width=120, height=40)
                self.nodescanvas.create_window((0, 0), window=self.text, anchor='nw')
                self.text.insert('end', 'Deleted Contexts:\n' + str(self.delnodes)[1:-1])
                self.text.configure(state='normal')
                self.testbutton = ttk.Button(self.canvas, text ='Render Chronological DAG', command = lambda:self.chronograph_render_wrap()) #popupWindow3(self, self.graph, self.littlecanvas2))
                self.testbutton.place(relx=0.75, rely=0.01, relwidth=0.15, relheight=0.03) 
                self.littlecanvas.bind("<Button-3>", self.preClick)
    #canvas to hold buttons
#        #canvas to hold the metadata

     
           # return(content)
    
    def open_file3(self): 
     #   t0 = time.time()
        file = askopenfile(mode ='r', filetypes =[('Python Files', '*.csv')]) 
        if file is not None: 
            self.datefile = pd.read_csv(file)
            self.datefile = self.datefile.applymap(str)
            for i, j in enumerate(self.datefile["context"]):
                self.graph.nodes()[str(j)].update({"Date":[self.datefile["date"][i], self.datefile["error"][i]]})
            self.context_no = list(self.graph.nodes())    

            
    def open_file4(self): 
    #    t0 = time.time()
        file = askopenfile(mode ='r', filetypes =[('Pythotransxn Files', '*.csv')]) 
        if file is not None: 
            self.phasefile = pd.read_csv(file)
            self.phasefile = self.phasefile.applymap(str)
            for i, j in enumerate(self.phasefile["context"]):
                self.graph.nodes()[str(j)].update({"Phase":self.phasefile["phase"][i]})
         #   self.phase_list = set(self.phasefile["phase"])

    def open_file5(self): 
   #     t0 = time.time()
        file = askopenfile(mode ='r', filetypes =[('Python Files', '*.csv')]) 
        if file is not None: 
            phase_rel_df = pd.read_csv(file)
            self.phase_rels = [(str(phase_rel_df['above'][i]), str(phase_rel_df['below'][i])) for i in range(len(phase_rel_df))] 

    def open_file6(self): 
   #     t0 = time.time()
        file = askopenfile(mode ='r', filetypes =[('Python Files', '*.csv')]) 
        if file is not None: 
            equal_rel_df = pd.read_csv(file)
            self.equal_rel_df = equal_rel_df.applymap(str)
            context_1 = list(self.equal_rel_df.iloc[:,0])
            context_2 = list(self.equal_rel_df.iloc[:,1])
            for k, j in enumerate(context_1):
                self.graph = nx.contracted_nodes(self.graph, j, context_2[k])
                x_nod = list(self.graph) 
                newnode = str(j) + " = " + str(context_2[k])
                y_nod = [newnode if i==j else i for i in x_nod]
                mapping = dict(zip(x_nod, y_nod))
                self.graph = nx.relabel_nodes(self.graph, mapping)
            if phase_true == 1:
                imgrender_phase(self.graph)
            else:
                imgrender(self.graph) 
            self.image = Image.open('testdag.png')
            self.width, self.height = self.image.size
            self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
            self.show_image()
    def cleanup(self):
        self.top.destroy()
    def load_mcmc(self):
        global mcmc_check
        self.top=tk.Toplevel(self.littlecanvas)
        self.top.geometry("1000x400")
        self.l=ttk.Label(self.top,text="MCMC in progress")
        self.l.pack()
        outputPanel = tk.Text(self.top, wrap='word', height = 11, width=50)
        outputPanel.pack()
        sys.stdout = StdoutRedirector(outputPanel)
        self.CONTEXT_NO, self.ACCEPT, self.PHI_ACCEPT, self.PHI_REF, self.A, self.P, self.ALL_SAMPS_CONT, self.ALL_SAMPS_PHI, self.resultsdict, self.all_results_dict = self.MCMC_func()
        mcmc_check = 'mcmc_loaded'
        sys.stdout = old_stdout
        self.controller.show_frame('PageOne')
        self.cleanup()
        
    def addedge(self, edgevec):
        global node_df
        x_1 = edgevec[0]
        x_2 = edgevec[1]
        self.graph.add_edge(x_1, x_2)
        if phase_true == 1:
            imgrender_phase(self.graph)
        else:
            imgrender(self.graph)
        self.image = Image.open('testdag.png')
        self.show_image()  


    def run_popup3(self):
            self.popup3 = popupWindow3(self, self.controller, self.graph, self.littlecanvas2, self.phase_rels, {}) 

##        #pt2
    def chronograph_render(self):
        global load_check
        if load_check != 'loaded':
            self.resid_check()
        try: 
            load_check = 'loaded'
        except (RuntimeError, TypeError, NameError):
            load_check = 'not_loaded'
        self.image2 = imgrender2(load_check)
        if self.image2 != 'No_image':
            self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
            self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw",
                                                                   image=self.littlecanvas2.img)
    
            self.width2, self.height2 = self.image2.size
            self.imscale2 = 1.0  # scale for the canvaas image
            self.delta2 = 1.1  # zoom magnitude
            # Put image into container rectangle and use it to set proper coordinates to the image
            self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
            self.littlecanvas2.bind("<Configure>", self.resize2)
            load_check = 'loaded'
        return self.popup3.graphcopy
    
    
    def stratfunc(self, node):
        rellist = list(nx.line_graph(self.graph))
        above = ()
        below = ()
        for i in enumerate(rellist):
            if str(node) in rellist[i[0]]:
                if str(node) == rellist[i[0]][0]:
                    below = np.append(below, rellist[i[0]][1])
                elif str(node) == rellist[i[0]][1]:
                    above = np.append(above, rellist[i[0]][0])
        abovebelowtext = tk.Text(self.abovebelowcanvas,
                                 width=120, height=40)
        self.abovebelowcanvas.create_window((0, 0), window=abovebelowtext, anchor='nw')
        abovebelowtext.insert('end', 'Direct stratigraphic relationships:\n Contexts above: ' +
                              str(above) + '\n' + 'Contexts below:' + str(below))

    def animation_start(self):
        self.pbar_ind.start() # .start


    def animation_stop(self):
        self.pbar_ind.stop()  
    

    def MCMC_func(self):
        context_no = [x for x in list(self.popup3.context_no) if x not in self.popup3.node_del_tracker] 
        print('cont_no')
        print(context_no)
        self.key_ref = [list(self.phasefile["phase"])[list(self.phasefile["context"]).index(i)] for i in context_no]
    #    print(self.key_ref)
        strat_vec = [[list(self.graph.predecessors(i)), list(self.graph.successors(i))] for i in context_no]
     #   print(strat_vec)
        self.RCD_EST = [int(list(self.datefile["date"])[list(self.datefile["context"]).index(i)]) for i in context_no]
        self.RCD_ERR = [int(list(self.datefile["error"])[list(self.datefile["context"]).index(i)]) for i in context_no]   
      #  print(self.RCD_EST)
       # print(self.RCD_ERR)
        rcd_est = self.RCD_EST
        rcd_err = self.RCD_ERR
        #print(self.popup3.CONT_TYPE)
  #      self.CONT_TYPE = ['normal' for i in context_no]
        TOPO = list(nx.topological_sort(self.chrono_dag))
        TOPO_SORT = [x for x in TOPO if (x not in self.popup3.node_del_tracker) and (x in context_no)]
        TOPO_SORT.reverse()
        print('topo')
        print(TOPO_SORT)
        self.prev_phase, self.post_phase = self.popup3.prev_phase, self.popup3.post_phase
  #      print(self.prev_phase, self.post_phase)
        CONTEXT_NO, ACCEPT, PHI_ACCEPT, PHI_REF, A, P, ALL_SAMPS_CONT, ALL_SAMPS_PHI = mcmc.run_MCMC(CALIBRATION, strat_vec, rcd_est, rcd_err, self.key_ref, context_no, self.popup3.phi_ref, self.popup3.prev_phase, self.popup3.post_phase, TOPO_SORT, self.popup3.CONT_TYPE)
        phase_nodes, resultsdict, all_results_dict = phase_labels(PHI_REF, self.popup3.post_phase, PHI_ACCEPT, ALL_SAMPS_PHI)
        for i, j in enumerate(CONTEXT_NO):
            resultsdict[j] = ACCEPT[i]
        for k, l in enumerate(CONTEXT_NO):
            all_results_dict[l] = ALL_SAMPS_CONT[k]
        
        return CONTEXT_NO, ACCEPT, PHI_ACCEPT, PHI_REF, A, P, ALL_SAMPS_CONT, ALL_SAMPS_PHI, resultsdict, all_results_dict

        
        

    def nodecheck(self, x_current, y_current):
 #       t0 = time.time()
        """ returns the node that corresponds to the mouse cooridinates"""
        node_inside = "no node"
        node_df_con = node_coords_fromjson(self.graph)
        node_df = node_df_con[0]
        xmax, ymax = node_df_con[1]
        #forms a dataframe from the dicitonary of coords    
        x, y = self.image.size 
        cavx = x*self.imscale
        cany = y*self.imscale

        xscale = (x_current)*(xmax)/cavx
        yscale = (cany-y_current)*(ymax)/cany
        outline = nx.get_node_attributes(self.graph, 'color')
        for n_ind in range(node_df.shape[0]):
            if ((node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and
                    (node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper)):
                node_inside = node_df.iloc[n_ind].name  
                self.graph[node_inside]
                outline[node_inside] = 'red'
                nx.set_node_attributes(self.graph, outline, 'color')  
            if phase_true == 1:
                imgrender_phase(self.graph)
            else:
                imgrender(self.graph) 
            self.image = Image.open('testdag.png')
            self.show_image()
        return node_inside

    def edge_render(self):
#        t0 = time.time()
        """renders string for deleted edges"""
        self.edges_del = self.edge_nodes
        edgetext = tk.Text(self.edgescanvas,
                           width=120, height=40, font = ('arial', 12, BOLD), bg = '#e8fdff')
        self.edgescanvas.create_window((0, 0), window=edgetext, anchor='nw')
        ednodes = str(self.edges_del[0]) + ' above '+ str(self.edges_del[1])
        self.temp = str(self.temp).replace('[', '')
        self.temp = str(self.temp).replace(']', '')
        self.temp = self.temp + '\n' + str(ednodes.replace("'", ""))
        edgetext.insert('end', 'Deleted Edges:' + str(self.temp)) #self.temp is string of deleted edges
        edgetext.configure()

    def nodes(self, currentevent):
        """performs action using the node and redraws the graph"""
        self.testmenu.place_forget()
        if self.variable.get() == "Delete Node":
            if self.node != "no node":
                self.graph.remove_node(self.node)
                self.delnodes = np.append(self.delnodes, self.node)
        
        if self.variable.get() == "Add Nodes":
            self.w=popupWindow(self)
            self.wait_window(self.w.top)
            self.node = self.w.value 
            self.graph.add_node(self.node, shape="box", fontsize="30.0",
                               fontname="Ubuntu", penwidth="1.0")                   
                       
        if self.variable.get() == "Metadata Menu":
            self.w=popupWindow2(self, self.graph, self.metacanvas)    
        if len(self.edge_nodes) == 1:       
            if self.variable.get() == "Delete Edge with "+ str(self.edge_nodes[0]):
                self.edge_nodes = np.append(self.edge_nodes, self.node)
                try:
                    self.graph.remove_edge(self.edge_nodes[0], self.edge_nodes[1])
                    self.edge_render()
                except (KeyError, nx.exception.NetworkXError):
                    try:
                        self.graph.remove_edge(self.edge_nodes[1], self.edge_nodes[0])
                        self.edge_render()
                    except (KeyError, nx.exception.NetworkXError):
                        ttk.messagebox.showinfo('Error', 'An edge doesnt exist between those nodes')
                
                self.OptionList.remove("Delete Edge with "+ str(self.edge_nodes[0]))
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command=self.nodes)
                self.edge_nodes = []

            elif self.variable.get() == ("Place "+ str(self.edge_nodes[0]) + " Above"):
                self.edge_nodes = np.append(self.edge_nodes, self.node) 
                self.addedge(self.edge_nodes)
                self.OptionList.remove("Place "+ str(self.edge_nodes[0]) + " Above")
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command=self.nodes)
                self.edge_nodes = []      
                
        if self.variable.get() == "Delete Edge":
            if len(self.edge_nodes) == 1:
                self.OptionList.remove("Delete Edge with "+ str(self.edge_nodes[0]))
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command = self.nodes)
                self.edge_nodes = []                    
            self.edge_nodes = np.append(self.edge_nodes, self.node)                
            self.OptionList.append("Delete Edge with "+ str(self.edge_nodes[0]))
            self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command = self.nodes)

        if len(self.comb_nodes) == 1:       
            if self.variable.get() == "Combine Node with "+ str(self.comb_nodes[0]):
                self.comb_nodes = np.append(self.comb_nodes, self.node)
                self.graph = nx.contracted_nodes(self.graph, self.comb_nodes[0], self.comb_nodes[1])
                x_nod = list(self.graph) 
                newnode = str(self.comb_nodes[0]) + " = " + str(self.comb_nodes[1])
                y_nod = [newnode if i==self.comb_nodes[0] else i for i in x_nod]
                mapping = dict(zip(x_nod, y_nod))
                self.graph = nx.relabel_nodes(self.graph, mapping)
                self.OptionList.remove("Combine Node with "+ str(self.comb_nodes[0]))
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command = self.nodes)
                self.comb_nodes = []
                
        if self.variable.get() == "Combine Node":
            if len(self.comb_nodes) == 1:
                self.OptionList.remove("Combine Node with "+ str(self.comb_nodes[0]))
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command = self.nodes)
                self.comb_nodes = []                    
            self.comb_nodes = np.append(self.comb_nodes, self.node)                
            self.OptionList.append("Combine Node with "+ str(self.comb_nodes[0]))
            self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command = self.nodes)       
                        
        if self.variable.get() == "Get Metadata":
            self.metatext = tk.Text(self.metacanvas, width=120, height=40)
            self.metacanvas.create_window((0, 0), window=self.metatext, anchor='nw')
            self.meta1 = pd.DataFrame.from_dict(self.graph.nodes()[str(self.node)], orient='index')
            self.meta2 = self.meta1.loc["Date":"Phase",]
            self.meta2.columns = ["Data"]
            if self.meta2.loc["Date"][0] != "None":
               self.meta2.loc["Date"][0] = str(self.meta2.loc["Date"][0][0]) + " +- " + str(self.meta2.loc["Date"][0][1]) + " Carbon BP"
            self.metatext.insert('end', 'Metadata of node ' +
                                 str(self.node) + ':\n')
            cols = list(self.meta2.columns)
            tree = ttk.Treeview(self.metacanvas)
            tree["columns"] = cols
            tree.place(relx=0, rely=0.25)
            tree.column("Data", anchor="w")
            tree.heading("Data", text="Data", anchor='w')        
            for index, row in self.meta2.iterrows():
                tree.insert("",0,text=index,values=list(row))
            self.metatext.configure()
                
        if self.variable.get() == "Place Above Other Context":
            if len(self.edge_nodes) == 1:
                "tester"
                self.OptionList.remove("Place "+ str(self.edge_nodes[0]) + " Above")
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command = self.nodes)
                self.edge_nodes = []                    
            self.edge_nodes = np.append(self.edge_nodes, self.node)                
            self.OptionList.append("Place "+ str(self.edge_nodes[0]) + " Above")
            self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command = self.nodes)
        if self.variable.get() == "Get stratigraphic information":
            self.stratfunc(self.node)
        nx.set_node_attributes(self.graph, 'black', 'color')    
        if phase_true == 1:
            imgrender_phase(self.graph)
        else:
            imgrender(self.graph) 
        self.image = Image.open('testdag.png')
        self.width, self.height = self.image.size
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.show_image()
        self.text = tk.Text(self.nodescanvas, width=120, height=40)
        self.nodescanvas.create_window((0, 0), window=self.text, anchor='nw')
        nbnodes = str(self.delnodes)
        self.text.insert('end', 'Deleted Contexts:\n' + str(nbnodes.replace("'", ""))[1:-1])
        self.text.configure(state='normal')
        self.variable.set("Node Action")
        self.littlecanvas.unbind('<Button-1>')
        self.littlecanvas.bind('<Button-1>', self.move_from)
        self.littlecanvas.bind("<MouseWheel>", self.wheel)


    def move_from(self, event):
#        t0 = time.time()
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image != "noimage":
            self.littlecanvas.scan_mark(event.x, event.y)

    def move_to(self, event):
 #       t0 = time.time()
        """Drag (move) canvas to the new position"""
        if self.image != "noimage":
            self.littlecanvas.scan_dragto(event.x, event.y, gain=1)
            self.show_image()
            
        # redraw the image
    def move_from2(self, event):
#        t0 = time.time()
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image2 != "noimage":
            self.littlecanvas2.scan_mark(event.x, event.y)

    def move_to2(self, event):
 #       t0 = time.time()
        """Drag (move) canvas to the new position"""
        if self.image2 != "noimage":
            self.littlecanvas2.scan_dragto(event.x, event.y, gain=1)
            self.show_image()
            
            
    def wheel(self, event):
  #      t0 = time.time()
        """Zoom with mouse wheel"""
        x_zoom = self.littlecanvas.canvasx(event.x)
        y_zoom = self.littlecanvas.canvasy(event.y)
        bbox = self.littlecanvas.bbox(self.container)  # get image area 
        if bbox[0] < x_zoom < bbox[2] and bbox[1] < y_zoom < bbox[3]:
            pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale *= self.delta  
        self.littlecanvas.scale('all', 0, 0, scale, scale)  # rescale all canvas objects
        self.show_image()
        
    def wheel2(self, event):
   #     t0 = time.time()
        """Zoom with mouse wheel"""
        x_zoom = self.littlecanvas2.canvasx(event.x)
        y_zoom = self.littlecanvas2.canvasy(event.y)
        bbox = self.littlecanvas2.bbox(self.container2)  # get image area 
        if bbox[0] < x_zoom < bbox[2] and bbox[1] < y_zoom < bbox[3]:
            pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale2 = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width2, self.height2)
            if int(i * self.imscale2) < 30:
                return  # image is less than 30 pixels
            self.imscale2 /= self.delta2
            scale2 /= self.delta2
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.littlecanvas2.winfo_width(), self.littlecanvas2.winfo_height())
            if i < self.imscale2:
                return  # 1 pixel is bigger than the visible area
            self.imscale2 *= self.delta2
            scale2 *= self.delta2  
        self.littlecanvas2.scale('all', 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def show_image(self):
        """Show image on the Canvas"""
        bbox1 = [0, 0, int(self.image.size[0]*self.imscale), int(self.image.size[1]*self.imscale)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.littlecanvas.canvasx(0),  # get visible area of the canvas
                 self.littlecanvas.canvasy(0),
                 self.littlecanvas.canvasx(self.littlecanvas.winfo_width()),
                 self.littlecanvas.canvasy(self.littlecanvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        bbox1 = [0, 0, int(self.image.size[0]*self.imscale), int(self.image.size[1]*self.imscale)]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.littlecanvas.configure(scrollregion=bbox)  # set scroll region
        x_1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y_1 = max(bbox2[1] - bbox1[1], 0)
        x_2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y_2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x_2 - x_1) > 0 and int(y_2 - y_1) > 0:  # show image if it in the visible area
            x_img = min(int(x_2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x_1 / self.imscale), int(y_1 / self.imscale),
                                     x_img, y_img))
            self.imagetk = ImageTk.PhotoImage(image.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.littlecanvas.delete(self.littlecanvas_img)
            self.imageid = self.littlecanvas.create_image(max(bbox2[0], bbox1[0]),
                                                          max(bbox2[1], bbox1[1]), anchor='nw',
                                                          image=self.imagetk)
            self.transx, self.transy = bbox2[0], bbox2[1]
            self.littlecanvas.imagetk = self.imagetk
            
    def show_image2(self):
        """Show image on the Canvas"""
        bbox1 = [0, 0, int(self.image2.size[0]*self.imscale2), int(self.image2.size[1]*self.imscale2)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.littlecanvas2.canvasx(0),  # get visible area of the canvas
                 self.littlecanvas2.canvasy(0),
                 self.littlecanvas2.canvasx(self.littlecanvas2.winfo_width()),
                 self.littlecanvas2.canvasy(self.littlecanvas2.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        bbox1 = [0, 0, int(self.image2.size[0]*self.imscale2), int(self.image2.size[1]*self.imscale2)]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.littlecanvas2.configure(scrollregion=bbox)  # set scroll region
        x_1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y_1 = max(bbox2[1] - bbox1[1], 0)
        x_2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y_2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x_2 - x_1) > 0 and int(y_2 - y_1) > 0:  # show image if it in the visible area
            x_img = min(int(x_2 / self.imscale2), self.width2)   # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale2), self.height2)  # ...and sometimes not
            image2 = self.image2.crop((int(x_1 / self.imscale2), int(y_1 / self.imscale2),
                                     x_img, y_img))
            self.imagetk2 = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.littlecanvas2.delete(self.littlecanvas2_img)
            self.imageid2 = self.littlecanvas2.create_image(max(bbox2[0], bbox1[0]),
                                                          max(bbox2[1], bbox1[1]), anchor='nw',
                                                          image=self.imagetk2)
            self.transx2, self.transy2 = bbox2[0], bbox2[1]
            self.littlecanvas.imagetk2 = self.imagetk2            


    def phasing(self):
        global phase_true, node_df
 #       t0 = time.time()
        """runs image render function with phases on seperate levels"""
        imgrender_phase(self.graph)
        self.image = Image.open('testdag.png')
        phase_true = 1
        self.show_image()
        node_df = node_coords_fromjson("fi_new.txt")
        return node_df


    def resize(self, event):
    #    t0 = time.time()
        """resizes image on canvas"""
        img = Image.open('testdag.png')#.resize((event.width, event.height), Image.ANTIALIAS)
        self.littlecanvas.img = ImageTk.PhotoImage(img)
        self.w_1 = event.width
        self.h_1 = event.height
        self.littlecanvas.itemconfig(self.littlecanvas_img, image=self.littlecanvas.img)
        
    def resize2(self, event):
#        t0 = time.time()
        """resizes image on canvas"""
        img = Image.open('testdag.png')#.resize((event.width, event.height), Image.ANTIALIAS)
        self.littlecanvas2.img = ImageTk.PhotoImage(img)
        self.w_1 = event.width
        self.h_1 = event.height
        self.littlecanvas2.itemconfig(self.littlecanvas2_img, image=self.littlecanvas2.img)        



class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller 
        label = tk.Label(self, text="This is page 1")
        label.pack(side="top", fill="x", pady=10)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        #define all variables that are used
        self.h_1 = 0
        self.w_1 = 0
        self.transx2 = 0
        self.transy2 = 0
        self.meta1 = ""
        self.metatext = ""
        self.rad_sel = ""
        self.mode = ""
        ##### intial values for all the functions
        self.delnodes = []
        self.edge_nodes = []
        self.comb_nodes = []
        self.edges_del = []
        self.temp = []
        self.results_list = []
        self.x_1 = 1
        self.image = "noimage"
        self.phase_rels = None 
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1 
        self.results_text = None
        self.canvas_plt = None
        self.phase_len_nodes = []
        #forming and placing canvas and little canvas
        
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.canvas.update()
        self.littlecanvas = tk.Canvas(self.canvas, bd=0, bg = 'white',
                                      selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas.place(relx=0.02, rely=0.05, relwidth=0.35, relheight=0.43)
        self.littlecanvas_a = tk.Canvas(self.canvas, bd=0, bg = 'white',
                                      selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas_a.place(relx=0.02, rely=0.50, relwidth=0.35, relheight=0.43)
        self.littlecanvas2 = tk.Canvas(self.canvas, bd=0, bg = 'white',
                                      selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas2.place(relx=0.39, rely=0.05, relwidth=0.35, relheight=0.9)    
        self.littlecanvas3 = tk.Canvas(self.canvas, bd=0, bg = 'white',
                                      selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas3.place(relx=0.77, rely=0.25, relwidth=0.2, relheight=0.5)  
        
        
        self.littlecanvas2.bind("<MouseWheel>", self.wheel2)
        self.littlecanvas2.bind('<Button-4>', self.wheel2)# only with Linux, wheel scroll down
        self.littlecanvas2.bind('<Button-5>', self.wheel2)
        self.littlecanvas2.bind('<Button-3>', self.onRight)
        self.littlecanvas2.bind('<Button-1>', self.move_from2)
        self.littlecanvas2.bind('<B1-Motion>', self.move_to2)
        #placing image on littlecanvas from graph
        self.littlecanvas2.rowconfigure(0, weight=1)
        self.littlecanvas2.columnconfigure(0, weight=1)
        self.littlecanvas2.update()
        #placing image on littlecanvas from graph
        self.littlecanvas.rowconfigure(0, weight=1)
        self.littlecanvas.columnconfigure(0, weight=1)
        self.littlecanvas.update()

        self.button1 = ttk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        self.button1.place(relx=0.78, rely=0.01, relwidth=0.1, relheight=0.03) 
        self.button2 = ttk.Button(self, text="Plot posterior density plots",
                           command= self.mcmc_output )
        self.button2.place(relx=0.78, rely=0.15, relwidth=0.1, relheight=0.03)
        self.button2a = ttk.Button(self, text="Get HPD intervals",
                           command= self.get_hpd_interval )
        self.button2a.place(relx=0.78, rely=0.19, relwidth=0.1, relheight=0.03)
        self.button3 = ttk.Button(self, text="Clear list",
                           command= self.clear_results_list )
        self.button3.place(relx=0.88, rely=0.15, relwidth=0.1, relheight=0.03)
        self.ResultList = [
            "Add to results list",
            "Get time elapsed", 
            ]
        self.variable = tk.StringVar(self.littlecanvas)
        self.variable.set("Add to results list")
        self.testmenu2 = ttk.OptionMenu(self.littlecanvas2, self.variable,self.ResultList[0], *self.ResultList, command = self.node_finder)
        
    def clear_results_list(self):
        self.results_list = []
        self.littlecanvas3.delete(self.results_text)
        self.canvas_plt.get_tk_widget().pack_forget()
        for item in self.tree_phases.get_children():
            self.tree_phases.delete(item)
        
    def node_finder(self, currentevent):
        self.testmenu2.place_forget()
        startpage = self.controller.get_page('StartPage')
        self.chronograph = startpage.chrono_dag
        print('chronograph_nodes')
        print(self.chronograph.nodes())
        x = str(self.chrono_nodes(currentevent))

        if self.variable.get() == 'Add to results list':
            self.littlecanvas3.delete(self.results_text)
            #ref = np.where(np.array(startpage.CONTEXT_NO) == x)[0][0]
            if x != 'no node':
                self.results_list.append(x)
                
        if len(self.phase_len_nodes) == 1:
            if self.variable.get() == "Get time elapsed between "+ str(self.phase_len_nodes[0]) + ' and another context':
                self.phase_len_nodes = np.append(self.phase_len_nodes, x)
                if self.canvas_plt != None:
                    self.canvas_plt.get_tk_widget().pack_forget()
                self.fig = Figure()
                LENGTHS = phase_length_finder(self.phase_len_nodes[0], self.phase_len_nodes[1], startpage.ALL_SAMPS_CONT, startpage.CONTEXT_NO, startpage.all_results_dict)
                plot1 = self.fig.add_subplot(111)
                plot1.hist(LENGTHS, bins='auto', color='#0504aa',
                            alpha=0.7, rwidth=0.85, density = True )
                plot1.title.set_text('Posterior density plot for time elapsed between ' + str(self.phase_len_nodes[0]) + ' and '+ str(self.phase_len_nodes[1]))
                interval = list(mcmc.HPD_interval(np.array(LENGTHS[1000:])))
                columns = ('context_1', 'context_2', 'hpd_interval')
                self.fig.set_tight_layout(True)
                self.canvas_plt = FigureCanvasTkAgg(self.fig,
                        master = self.littlecanvas)
                
                self.canvas_plt.get_tk_widget().pack()
                self.canvas_plt.draw_idle()
                #show hpd intervlls -----------
                self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show='headings')               
                # define headings
                self.tree_phases.heading('context_1', text='Context 1')
                self.tree_phases.heading('context_2', text='Context 2')
                self.tree_phases.heading('hpd_interval', text='HPD interval')
                intervals = []
                hpd_str = ""
                refs = [k for k in range(len(interval)) if k %2]
                for i in refs:
                    hpd_str = hpd_str + str(np.abs(interval[i-1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
                # add data to the treeview
                intervals.append((self.phase_len_nodes[0], self.phase_len_nodes[1], hpd_str))
                for contact in intervals:
                    self.tree_phases.insert('', tk.END, values=contact)
                self.tree_phases.grid(row=0, column=0, sticky='nsew')                
                # add a scrollbar
                scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
                self.tree_phases.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky='nsew')
            self.ResultList.remove("Get time elapsed between "+ str(self.phase_len_nodes[0]) + ' and another context')
            self.testmenu2 = ttk.OptionMenu(self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command = self.node_finder)
            self.phase_len_nodes = []
                
        if self.variable.get() == "Get time elapsed":
            if len(self.phase_len_nodes) == 1:
                self.ResultList.remove("Get time elapsed between "+ str(self.phase_len_nodes[0]) + ' and another context')
                self.testmenu2 = ttk.OptionMenu(self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command = self.node_finder)
                self.phase_len_nodes = []                    
            self.phase_len_nodes = np.append(self.phase_len_nodes, x)                
            self.ResultList.append("Get time elapsed between "+ str(self.phase_len_nodes[0]) + ' and another context')
            self.testmenu2 = ttk.OptionMenu(self.littlecanvas2, self.variable,self.ResultList[0], *self.ResultList, command = self.node_finder)
        self.results_text = self.littlecanvas3.create_text(100, 10, text = self.results_list)
        self.variable.set("Add to results list")

    def onRight(self, *args):
        '''makes test menu appear after right click '''
        self.littlecanvas2.unbind("Button-1>")
        self.littlecanvas2.bind("<Button-1>", self.onLeft)
        # Here we fetch our X and Y coordinates of the cursor RELATIVE to the window
        self.cursorx2 = int(self.littlecanvas2.winfo_pointerx() - self.littlecanvas2.winfo_rootx())
        self.cursory2 = int(self.littlecanvas2.winfo_pointery() - self.littlecanvas2.winfo_rooty())
    
        # Now we define our right click menu canvas
        # And here is where we use our X and Y variables, to place the menu where our cursor is,
        # That's how right click menus should be placed.           
        self.testmenu2.place(x=self.cursorx2, y=self.cursory2)
        # This is for packing our options onto the canvas, to prevent the canvas from resizing.
        # This is extremely useful if you split your program into multiple canvases or frames
        # and the pack method is forcing them to resize.
        self.testmenu2.pack_propagate(0)
        # Here is our label on the right click menu for deleting a row, notice the cursor
        # value, which will give us a pointy finger when you hover over the option.
        self.testmenu2.config(width=10)        
        # This function is for removing the canvas when an option is clicked.
  
    def preClick(self, *args):
        '''makes test menu appear and removes any previous test menu'''
        try:
            self.testmenu2.place_forget()
            self.onRight()
        except Exception:  
            self.onRight()

    # Hide menu when left clicking
    def onLeft(self, *args):
        '''hides menu when left clicking'''
        try:
            self.testmenu2.place_forget()
        except Exception:
            pass
        
    def mcmc_output(self):
        global mcmc_check
        startpage = self.controller.get_page('StartPage')
        if mcmc_check == 'mcmc_loaded':
          #  hpd_str = ""
           # columns = ('context', 'hpd_interval')
          #  self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show='headings') 
            if self.canvas_plt != None:
                    self.canvas_plt.get_tk_widget().pack_forget()
                    self.toolbar.destroy()
            fig = Figure(figsize = (5, 5),
                 dpi = 100)
         #   self.tree_phases.heading('context', text='Context')
        #    self.tree_phases.heading('hpd_interval', text='HPD interval')
           # intervals = []
            for i,j  in enumerate(self.results_list):
                plt.rcParams['text.usetex']
                plot_index = int(str(51) + str(i+1))
                plot1 = fig.add_subplot(plot_index)
                plot1.hist(startpage.resultsdict[j], bins='auto', color='#0504aa',
                            alpha=0.7, rwidth=0.85, density = True )
                fig.gca().invert_xaxis()
                plot1.set_xlim(startpage.A, startpage.P)
                node = str(j)
                if 'a' in node:
                    node = node.replace('a_', r'\alpha_{')
                if 'b' in node:
                    node  = node.replace('b_', r'\beta_{')
                if '=' in node:
                    node = node.replace('=', '} = ') 
                plot1.title.set_text(r"Posterior density plot for context " +  r"$" + node + "}$")
                
                              
              #  interval = list(mcmc.HPD_interval(np.array(startpage.resultsdict[j][1000:])))
            # define headings
              #  hpd_str = ""
             #   refs = [k for k in range(len(interval)) if k %2]
            #    for i in refs:
           #         hpd_str = hpd_str + str(np.abs(interval[i-1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
                # add data to the treeview
           #     intervals.append((node, hpd_str))

            
          #  for contact in intervals:
         #       self.tree_phases.insert('', tk.END, values=contact)
        #    self.tree_phases.grid(row=0, column=0, sticky='nsew')                
            # add a scrollbar
       #     scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
       #     self.tree_phases.configure(yscroll=scrollbar.set)
       #     scrollbar.grid(row=0, column=1, sticky='nsew')
       #     self.littlecanvas_a.create_text(150, 80, text = hpd_str)

            fig.set_tight_layout(True)
            self.canvas_plt = FigureCanvasTkAgg(fig,
                               master = self.littlecanvas)  
            self.canvas_plt.draw()
           # self.canvas_plt.get_tk_widget().pack()
  
    # creating the Matplotlib toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas_plt,
                                          self.littlecanvas)#
            self.toolbar.update()#
            self.canvas_plt.get_tk_widget().pack()
            
    def get_hpd_interval(self):
        global mcmc_check
        startpage = self.controller.get_page('StartPage')
        USER_INP = simpledialog.askstring(title="HPD interval percentage",
                                  prompt="Please input HPD interval percentage. Note, 95% is used as standard \n \n Percentage:")

        self.lim = np.float(USER_INP)/100
        if mcmc_check == 'mcmc_loaded':
            hpd_str = ""
            columns = ('context', 'hpd_interval')
            self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show='headings') 
            self.tree_phases.heading('context', text='Context')
            self.tree_phases.heading('hpd_interval', text=str(USER_INP) + '% HPD interval')
            intervals = []
            for i,j  in enumerate(list(set(self.results_list))):
                node = str(j)             
                interval = list(mcmc.HPD_interval(np.array(startpage.resultsdict[j][1000:]), lim = self.lim))
            # define headings
                hpd_str = ""
                refs = [k for k in range(len(interval)) if k %2]
                for i in refs:
                    hpd_str = hpd_str + str(np.abs(interval[i-1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
                # add data to the treeview
                intervals.append((node, hpd_str)) 
            for contact in intervals:
                self.tree_phases.insert('', tk.END, values=contact)
            self.tree_phases.grid(row=0, column=0, sticky='nsew')                
            # add a scrollbar
            scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
            self.tree_phases.configure(yscroll=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky='nsew')
            self.littlecanvas_a.create_text(150, 80, text = hpd_str)
            
    def chronograph_render_post(self):
        global load_check
        if load_check == 'loaded':
            self.image2 = imgrender2(load_check)
            self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
            self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw",
                                                                  image=self.littlecanvas2.img)
    
            self.width2, self.height2 = self.image2.size
            self.imscale2 = 1.0  # scale for the canvaas image
            self.delta2 = 1.1  # zoom magnitude
                # Put image into container rectangle and use it to set proper coordinates to the image
            self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
            
    def tkraise(self, aboveThis=None):
        self.chronograph_render_post() 
        super().tkraise(aboveThis)  
        
    def move_from2(self, event):
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image2 != "noimage":
            self.littlecanvas2.scan_mark(event.x, event.y)

    def move_to2(self, event):
        """Drag (move) canvas to the new position"""        
        if self.image2 != "noimage":
            self.littlecanvas2.scan_dragto(event.x, event.y, gain=1)
            self.show_image2()
            
            
    def wheel2(self, event):
        """Zoom with mouse wheel"""
        x_zoom = self.littlecanvas2.canvasx(event.x)
        y_zoom = self.littlecanvas2.canvasy(event.y)
        bbox = self.littlecanvas2.bbox(self.container2)  # get image area 
        if bbox[0] < x_zoom < bbox[2] and bbox[1] < y_zoom < bbox[3]:
            pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale2 = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width2, self.height2)
            if int(i * self.imscale2) < 30:
                return  # image is less than 30 pixels
            self.imscale2 /= self.delta2
            scale2 /= self.delta2
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.littlecanvas2.winfo_width(), self.littlecanvas2.winfo_height())
            if i < self.imscale2:
                return  # 1 pixel is bigger than the visible area
            self.imscale2 *= self.delta2
            scale2 *= self.delta2  
        self.littlecanvas2.scale('all', 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def show_image2(self):
        """Show image on the Canvas"""
        bbox1 = [0, 0, int(self.image2.size[0]*self.imscale2), int(self.image2.size[1]*self.imscale2)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.littlecanvas2.canvasx(0),  # get visible area of the canvas
                 self.littlecanvas2.canvasy(0),
                 self.littlecanvas2.canvasx(self.littlecanvas2.winfo_width()),
                 self.littlecanvas2.canvasy(self.littlecanvas2.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        bbox1 = [0, 0, int(self.image2.size[0]*self.imscale2), int(self.image2.size[1]*self.imscale2)]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.littlecanvas2.configure(scrollregion=bbox)  # set scroll region
        x_1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y_1 = max(bbox2[1] - bbox1[1], 0)
        x_2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y_2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x_2 - x_1) > 0 and int(y_2 - y_1) > 0:  # show image if it in the visible area
            x_img = min(int(x_2 / self.imscale2), self.width2)   # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale2), self.height2)  # ...and sometimes not
            image2 = self.image2.crop((int(x_1 / self.imscale2), int(y_1 / self.imscale2),
                                     x_img, y_img))
            self.imagetk2 = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.littlecanvas2.delete(self.littlecanvas2_img)
            self.imageid2 = self.littlecanvas2.create_image(max(bbox2[0], bbox1[0]),
                                                          max(bbox2[1], bbox1[1]), anchor='nw',
                                                          image=self.imagetk2)
            self.transx2, self.transy2 = bbox2[0], bbox2[1]
            self.littlecanvas.imagetk2 = self.imagetk2 
            
    def nodecheck(self, x_current, y_current):
        global node_df
        """ returns the node that corresponds to the mouse cooridinates"""
        node_inside = "no node"
        node_df_con = node_coords_fromjson(self.chronograph)
        node_df = node_df_con[0]
        xmax, ymax = node_df_con[1]
        #forms a dataframe from the dicitonary of coords    
        x, y = self.image2.size 
        cavx = x*self.imscale2
        cany = y*self.imscale2
        xscale = (x_current)*(xmax)/cavx
        yscale = (cany-y_current)*(ymax)/cany
        outline = nx.get_node_attributes(self.chronograph, 'color')
        for n_ind in range(node_df.shape[0]):
            if ((node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and
                    (node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper)):
                node_inside = node_df.iloc[n_ind].name
                outline[node_inside] = 'red'
                nx.set_node_attributes(self.chronograph, outline, 'color')  
        return node_inside

    def chrono_nodes(self, current):
        x_scal = self.cursorx2 + self.transx2
        y_scal = self.cursory2 + self.transy2
        node = self.nodecheck(x_scal, y_scal)
        return(node)
        
class PageTwo(object):
    def __init__(self, master, controller):
        self.top=tk.Toplevel(controller)
        self.top.geometry("1000x1000")
        self.intru_list = []
        self.resid_list = []
        self.controller = controller
        self.h_1 = 0
        self.w_1 = 0
        self.transx2 = 0
        self.transy2 = 0
        self.modevariable = None
        self.meta1 = ""
        self.metatext = ""
        self.rad_sel = ""
        self.mode = ""
        ##### intial values for all the functions
        self.delnodes = []
        self.edge_nodes = []
        self.comb_nodes = []
        self.edges_del = []
        self.temp = []
        self.results_list = []
        self.x_1 = 1
        self.image = "noimage"
        self.phase_rels = None
       # self.graphcopy = None
        self.imscale2 = 1.0  # scale for the canvaas image
        self.delta2 = 1.1 
        self.results_text = None
        self.canvas_plt = None
        self.phase_len_nodes = []
        self.canvas = tk.Canvas(self.top, bd=0, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        startpage = self.controller.get_page('StartPage')
        self.graphcanvas = tk.Canvas(self.canvas, bd=0, bg = 'white',
                                      selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.graphcanvas.place(relx=0.02, rely=0.05, relwidth=0.35, relheight=0.9)
        
        
        
        label = tk.Message(self.top, bg = 'white', font = ('Courier New', '14', 'bold'), text='Using this page: \n\n Please click on the buttons below to set into residual or intrusive mode. Then double right click on any context to set as residual/intrusive. \n\n Note that orange boxes denote intrusive contexts and blue boxes denote residual contexts. \n\n If you have clicked on a context by mistake, double right click to remove any label attributed to the context.')
        label.place(relx=0.4, rely=0.05)
        label2 = tk.Label(self.canvas, bg = 'white', font = ('Courier New', '14', 'bold'), text='Residual Contexts')
        label2.place(relx=0.4, rely=0.4)
        self.residcanvas = tk.Canvas(self.canvas, bd=0, bg = 'white',
                                      selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.residcanvas.place(relx=0.4, rely=0.42, relwidth=0.35, relheight=0.08)
        self.intrucanvas = tk.Canvas(self.canvas, bd=0, bg = 'white',
                                      selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.intrucanvas.place(relx=0.4, rely=0.54, relwidth=0.35, relheight=0.08)
        
        self.resid_label = tk.Label(self.residcanvas, text = self.resid_list, bg = 'white')
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        scroll_bar1 = ttk.Scrollbar(self.residcanvas)
        scroll_bar1.pack(side=tk.RIGHT)
        self.intru_label = tk.Label(self.intrucanvas, text = self.intru_list, bg = 'white')
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        scroll_bar2 = ttk.Scrollbar(self.intrucanvas)
        scroll_bar2.pack(side=tk.RIGHT)
        
        # Insert text into the text widget
    #    text_widget1.insert('1.0', self.intru_list)
        label3 = tk.Label(self.canvas, bg = 'white', font = ('Courier New', '14', 'bold'), text='Intrusive Contexts')
        label3.place(relx=0.4, rely=0.52)
        if startpage.graph != None:
            self.graphcopy = self.load_graph()
            self.show_image2()
        self.graphcanvas.update()
        button = tk.Button(self.top, text="Proceed",
                           command=lambda: self.popup4_wrapper(controller))
        
        button1 = tk.Button(self.top, text="Residual mode",
                           command=lambda: self.mode_set('resid'))
        button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
        button3 = tk.Button(self.top, text="Intrusive mode",
                           command=lambda: self.mode_set('intru'))
        button.place(relx=0.48, rely=0.65, relwidth=0.09, relheight=0.03)
        button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)

        self.graphcanvas.bind("<MouseWheel>", self.wheel2)
        self.graphcanvas.bind('<Button-4>', self.wheel2)# only with Linux, wheel scroll down
        self.graphcanvas.bind('<Button-5>', self.wheel2)
        self.graphcanvas.bind('<Double-Button-3>', self.resid_node_click)
        self.graphcanvas.bind('<Button-1>', self.move_from2)
        self.graphcanvas.bind('<B1-Motion>', self.move_to2)
        master.wait_window(self.top)
        
        #placing image on littlecanvas from graph
    def popup4_wrapper(self, controller):
        self.popup4 = popupWindow4(self, controller, self.resid_list, self.intru_list, self.node_del_tracker, self.graphcopy)
        self.top.destroy()

    def mode_set(self, var_set):
        self.modevariable = var_set
        if var_set == 'resid':
            button1 = tk.Button(self.top, text="Residual mode",
                           command=lambda: self.mode_set('resid'), background = 'orange')
            button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
            button3 = tk.Button(self.top, text="Intrusive mode",
                           command=lambda: self.mode_set('intru'))
            button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)
        if var_set == 'intru':
            button1 = tk.Button(self.top, text="Residual mode",
                           command=lambda: self.mode_set('resid'))
            button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
            button3 = tk.Button(self.top, text="Intrusive mode",
                           command=lambda: self.mode_set('intru'), background = 'lightgreen')
            button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)
        
    def tkraise(self, aboveThis=None):
        self.load_graph()
        super().tkraise(aboveThis) 
        
        
    def load_graph(self):
            startpage = self.controller.get_page('StartPage')  
            self.graphcopy = copy.deepcopy(startpage.graph)
            datadict = nx.get_node_attributes(self.graphcopy, 'Date')
            nodes = self.graphcopy.nodes()
            self.node_del_tracker = []
            for i in nodes:
                if datadict[i] == [None, None]:
                    self.node_del_tracker.append(i)
            color = (nx.get_node_attributes(self.graphcopy, 'color'))
            fill = (nx.get_node_attributes(self.graphcopy, 'fontcolor'))
            for j in self.node_del_tracker:
                color[j] = 'gray'
                fill[j] = 'gray'
                
            nx.set_node_attributes(self.graphcopy, color, 'color')
            nx.set_node_attributes(self.graphcopy, fill, 'fontcolor')
            if phase_true == 1:
                    self.image = imgrender_phase(self.graphcopy)
            else:
                self.image = imgrender(self.graphcopy)
            self.icon = ImageTk.PhotoImage(self.image)
            self.graphcanvas_img = self.graphcanvas.create_image(0, 0, anchor="nw",
                                                                   image=self.icon)
            self.width2, self.height2 = self.image.size
            self.imscale2 = 1.0  # scale for the canvaas image
            self.delta2 = 1.1  # zoom magnitude
            startpage.update_idletasks() 
            self.container = self.graphcanvas.create_rectangle(0, 0, self.width2, self.height2, width=0)
            return self.graphcopy
            

    def move_from2(self, event):
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image != "noimage":
            self.graphcanvas.scan_mark(event.x, event.y)

    def move_to2(self, event):
        """Drag (move) canvas to the new position"""        
        if self.image != "noimage":
            self.graphcanvas.scan_dragto(event.x, event.y, gain=1)
            self.show_image2()
            
            
    def wheel2(self, event):
        """Zoom with mouse wheel"""
        x_zoom = self.graphcanvas.canvasx(event.x)
        y_zoom = self.graphcanvas.canvasy(event.y)
        bbox = self.graphcanvas.bbox(self.container)  # get image area 
        if bbox[0] < x_zoom < bbox[2] and bbox[1] < y_zoom < bbox[3]:
            pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale2 = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width2, self.height2)
            if int(i * self.imscale2) < 30:
                return  # image is less than 30 pixels
            self.imscale2 /= self.delta2
            scale2 /= self.delta2
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height())
            if i < self.imscale2:
                return  # 1 pixel is bigger than the visible area
            self.imscale2 *= self.delta2
            scale2 *= self.delta2  
        self.graphcanvas.scale('all', 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def show_image2(self):
        """Show image on the Canvas"""
        startpage = self.controller.get_page('StartPage')
        startpage.update_idletasks()
        bbox1 = [0, 0, int(self.image.size[0]*self.imscale2), int(self.image.size[1]*self.imscale2)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.graphcanvas.canvasx(0),  # get visible area of the canvas
                 self.graphcanvas.canvasy(0),
                 self.graphcanvas.canvasx(self.graphcanvas.winfo_width()),
                 self.graphcanvas.canvasy(self.graphcanvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        bbox1 = [0, 0, int(self.image.size[0]*self.imscale2), int(self.image.size[1]*self.imscale2)]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.graphcanvas.configure(scrollregion=bbox)  # set scroll region
        x_1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y_1 = max(bbox2[1] - bbox1[1], 0)
        x_2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y_2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        
        if int(x_2 - x_1) > 0 and int(y_2 - y_1) > 0:  # show image if it in the visible area            
            x_img = min(int(x_2 / self.imscale2), self.width2)   # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale2), self.height2)  # ...and sometimes not
            image2 = self.image.crop((int(x_1 / self.imscale2), int(y_1 / self.imscale2),
                                     x_img, y_img)) 
            self.graphcanvas.delete(self.icon)
            self.icon = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.imageid2 = self.graphcanvas.create_image(max(bbox2[0], bbox1[0]),
                                                          max(bbox2[1], bbox1[1]), anchor='nw',
                                                          image=self.icon)
            self.transx2, self.transy2 = bbox2[0], bbox2[1]
        
            
    def nodecheck(self, x_current, y_current):
        global node_df
        startpage = self.controller.get_page('StartPage')
        startpage.update_idletasks()
        """ returns the node that corresponds to the mouse cooridinates"""
        node_inside = "no node"
        if self.graphcopy != None:
            node_df_con = node_coords_fromjson(self.graphcopy)
            node_df = node_df_con[0]
            xmax, ymax = node_df_con[1]
            #forms a dataframe from the dicitonary of coords    
            x, y = self.image.size 
            cavx = x*self.imscale2
            cany = y*self.imscale2
            xscale = (x_current)*(xmax)/cavx
            yscale = (cany-y_current)*(ymax)/cany
            outline = nx.get_node_attributes(self.graphcopy, 'color')
            for n_ind in range(node_df.shape[0]):
                if ((node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and
                        (node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper)):
                    node_inside = node_df.iloc[n_ind].name
                    nx.set_node_attributes(self.graphcopy, outline, 'color')  
        return node_inside

    def resid_node_click(self, event):   
        startpage = self.controller.get_page('StartPage')
        startpage.update_idletasks()
        self.cursorx2 = int(self.graphcanvas.winfo_pointerx() - self.graphcanvas.winfo_rootx())
        self.cursory2 = int(self.graphcanvas.winfo_pointery() - self.graphcanvas.winfo_rooty())
        x_scal = self.cursorx2 + self.transx2
        y_scal = self.cursory2 + self.transy2
        node = self.nodecheck(x_scal, y_scal)
        outline = nx.get_node_attributes(self.graphcopy, 'color')
        if ((node in self.resid_list) == True) and (self.modevariable != 'intru'):
            self.resid_list.remove(node)
            outline[node] = 'black' 
        elif ((node in self.resid_list) == True) and (self.modevariable == 'intru'):
            self.resid_list.remove(node)
            outline[node] = 'green'
            self.intru_list.append(node)
        elif ((node in self.intru_list) == True) and (self.modevariable != 'resid') :
            self.intru_list.remove(node)
            outline[node] = 'black'
        elif ((node in self.intru_list) == True) and (self.modevariable == 'resid') :
            self.intru_list.remove(node)
            self.resid_list.append(node)
            outline[node] = 'orange' 
        elif (self.modevariable == 'resid') and ((node in self.resid_list) == False):
            self.resid_list.append(node)
            outline[node] = 'orange'          
        elif self.modevariable == 'intru'and ((node in self.intru_list) == False):
            self.intru_list.append(node)
            outline[node] = 'green'

        self.resid_label = tk.Label(self.residcanvas, text = str(self.resid_list).replace("'", "")[1:-1], bg = 'white')
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.intru_label = tk.Label(self.intrucanvas, text = str(self.intru_list).replace("'", "")[1:-1], bg = 'white')
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        scroll_bar1 = ttk.Scrollbar(self.residcanvas)
        scroll_bar1.pack(side=tk.RIGHT)
        scroll_bar2 = ttk.Scrollbar(self.intrucanvas)
        scroll_bar2.pack(side=tk.RIGHT)
        nx.set_node_attributes(self.graphcopy, outline, 'color') 
        if phase_true == 1:
            imgrender_phase(self.graphcopy)
        else:
            imgrender(self.graphcopy) 
        self.image = Image.open('testdag.png')
        self.width2, self.height2 = self.image.size
        self.container = self.graphcanvas.create_rectangle(0, 0, self.width2, self.height2, width=0)
        self.show_image2()
        return(node)
            
            
MAIN_FRAME = MainFrame() 

style = ThemedStyle(MAIN_FRAME)
style.set_theme("breeze") 
MAIN_FRAME.geometry("2000x1000")
MAIN_FRAME.mainloop()