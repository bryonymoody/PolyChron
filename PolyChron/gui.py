#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 17:43:25 2021

@author: bryony
"""

import os
import pathlib
import tkinter as tk
from tkinter import ttk
import copy
import re
import ast
import matplotlib as plt
from PIL import Image, ImageTk, ImageChops
from networkx.drawing.nx_pydot import read_dot, write_dot
import networkx as nx
import pydot
import numpy as np
import pandas as pd
from tkinter.filedialog import askopenfile
from graphviz import render
import PolyChron.automated_mcmc_ordering_coupling_copy as mcmc
from ttkthemes import ThemedStyle
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pickle
from tkinter import simpledialog
import tkinter.font as tkFont
from tkinter.messagebox import askquestion
import csv

# Currently unused dependencies
# import svgutils.transform as sg
# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPDF, renderPM
# from svglib.svglib import svg2rlg
# import cairosvg
from importlib.metadata import version  # requires python >= 3.8
import argparse

# Get the absolute path to a directory in the users home dir
POLYCHRON_PROJECTS_DIR = (pathlib.Path.home() / "Documents/Pythonapp_tests/projects").resolve()
# Ensure the directory exists (this is a little aggressive)
POLYCHRON_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
# Change into the projects dir
os.chdir(POLYCHRON_PROJECTS_DIR)
old_stdout = sys.stdout


class StdoutRedirector(object):
    def __init__(self, text_area, pb1):
        """allows us to rimedirect
        output to the app canvases"""
        self.text_area = text_area
        self.pb1 = pb1

    def write(self, str):
        """writes to canvas"""
        #     self.text_area.update_idletasks()
        self.pb1.update_idletasks
        # self.text_area.destroy()
        str1 = re.findall(r"\d+", str)
        if len(str1) != 0:
            self.text_area["text"] = str1[0] + "% complete"
            self.pb1["value"] = int(str1[0])
            self.text_area.update_idletasks()
        #  self.text_area.see(1.0)

    def flush(self):
        pass


# global variables
phase_true = 0
load_check = "not_loaded"
mcmc_check = "mcmc_notloaded"
proj_dir = ""
SCRIPT_DIR = pathlib.Path(__file__).parent  # Path to directory containing this script
CALIBRATION = pd.read_csv(SCRIPT_DIR / "linear_interpolation.txt")


def trim(im_trim):
    """Trims images down"""
    bg_trim = Image.new(im_trim.mode, im_trim.size)
    diff = ImageChops.difference(im_trim, bg_trim)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    return im_trim.crop(bbox)


def clear_all(tree):
    for item in tree.get_children():
        tree.delete(item)


def node_del_fixed(graph, node):
    in_nodes = [i[0] for i in list(graph.in_edges(node))]
    out_nodes = [i[1] for i in list(graph.out_edges(node))]
    graph.remove_node(node)
    for i in in_nodes:
        for j in out_nodes:
            graph.add_edge(i, j, arrowhead="none")

    graph_check = nx.transitive_reduction(graph)
    if graph.edges() != graph_check.edges():
        edges1 = list(graph.edges()).copy()
        for k in edges1:
            if k not in graph_check.edges():
                graph.remove_edge(k[0], k[1])
    return graph


def polygonfunc(i):
    """finds node coords of a kite"""
    x = re.findall(r'points="(.*?)"', i)[0].replace(" ", ",")
    a = x.split(",")
    # if loop checks if it's a rectangle or a kite then gets the right coords
    if -1 * float(a[7]) == -1 * float(a[3]):
        coords_converted = [float(a[2]), float(a[6]), -1 * float(a[5]), -1 * float(a[1])]
    else:
        coords_converted = [float(a[2]), float(a[6]), -1 * float(a[7]), -1 * float(a[3])]
    return coords_converted


def ellipsefunc(i):
    """finds coords from dot file for ellipse nodes"""
    x = re.findall(r"cx=(.*?)/>", i)[0].replace(" ", ",")
    x = x.replace("cy=", "").replace("rx=", "").replace("ry=", "").replace('"', "")
    a = x.split(",")
    coords_converted = [
        float(a[0]) - float(a[2]),
        float(a[0]) + float(a[2]),
        -1 * float(a[1]) - float(a[3]),
        -1 * float(a[1]) + float(a[3]),
    ]
    return coords_converted


def node_coords_fromjson(graph):
    """Gets coordinates of each node"""
    global phase_true
    if "pydot" in str(type(graph)):
        graphs = graph
    else:
        graphs = nx.nx_pydot.to_pydot(graph)
    svg_string = str(graphs.create_svg())
    scale_info = re.search("points=(.*?)/>", svg_string).group(1).replace(" ", ",")
    scale_info = scale_info.split(",")
    scale = [float(scale_info[4]), -1 * float(scale_info[3])]
    coords_x = re.findall(r'id="node(.*?)</text>', svg_string)
    coords_temp = [polygonfunc(i) if "points" in i else ellipsefunc(i) for i in coords_x]
    node_test = re.findall(r'node">\\n<title>(.*?)</title>', svg_string)
    node_list = [i.replace("&#45;", "-") for i in node_test]

    new_pos = dict(zip(node_list, coords_temp))
    df = pd.DataFrame.from_dict(new_pos, orient="index", columns=["x_lower", "x_upper", "y_lower", "y_upper"])
    return df, scale


def all_node_info(node_list, x_image, node_info):
    """obtains node attributes from original dot file"""
    for i in node_list:
        for j in x_image:
            b_string = re.search('"(.*)" ', j)
            if b_string is not None:
                if i == b_string.group(1):
                    if i in j and "->" not in j:
                        tset = j[(j.index("[") + 1) : (len(j) - 1)]
                        atr_new = tset.replace("] [", "','")
                        atr_new = atr_new.replace("=", "':' ")
                        atr_new = atr_new.replace("' \"", '"')
                        atr_new = atr_new.replace("\"'", '"')
                        atr_new = atr_new.replace("' ", "'")
                        atr_newer = str("{'" + atr_new + "}")
                        dicc = ast.literal_eval(atr_newer)
                        node_info.append(dicc)
    return node_info


def phase_length_finder(con_1, con_2, resultsdict):
    """finding the phase length between any two contexts or phase boundaries"""
    phase_lengths = []
    x_3 = resultsdict[con_1]
    x_4 = resultsdict[con_2]
    for i in range(len(x_3)):
        phase_lengths.append(np.abs(x_3[i] - x_4[i]))
    un_phase_lens = []
    for i in range(len(phase_lengths) - 1):
        if phase_lengths[i] != phase_lengths[i + 1]:
            un_phase_lens.append(phase_lengths[i])
    return phase_lengths


def imagefunc(dotfile):
    """Sets note attributes to a dot string"""
    file = read_dot(dotfile)
    ####code to get colours####
    f_string = open(str(dotfile), "r")
    dotstr = f_string.read()
    dotstr = dotstr.replace(";<", "@<")
    dotstr = dotstr.replace("14.0", "50.0")
    # change any ';>' to '@>' then back again after
    x_image = dotstr.rsplit(";")
    for i in enumerate(x_image):
        x_image[i[0]] = x_image[i[0]].replace("@<", ";<")
    node_list = list(file.nodes)
    node_info_init = list()
    node_info = all_node_info(node_list, x_image, node_info_init)
    for k in enumerate(node_list):
        node_info[k[0]].update(
            {"Determination": "None", "Find_Type": "None", "Group": node_info[k[0]]["fillcolor"], "color": "black"}
        )
    individ_attrs = zip(node_list, node_info)
    attrs = dict(individ_attrs)  # add the dictionary of attributed to a node
    nx.set_node_attributes(file, attrs)
    return file


def phase_relabel(graph):
    """relabels the phase labels to be alphas and betas, for display only,
    still refer to them with a's and b's"""
    label_dict = {}
    for i in graph.nodes():
        if "a_" in i:
            if "b_" in i:
                label_str = i.replace("a_", "<&alpha;<SUB>")
                label_str = label_str.replace(" = b_", "</SUB> = &beta;<SUB>") + "</SUB>>"
                label_dict[i] = label_str
            else:
                label_str = i.replace("a_", "<&alpha;<SUB> ") + "</SUB>>"
                label_dict[i] = label_str
        elif ("b_" in i) and ("a_" not in i):
            label_str = i.replace("b_", "<&beta;<SUB>") + "</SUB>>"
            label_dict[i] = label_str
    # sets the new phase labels to the node attribute labels
    nx.set_node_attributes(graph, label_dict, "label")
    return graph


def chrono_edge_remov(file_graph):
    """removes any excess edges so we can render the chronograph"""
    xs, ys = [], []
    # gets a list of all the edges and splits into above and below
    for x, y in list(file_graph.edges):
        xs.append(x)
        ys.append(y)
    graph_data = phase_info_func(file_graph)
    phase_list = list(graph_data[1][2])
    phase_dic = graph_data[3]
    # case with more than one phase
    if len(phase_list) != 1:
        if len(graph_data[1][3]) == 0:
            file_graph.add_edge(phase_dic[phase_list[0]][0], phase_dic[phase_list[1]][0], arrowhead="none")
            graph_data = phase_info_func(file_graph)
        x_l, y_l = graph_data[2][0], graph_data[2][1]
        evenlist, oddlist, elist, olist = [], [], [], []
        for i in range(len(x_l)):
            if i % 2 == 0:
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
            file_graph.add_edge("b_" + str(j), evenlist[i], arrowhead="none")
        for i, j in enumerate(olist):
            file_graph.add_edge(oddlist[i], "a_" + str(j.replace("_below", "")), arrowhead="none")
    # case when there's only one phase
    elif len(phase_list) == 1:
        evenlist = []
        oddlist = []
        for nd in graph_data[1][1]:
            if len(list(file_graph.predecessors(nd))) == 0:
                evenlist.append(nd)  # if no predecesors, adds to list for nodes to connect to phase boundary
            if len(list(file_graph.edges(nd))) == 0:
                oddlist.append(nd)
        for node in list(phase_list):
            alp_beta_node_add(node, file_graph)
        for node in list(phase_list):
            alp_beta_node_add(node, file_graph)
        phase_lab = phase_list[0]
        for z in evenlist:
            file_graph.add_edge("b_" + str(phase_lab), z, arrowhead="none")

        for m in oddlist:
            file_graph.add_edge(m, "a_" + str(phase_lab), arrowhead="none")
    # graph data gives 1) phases in a dict and nodes at the edge of that phase,
    # 2) phases for each context, 3) contexts, 4) phases in "below form",
    # 5)dictionary of phases and contexts in them
    # xs, ys gives any edges removed becuase phase boundaries need to go in
    # list of phases
    return graph_data, [xs, ys], phase_list


def phase_labels(phi_ref, POST_PHASE, phi_accept, all_samps_phi):
    """provides phase limits for a phase"""
    labels = ["a_" + str(phi_ref[0])]
    i = 0
    results_dict = {labels[0]: phi_accept[i]}
    all_results_dict = {labels[0]: all_samps_phi[i]}
    for a_val in enumerate(POST_PHASE):
        i = i + 1
        if a_val[1] == "abutting":
            labels.append("b_" + str(phi_ref[a_val[0]]) + " = a_" + str(phi_ref[a_val[0] + 1]))
            results_dict["a_" + str(phi_ref[a_val[0] + 1]) + " = b_" + str(phi_ref[a_val[0]])] = phi_accept[i]
            all_results_dict["a_" + str(phi_ref[a_val[0] + 1]) + " = b_" + str(phi_ref[a_val[0]])] = all_samps_phi[i]
        # results_dict['a_' + str(phi_ref[a_val[0]+1])] = phi_accept[i]
        elif a_val[1] == "end":
            labels.append("b_" + str(phi_ref[-1]))
            results_dict["b_" + str(phi_ref[a_val[0]])] = phi_accept[i]
            all_results_dict["b_" + str(phi_ref[a_val[0]])] = all_samps_phi[i]
        elif a_val == "gap":
            labels.append("b_" + str(phi_ref[a_val[0]]))
            labels.append("a_" + str(phi_ref[a_val[0] + 1]))
            results_dict["b_" + str(phi_ref[a_val[0]])] = phi_accept[i]
            all_results_dict["b_" + str(phi_ref[a_val[0]])] = all_samps_phi[i]
            i = i + 1
            results_dict["a_" + str(phi_ref[a_val[0] + 1])] = phi_accept[i]
            all_results_dict["a_" + str(phi_ref[a_val[0] + 1])] = all_samps_phi[i]
        else:
            labels.append("a_" + str(phi_ref[a_val[0] + 1]))
            labels.append("b_" + str(phi_ref[a_val[0]]))
            results_dict["a_" + str(phi_ref[a_val[0] + 1])] = phi_accept[i]
            all_results_dict["a_" + str(phi_ref[a_val[0] + 1])] = all_samps_phi[i]
            i = i + 1
            results_dict["b_" + str(phi_ref[a_val[0]])] = phi_accept[i]
            all_results_dict["b_" + str(phi_ref[a_val[0]])] = all_samps_phi[i]
    # returns dictionary of results do we can plot probability density functions
    return labels, results_dict, all_results_dict


def del_empty_phases(phi_ref, del_phase, phasedict):
    """checks for any phase rels that need changing due to missing dates"""
    del_phase = [i for i in phi_ref if i in del_phase]
    del_phase_dict_1 = {}
    for j in del_phase:
        del_phase_dict = {}
        rels_list = [i for i in phasedict.keys() if j in i]
        for rels in rels_list:
            if rels[0] == j:
                del_phase_dict["lower"] = rels[1]
            if rels[1] == j:
                del_phase_dict["upper"] = rels[0]
        del_phase_dict_1[j] = del_phase_dict
    if phi_ref[-1] in del_phase_dict_1.keys():
        del_phase_dict_1[phi_ref[-1]]["upper"] = "end"
    if phi_ref[0] in del_phase_dict_1.keys():
        del_phase_dict_1[phi_ref[0]]["lower"] = "start"
    # We then have to run the loop again in case any phases are next to eachother, this checks that
    for j in del_phase:
        rels_list = [i for i in phasedict.keys() if j in i]
        for rels in rels_list:
            if rels[0] == j:
                if rels[1] in del_phase:
                    del_phase_dict_1[j]["lower"] = del_phase_dict_1[rels[1]]["lower"]
    del_phase.reverse()
    for k in del_phase:
        rels_list = [i for i in phasedict.keys() if k in i]
        for rels in rels_list:
            if rels[1] == k:
                if rels[0] in del_phase:
                    del_phase_dict_1[k]["upper"] = del_phase_dict_1[rels[0]]["upper"]
    new_phase_rels = [
        [del_phase_dict_1[l]["upper"], del_phase_dict_1[l]["lower"]]
        for l in del_phase_dict_1.keys()
        if del_phase_dict_1[l]["upper"] != "end"
        if del_phase_dict_1[l]["lower"] != "start"
    ]
    return new_phase_rels


def phase_rels_delete_empty(file_graph, new_phase_rels, p_list, phasedict, phase_nodes, graph_data):
    phase_relabel(file_graph)
    # adds edges between phases that had gaps due to no contexts being left in them
    label_dict = {}
    null_phases = []  # keep track of phases we need to delete
    [file_graph.add_edge("a_" + str(i[0]), "b_" + str(i[1]), arrowhead="none") for i in new_phase_rels]
    for p in p_list:
        relation = phasedict[p]
        if relation == "gap":
            if p[0] not in graph_data[1][2]:
                phasedict.pop[p]
                null_phases.append(p)
            elif p[1] not in graph_data[1][2]:
                null_phases.append(p)
            else:
                file_graph.add_edge("a_" + str(p[0]), "b_" + str(p[1]), arrowhead="none")
        if relation == "overlap":
            if p[0] not in graph_data[1][2]:
                null_phases.append(p)
            elif p[1] not in graph_data[1][2]:
                null_phases.append(p)
            else:
                file_graph.add_edge("b_" + str(p[1]), "a_" + str(p[0]), arrowhead="none")
        if relation == "abutting":
            if p[0] not in graph_data[1][2]:
                null_phases.append(p)
            elif p[1] not in graph_data[1][2]:
                null_phases.append(p)
            else:
                file_graph = nx.contracted_nodes(file_graph, "a_" + str(p[0]), "b_" + str(p[1]))
                x_nod = list(file_graph)
                newnode = str("a_" + str(p[0]) + " = " + "b_" + str(p[1]))
                label_str = "<&alpha;<SUB>" + str(p[0]) + "</SUB> = &beta;<SUB>" + str(p[1]) + "</SUB>>"
                label_dict[newnode] = label_str
                phase_nodes.append("a_" + str(p[0]) + " = " + "b_" + str(p[1]))
                y_nod = [newnode if i == "a_" + str(p[0]) else i for i in x_nod]
                mapping = dict(zip(x_nod, y_nod))
                file_graph = nx.relabel_nodes(file_graph, mapping)
    return file_graph, null_phases, label_dict


def chrono_edge_add(file_graph, graph_data, xs_ys, phasedict, phase_trck, post_dict, prev_dict):
    xs = xs_ys[0]
    ys = xs_ys[1]
    phase_nodes = []
    phase_norm, node_list = graph_data[1][0], graph_data[1][1]
    all_node_phase = dict(zip(node_list, phase_norm))
    for i in node_list:  # loop adds edges between phases
        if i not in xs:
            if i not in ys:
                file_graph.add_edge("b_" + str(all_node_phase[i]), i, arrowhead="none")
                file_graph.add_edge(i, "a_" + str(all_node_phase[i]), arrowhead="none")
            else:
                file_graph.add_edge(i, "a_" + str(all_node_phase[i]), arrowhead="none")
        elif i in xs:
            if i not in ys:
                file_graph.add_edge("b_" + str(all_node_phase[i]), i, arrowhead="none")
    if phasedict is not None:
        p_list = list(set(phase_trck))  # phases before any get removed due to having no dates

        phase_nodes.append("a_" + str(p_list[0][0]))
        up_phase = [i[0] for i in p_list]
        low_phase = [i[1] for i in p_list]
        act_phases = set(up_phase + low_phase)  # actual phases we are working with
        del_phase = act_phases - set(graph_data[1][2])
        graph = nx.DiGraph(graph_attr={"splines": "ortho"})
        if len(phase_trck) != 0:
            graph.add_edges_from(phase_trck, arrows="none")
            phi_ref = list(reversed(list(nx.topological_sort(graph))))
            graph_temp = nx.transitive_reduction(graph)
            a = set(graph.edges())
            b = set(graph_temp.edges())
            if len(list(a - b)) != 0:
                rem = list(a - b)[0]
                file_graph.remove_edge(rem[0], rem[1])
        new_phase_rels = del_empty_phases(phi_ref, del_phase, phasedict)
        # changes diplay labels to alpha ans betas
        file_graph, null_phases, label_dict = phase_rels_delete_empty(
            file_graph, new_phase_rels, p_list, phasedict, phase_nodes, graph_data
        )

        phi_ref = [i for i in phi_ref if i in set(graph_data[1][2])]
        phase_nodes.append("b_" + str(p_list[len(p_list) - 1][0]))

    # replace phase rels with gap for phases adjoined due to missing phases
    for i in new_phase_rels:
        post_dict[i[1]] = "gap"
        prev_dict[i[0]] = "gap"
    nx.set_node_attributes(file_graph, label_dict, "label")
    return (file_graph, phi_ref, null_phases)


def imgrender(file, canv_width, canv_height):
    global node_df
    """renders png from dotfile"""
    file.graph["graph"] = {"splines": "ortho"}
    write_dot(file, "fi_new")
    ####code to get colours####
    #    f_string = open(str('fi_new'), "r")
    #   f = f_string.read()
    ##    f = f.replace('{', '{ splines = "ortho";', 1)
    #  g = pydot.graph_from_dot_data(f)
    # graph = g[0]
    #   graph.write_dot('fi_neww')
    render("dot", "png", "fi_new")
    render("dot", "svg", "fi_new")
    inp = Image.open("fi_new.png")
    inp_final = trim(inp)
    #  scale_factor = min(canv_width/inp.size[0], canv_height/inp.size[1])
    #    print(scale_factor)
    #   inp_final = inp.resize((int(inp.size[0]*scale_factor), int(inp.size[1]*scale_factor)), Image.ANTIALIAS)
    inp_final.save("testdag.png")
    outp = Image.open("testdag.png")
    node_df = node_coords_fromjson(file)
    #     str_size = "\"" + str(int((canv_height)/96))+ ","+str(int((canv_width)/96)) + "!" +"\""
    #     file.graph['graph']={'splines':'ortho', 'size' : str(2417/90)+ ","+str(2016/96)}#str_size}
    #     graph_check = nx.transitive_reduction(file)
    #     if file.edges() != graph_check.edges():
    #        edges1 = list(file).copy()
    #        for k in edges1:
    #            if k not in graph_check.edges():
    #                file(k[0], k[1])
    #     write_dot(file, 'fi_new')
    #     render('dot', 'png', 'fi_new')
    #     fig = sg.fromfile('fi_new.svg')
    #     img_size = fig.get_size()
    #     img_size = [int(i.replace("pt", "")) for i in img_size]
    #     scale_factor = min(canv_width/img_size[0], canv_height/img_size[1])
    #     fig.set_size((str(int((img_size[0]*scale_factor))), str(int((img_size[1]*scale_factor)*1))))
    #     fig.save('myimage2.svg')
    #     cairosvg.svg2png(url='myimage2.svg', write_to='testdag.png')
    # #
    #  #   write_dot(file, 'fi_new')
    #   #  render('dot', 'png', 'fi_new')
    #     outp = Image.open("fi_new.png")
    #     outp = trim(outp)
    #     node_df = node_coords_fromjson(file)
    return outp


def imgrender2(canv_width, canv_height):
    """renders png from dotfile"""
    global load_check, node_df
    if load_check == "loaded":
        render("dot", "png", "fi_new_chrono")
        render("dot", "svg", "fi_new_chrono")
        inp = Image.open("fi_new_chrono.png")
        inp_final = trim(inp)
        #     scale_factor = min(canv_width/inp.size[0], canv_height/inp.size[1])
        #     inp_final = inp.resize((int(inp.size[0]*scale_factor), int(inp.size[1]*scale_factor)), Image.ANTIALIAS)
        inp_final.save("testdag_chrono.png")
        outp = Image.open("testdag_chrono.png")
    else:
        outp = "No_image"
    return outp


def edge_of_phase(test1, pset, node_list, node_info):
    """find nodes on edge of each phase"""
    x_l = []
    y_l = []
    mydict = {}
    phase_tracker = []
    if FILE_INPUT is not None:
        for i in enumerate(pset):
            temp_nodes_list = []
            for j in enumerate(node_list):
                if node_info[j[0]]["fillcolor"] == pset[i[0]]:
                    temp_nodes_list.append(node_list[j[0]])
                    p_phase = str(pset[i[0]][pset[i[0]].rfind("/") + 1 : len(pset[i[0]])])
                    node_info[j[0]].update({"Group": p_phase})
                mydict[str(pset[i[0]][pset[i[0]].rfind("/") + 1 : len(pset[i[0]])])] = temp_nodes_list
    else:
        for i in enumerate(pset):
            temp_nodes_list = []
            for j in enumerate(node_list):
                if node_info[j[0]]["Group"] == pset[i[0]]:
                    temp_nodes_list.append(node_list[j[0]])
                mydict[pset[i[0]]] = temp_nodes_list
    for i in enumerate(test1):
        for key in mydict:
            if test1[i[0]][1] in mydict[key] and test1[i[0]][0] not in mydict[key]:
                x_l.append(test1[i[0]][1])
                y_l.append(key)
                phase_lst = [list(mydict.values()).index(j) for j in list(mydict.values()) if test1[i[0]][0] in j]
                key_1 = list(mydict.keys())[phase_lst[0]]  # trying to find phase of other value
                x_l.append(test1[i[0]][0])
                y_l.append(str(key_1 + "_below"))
                phase_tracker.append((key_1, key))
    return x_l, y_l, mydict.keys(), phase_tracker, mydict


def phase_info_func(file_graph):
    # t0 = time.time()
    """returns a dictionary of phases and nodes in each phase"""
    res = []
    node_list = list(file_graph.nodes)
    nd = dict(file_graph.nodes(data=True))
    node_info = [nd[i] for i in node_list]
    if FILE_INPUT is not None:
        phase = nx.get_node_attributes(file_graph, "fillcolor")
        phase_norm = [phase[ph][phase[ph].rfind("/") + 1 : len(phase[ph])] for ph in phase]
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
        phase1 = nx.get_node_attributes(file_graph, "Group")
        for key in phase1.keys():
            res.append(phase1[key])
        phase_norm = res
    x_l, y_l, phase_list, phase_trck, phase_dic = edge_of_phase(
        list(nx.line_graph(file_graph)), list(set(res)), node_list, node_info
    )
    reversed_dict = {}
    if len(phase_list) > 1:
        testdic = dict(zip(x_l, y_l))
        for key, value in testdic.items():
            reversed_dict.setdefault(value, [])
            reversed_dict[value].append(key)
    return reversed_dict, [phase_norm, node_list, phase_list, phase_trck], [x_l, y_l], phase_dic


def alp_beta_node_add(x, graph):
    """adds an alpha and beta node to node x"""
    graph.add_node("a_" + str(x), shape="diamond", fontsize="20.0", fontname="helvetica", penwidth="1.0")
    graph.add_node("b_" + str(x), shape="diamond", fontsize="20.0", fontname="helvetica", penwidth="1.0")


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
        x_2 = "{rank = same; " + y_5 + ";}\n"
        rank_same.append(x_2)
    rank_string = "".join(rank_same)[:-1]
    new_string = file_content[:-2] + rank_string + file_content[-2]
    return new_string


def imgrender_phase(file):
    global node_df
    #  t0 = time.time()
    """Renders image from dot file with all nodes of the same phase collected together"""
    write_dot(file, "fi_new.txt")
    my_file = open("fi_new.txt")
    file_content = my_file.read()
    new_string = rank_func(phase_info_func(file)[0], file_content)
    textfile = open("fi_new.txt", "w")
    textfile.write(new_string)
    textfile.close()
    (graph,) = pydot.graph_from_dot_file("fi_new.txt")
    graph.write_png("test.png")
    inp = Image.open("test.png")
    inp = trim(inp)
    # Call the real .tkraise
    inp.save("testdag.png")
    outp = Image.open("testdag.png")
    node_df = node_coords_fromjson(graph)
    return outp


class popupWindow(object):
    def __init__(self, master):
        """initialises popupWindow"""
        self.top = tk.Toplevel(master)
        self.top.configure(bg="#AEC7D6")
        self.top.geometry("1000x400")
        # pop up window to allow us to enter a context that we want to change the meta data for
        self.l = ttk.Label(self.top, text="Context Number")
        self.l.pack()
        self.e = ttk.Entry(self.top)  # allows us to keep t6rack of the number we've entered
        self.e.pack()
        self.b = ttk.Button(self.top, text="Ok", command=self.cleanup)  # gets ridof the popup
        self.b.pack()
        self.value = tk.StringVar(self.top)

    def cleanup(self):
        """destroys popupWindow"""
        self.value = self.e.get()
        self.top.destroy()


class popupWindow2(object):
    def __init__(self, master, graph, canvas):
        """initiliases popup2"""
        self.top = tk.Toplevel(master)
        self.top.title("Adding new supplementary data")
        self.top.configure(bg="#AEC7D6")
        self.top.geometry("1000x400")
        # this popup window lets us change the metadata after popupwindow has gone
        self.graph = graph
        self.canvas2 = tk.Canvas(self.top)
        self.canvas2.place(relx=0, rely=0, relwidth=1, relheight=1)
        #        #making node add section
        # defining variables to keep track of what is being updated in the meta data
        self.variable_a = tk.StringVar(self.top)
        self.variable_b = tk.StringVar(self.top)
        self.variable_c = tk.StringVar(self.top)
        self.variable_d = tk.StringVar(self.top)
        self.label4 = ttk.Label(self.canvas2)
        self.entry4 = ttk.Entry(self.canvas2)
        self.label5 = ttk.Label(self.canvas2)
        self.entry5 = ttk.Entry(self.canvas2)
        self.label6 = ttk.Label(self.canvas2)
        self.entry6 = ttk.Entry(self.canvas2)
        #        #entry box for adding metadata
        self.entry3 = ttk.Entry(self.canvas2)
        #  self.button3 = ttk.Button(self.top, text='Add Metadata to node', command=self.testcom())#need to add command
        self.label3 = ttk.Label(self.canvas2, text="Node")
        self.canvas2.create_window(40, 60, window=self.entry3, width=50)
        self.canvas2.create_window(40, 35, window=self.label3)
        # needs way more detail adding to this
        self.dict = {
            "Find Type": ["Find1", "Find2", "Find3"],
            "Determination": ["None", "Input date"],
            "Group": ["None", "Input Group"],
        }
        #       #defining variables to keep track of what is being updated in the meta data
        self.variable_a = tk.StringVar(self.top)
        self.variable_b = tk.StringVar(self.top)
        self.variable_c = tk.StringVar(self.top)
        self.variable_d = tk.StringVar(self.top)
        self.optionmenu_a = ttk.OptionMenu(self.top, self.variable_a, list(self.dict.keys())[0], *self.dict.keys())
        self.optionmenu_b = ttk.OptionMenu(self.top, self.variable_b, "None", "None")
        self.optionmenu_a.place(relx=0.3, rely=0.15)
        self.optionmenu_b.place(relx=0.6, rely=0.15)
        self.variable_a.trace("w", self.update_options)
        self.variable_b.trace("w", self.testdate_input)
        self.variable_c.trace("w", self.update_options)
        self.variable_d.trace("w", self.update_options)
        self.variable_a.set("Determination")

    #   self.button3.place(relx=0.1, rely=0.7)

    def testdate_input(self):
        """formats the windows so that they have the right inputs depending of if it's a date or a phase"""
        if self.variable_b.get() == "Input date":
            self.label4 = ttk.Label(self.canvas2, text="Radiocarbon Date")
            self.entry4 = ttk.Entry(self.canvas2)
            self.canvas2.create_window(90, 130, window=self.entry4, width=50)
            self.canvas2.create_window(90, 90, window=self.label4)
            self.label5 = ttk.Label(self.canvas2, text="Error")
            self.entry5 = ttk.Entry(self.canvas2)
            self.canvas2.create_window(200, 130, window=self.entry5, width=50)
            self.canvas2.create_window(200, 90, window=self.label5)
        if self.variable_b.get() == "Input group":
            self.label6 = ttk.Label(self.canvas2, text="Group")
            self.entry6 = ttk.Entry(self.canvas2)
            self.canvas2.create_window(90, 130, window=self.entry6, width=50)
            self.canvas2.create_window(90, 90, window=self.label6)

    # def testcom(self):
    #     """metadata menu 2 update"""
    #     #these if loops clean up after user input for chaging meta data
    #     if self.variable_a.get() == "Group":
    #         if self.variable_b.get() == "Input Group":
    #             self.graph.nodes()[str(self.entry3.get())].update({"Group":self.entry6.get()})
    #             self.label6.destroy()
    #             self.entry6.destroy()
    #         else:
    #             self.graph.nodes()[str(self.entry3.get())].update({"Group":self.variable_b.get()})
    #     elif self.variable_a.get() == "Determination":
    #         if self.variable_b.get() == "Input date":
    #             self.graph.nodes()[str(self.entry3.get())].update({"Determination": [self.entry4.get(), self.entry5.get()]})
    #             self.label4.destroy()
    #             self.entry4.destroy()
    #             self.label5.destroy()
    #             self.entry5.destroy()
    #         else:
    #             self.graph.nodes()[str(self.entry3.get())].update({"Determination":self.variable_b.get()})
    #     elif self.variable_a.get() == "Find_Type":
    #         self.graph.nodes()[str(self.entry3.get())].update({"Find_Type":self.variable_b.get()})
    # #    self.canvas2.create_window((0, 0), window=self.metatext, anchor='nw')
    #     self.meta1 = pd.DataFrame.from_dict(self.graph.nodes()[str(self.entry3.get())],
    #                                         orient='index')
    #     self.meta2 = self.meta1.loc["Determination":"Group",]
    #     self.meta2.columns = ["Data"]
    #     if self.meta2.loc["Determination"][0] != "None":
    #         self.meta2.loc["Determination"][0] = str(self.meta2.loc["Determination"][0][0]) + " +- " + str(self.meta2.loc["Determination"][0][1]) + " Carbon BP"
    #     #self.canvas.itemconfig(self.metatext_id, text="Metadata of node " + str(self.entry3),  font='helvetica 12 bold')
    #     cols = list(self.meta2.columns)
    #     tree = ttk.Treeview(self.canvas)
    #     tree["columns"] = cols
    #     tree.place(relx=0.76, rely=0.65)
    #     tree.column("Data", anchor="w")
    #     tree.heading("Data", text="Data", anchor='w')
    #     for index, row in self.meta2.iterrows():
    #         tree.insert("", 0, text=index, values=list(row))

    def update_options(self, *args):
        """updates metadata drop down menu 1"""
        meta_data = self.dict[self.variable_a.get()]
        self.variable_b.set(meta_data[0])
        menu = self.optionmenu_b["menu"]
        menu.delete(0, "end")
        for meta in meta_data:
            menu.add_command(label=meta, command=lambda nation=meta: self.variable_b.set(nation))

    def cleanup(self):
        """cleans up popup2"""
        self.top.destroy()


class popupWindow3(object):
    def __init__(
        self, master, graph, canvas, phase_rels, dropdown_ns=[], dropdown_intru=[], resid_list=[], intru_list=[]
    ):
        """initialises popup3"""
        # set up the canvas for checking if contexts are residual or intrusive
        self.littlecanvas2 = canvas
        self.top = tk.Toplevel(master)
        self.top.geometry("1500x400")
        self.maincanvas = tk.Canvas(
            self.top, bg="#AEC7D6", highlightthickness=0, borderwidth=0, highlightbackground="white"
        )
        self.maincanvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.maincanvas.update()
        self.backcanvas = tk.Canvas(
            self.maincanvas, bg="white", highlightthickness=0, borderwidth=0, highlightbackground="white"
        )
        self.backcanvas.place(relx=0.135, rely=0.9, relheight=0.13, relwidth=0.53)
        self.backcanvas.create_line(150, 30, 600, 30, arrow=tk.LAST, width=3)
        self.time_label = tk.Label(self.maincanvas, text="Time")
        self.time_label.config(bg="white", font=("helvetica", 12, "bold"), fg="#2f4858", wraplength=130)
        self.time_label.place(relx=0.32, rely=0.91, relwidth=0.12, relheight=0.05)
        self.top.title("Adding group relationships")
        self.graph = graph
        # makes a copy of the graph so I can edit it to chrnograph
        self.graphcopy = copy.deepcopy(self.graph)
        phasedict = nx.get_node_attributes(self.graphcopy, "Group")  # get all the phases for each node
        datadict = nx.get_node_attributes(self.graphcopy, "Determination")  # get all dates for each notes
        nodes = self.graphcopy.nodes()  # all contexts
        self.node_del_tracker = []  # empty node tracker
        # checks for each context and if there isn't node or phase info, it deletes it
        for i in nodes:
            if phasedict[i] is not None:
                self.node_del_tracker.append(i)
            elif datadict[i] == [None, None]:
                self.node_del_tracker.append(i)
        for j in self.node_del_tracker:
            self.graphcopy = node_del_fixed(self.graphcopy, j)
        # sets up all the vairables we need for this class
        self.context_no_unordered = [
            x for x in list(self.graph.nodes()) if x not in self.node_del_tracker
        ]  # sets up a context list
        self.CONT_TYPE = ["normal" for i in self.context_no_unordered]  # set up context types
        self.phases = phase_rels
        self.resid_list3 = resid_list
        self.intru_list3 = intru_list
        self.dropdown_ns = dropdown_ns
        self.dropdown_intru = dropdown_intru
        # checks if contexts are residual or intrusive and if we want to keep them or exclude from modelling
        for i in self.resid_list3:
            if self.dropdown_ns[i].get() == "Treat as TPQ":
                self.CONT_TYPE[np.where(np.array(self.context_no_unordered) == i)[0][0]] = "residual"
            elif self.dropdown_ns[i].get() == "Exclude from modelling":
                self.graphcopy = node_del_fixed(self.graphcopy, i)
                self.CONT_TYPE.pop(np.where(np.array(self.context_no_unordered) == i)[0][0])
                self.context_no_unordered.remove(self.resid_list3[i])

        for j in self.intru_list3:
            if self.dropdown_intru[j].get() == "Treat as TAQ":
                self.CONT_TYPE[np.where(np.array(self.context_no_unordered) == j)[0][0]] = "intrusive"
            elif self.dropdown_intru[j].get() == "Exclude from modelling":
                self.graphcopy = node_del_fixed(self.graphcopy, j)
                self.CONT_TYPE.pop(np.where(np.array(self.context_no_unordered) == j)[0][0])
                self.context_no_unordered.remove(j)
        self.step_1 = chrono_edge_remov(self.graphcopy)
        self.COLORS = [
            "LavenderBlush2",
            "powder blue",
            "LavenderBlush3",
            "LemonChiffon4",
            "dark khaki",
            "LightGoldenrod1",
            "aquamarine2",
            "hot pink",
            "DarkOrchid4",
            "pale turquoise",
            "LightSteelBlue2",
            "DeepPink4",
            "firebrick4",
            "khaki4",
            "turquoise3",
            "alice blue",
            "DarkOrange4",
            "LavenderBlush4",
            "misty rose",
            "pink1",
            "OrangeRed2",
            "chocolate2",
            "OliveDrab2",
            "LightSteelBlue3",
            "firebrick2",
            "dark orange",
            "ivory2",
            "yellow2",
            "DeepPink3",
            "aquamarine",
            "LightPink2",
            "DeepSkyBlue2",
            "LightCyan4",
            "RoyalBlue3",
            "SeaGreen3",
            "SlateGray1",
            "IndianRed3",
            "DarkGoldenrod3",
            "HotPink1",
            "navy",
            "tan2",
            "orange4",
            "tomato",
            "LightSteelBlue1",
            "coral1",
            "MediumOrchid4",
            "light grey",
            "DarkOrchid3",
            "RosyBrown2",
            "LightSkyBlue1",
            "medium sea green",
            "deep pink",
            "OrangeRed3",
            "sienna2",
            "thistle2",
            "linen",
            "tan4",
            "bisque2",
            "MediumPurple4",
            "DarkSlateGray4",
            "mint cream",
            "sienna3",
            "lemon chiffon",
            "ivory3",
            "chocolate1",
            "peach puff",
            "DeepSkyBlue3",
            "khaki2",
            "SlateGray2",
            "dark turquoise",
            "deep sky blue",
            "light sky blue",
            "lime green",
            "yellow",
            "burlywood3",
            "tomato4",
            "orange3",
            "wheat2",
            "olive drab",
            "brown3",
            "burlywood1",
            "LightPink1",
            "light cyan",
            "saddle brown",
            "SteelBlue3",
            "SpringGreen3",
            "goldenrod4",
            "dark salmon",
            "DodgerBlue3",
            "MediumPurple3",
            "azure2",
            "lavender blush",
            "SteelBlue4",
            "honeydew3",
            "LightBlue1",
            "DeepSkyBlue4",
            "medium aquamarine",
            "turquoise1",
            "thistle",
            "DarkGoldenrod2",
            "wheat3",
            "LemonChiffon2",
            "turquoise",
            "light sea green",
            "maroon3",
            "green4",
            "SlateBlue1",
            "DarkOliveGreen3",
            "dark violet",
            "LightYellow3",
            "DarkGoldenrod1",
            "PeachPuff3",
            "DarkOrange1",
            "goldenrod2",
            "goldenrod1",
            "SkyBlue4",
            "ivory4",
            "DarkSeaGreen3",
            "aquamarine4",
            "VioletRed3",
            "orange red",
            "CadetBlue3",
            "DarkSlateGray2",
            "seashell2",
            "DarkOliveGreen4",
            "SkyBlue2",
            "DarkOrchid2",
            "maroon1",
            "orchid1",
            "red3",
            "LightSkyBlue4",
            "HotPink4",
            "LightBlue2",
            "coral3",
            "magenta4",
            "bisque4",
            "SteelBlue1",
            "cornsilk3",
            "dark sea green",
            "RosyBrown3",
            "salmon3",
            "NavajoWhite2",
            "PaleTurquoise4",
            "SteelBlue2",
            "OliveDrab1",
            "ghost white",
            "HotPink3",
            "salmon",
            "maroon",
            "khaki3",
            "AntiqueWhite1",
            "PaleVioletRed2",
            "maroon2",
            "cyan3",
            "MistyRose4",
            "thistle3",
            "gold3",
            "tomato3",
            "tan1",
            "LightGoldenrod3",
            "blue violet",
            "tomato2",
            "RoyalBlue4",
            "pink3",
            "cadet blue",
            "slate gray",
            "medium slate blue",
            "PaleGreen3",
            "DodgerBlue2",
            "LightSkyBlue3",
            "lawn green",
            "PaleGreen1",
            "forest green",
            "thistle1",
            "snow",
            "LightSteelBlue4",
            "medium violet red",
            "pink2",
            "PaleVioletRed4",
            "VioletRed1",
            "gainsboro",
            "navajo white",
            "DarkOliveGreen1",
            "IndianRed2",
            "RoyalBlue2",
            "dark olive green",
            "AntiqueWhite3",
            "DarkSlateGray1",
            "LightSalmon3",
            "salmon4",
            "plum3",
            "orchid3",
            "azure",
            "bisque3",
            "turquoise4",
            "SeaGreen1",
            "sienna4",
            "pink",
            "MediumOrchid1",
            "thistle4",
            "PaleVioletRed3",
            "blanched almond",
            "DarkOrange2",
            "royal blue",
            "blue2",
            "chartreuse4",
            "LightGoldenrod4",
            "NavajoWhite4",
            "dark orchid",
            "plum1",
            "SkyBlue1",
            "OrangeRed4",
            "khaki",
            "PaleGreen2",
            "yellow4",
            "maroon4",
            "turquoise2",
            "firebrick3",
            "bisque",
            "LightCyan2",
            "burlywood4",
            "PaleTurquoise3",
            "azure4",
            "gold",
            "yellow3",
            "chartreuse3",
            "RosyBrown1",
            "white smoke",
            "PaleVioletRed1",
            "papaya whip",
            "medium spring green",
            "AntiqueWhite4",
            "SlateGray4",
            "LightYellow4",
            "coral2",
            "MediumOrchid3",
            "CadetBlue2",
            "LightBlue3",
            "snow2",
            "purple1",
            "magenta3",
            "OliveDrab4",
            "DarkOrange3",
            "seashell3",
            "magenta2",
            "green2",
            "snow4",
            "DarkSeaGreen4",
            "slate blue",
            "PaleTurquoise1",
            "red2",
            "LightSkyBlue2",
            "snow3",
            "green yellow",
            "DeepPink2",
            "orange2",
            "cyan",
            "light goldenrod",
            "light pink",
            "honeydew4",
            "RoyalBlue1",
            "sea green",
            "pale violet red",
            "AntiqueWhite2",
            "blue",
            "LightSalmon2",
            "SlateBlue4",
            "orchid4",
            "dark slate gray",
            "dark slate blue",
            "purple",
            "chartreuse2",
            "khaki1",
            "LightBlue4",
            "light yellow",
            "indian red",
            "VioletRed2",
            "gold4",
            "light goldenrod yellow",
            "rosy brown",
            "IndianRed4",
            "azure3",
            "orange",
            "VioletRed4",
            "salmon2",
            "SeaGreen2",
            "pale goldenrod",
            "pale green",
            "plum2",
            "dark green",
            "coral4",
            "LightGoldenrod2",
            "goldenrod3",
            "NavajoWhite3",
            "MistyRose2",
            "wheat1",
            "medium turquoise",
            "floral white",
            "red4",
            "firebrick1",
            "burlywood2",
            "DarkGoldenrod4",
            "goldenrod",
            "sienna1",
            "MediumPurple1",
            "purple2",
            "LightPink4",
            "dim gray",
            "LemonChiffon3",
            "light steel blue",
            "seashell4",
            "brown1",
            "wheat4",
            "MediumOrchid2",
            "DarkOrchid1",
            "RosyBrown4",
            "blue4",
            "cyan2",
            "salmon1",
            "MistyRose3",
            "chocolate3",
            "light salmon",
            "coral",
            "honeydew2",
            "light blue",
            "sandy brown",
            "LightCyan3",
            "brown2",
            "midnight blue",
            "CadetBlue1",
            "LightYellow2",
            "cornsilk4",
            "cornsilk2",
            "SpringGreen4",
            "PeachPuff4",
            "PaleGreen4",
            "SlateBlue2",
            "orchid2",
            "purple3",
            "light slate blue",
            "purple4",
            "lavender",
            "cornflower blue",
            "CadetBlue4",
            "DodgerBlue4",
            "SlateBlue3",
            "DarkSlateGray3",
            "medium orchid",
            "gold2",
            "pink4",
            "DarkOliveGreen2",
            "spring green",
            "dodger blue",
            "IndianRed1",
            "violet red",
            "MediumPurple2",
            "old lace",
            "LightSalmon4",
            "brown4",
            "SpringGreen2",
            "yellow green",
            "plum4",
            "SlateGray3",
            "steel blue",
            "HotPink2",
            "medium purple",
            "LightPink3",
            "PeachPuff2",
            "sky blue",
            "dark goldenrod",
            "PaleTurquoise2",
        ]
        self.canvas = tk.Canvas(self.top, bg="white")
        self.canvas.place(relx=0.135, rely=0.05, relheight=0.85, relwidth=0.53)
        self.canvas.update()
        self.instruc_label = tk.Label(
            self.maincanvas,
            text="Instructions: \n Place the oldest group in the bottom left corner then for each subseqent group, place it directly above and move it to be overlapping, abutting or to have a gap.",
        )
        self.instruc_label.config(bg="white", font=("helvetica", 12, "bold"), fg="#2f4858", wraplength=130)
        self.instruc_label.place(relx=0.01, rely=0.05, relwidth=0.12, relheight=0.85)
        self.instruc_label2 = tk.Label(self.maincanvas, text="User defined group relationships")
        self.instruc_label2.config(bg="white", font=("helvetica", 12, "bold"), fg="#2f4858")
        self.instruc_label2.place(relx=0.67, rely=0.17, relwidth=0.32, relheight=0.1)

        self.label_dict = {}
        phases = []
        for i in phase_rels:
            phases.append(i[0])
            phases.append(i[1])
        self.phase_labels = list(set(phases))
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        m = len(self.phase_labels)
        for ind, i in enumerate(self.phase_labels):
            msg = tk.Label(self.canvas, text=str(i))
            msg.config(bg=self.COLORS[ind], font=("helvetica", 14, "bold"))
            msg.bind("<B1-Motion>", self.on_move)
            msg.place(
                x=0.05 * w + (w / (2 * m)) * ind,
                y=0.85 * h - ((0.95 * h) / m) * ind,
                relwidth=0.76 / m,
                relheight=min(0.1, 0.9 / m),
            )
            self.label_dict[i] = msg
        self.button1 = tk.Button(
            self.maincanvas,
            text="Confirm groups",
            command=lambda: self.get_coords(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.button1.place(relx=0.8, rely=0.91)
        self.df = pd.DataFrame(phase_rels, columns=["Younger group", "Older group"])
        self.frmtreeborder = tk.LabelFrame(self.maincanvas, bg="white")
        self.frmtreeborder.columnconfigure(0, weight=1)
        self.frmtreeborder.rowconfigure(0, weight=1)
        cols = list(self.df.columns)
        self.tree = ttk.Treeview(self.frmtreeborder)
        self.frmtreeborder.place(relx=0.67, rely=0.25, relheight=0.65, relwidth=0.32)
        self.tree.grid(column=0, row=0, sticky="nsew", padx=6, pady=6)
        self.tree["columns"] = cols
        for i in cols:
            self.tree.column(i, anchor="w")
            self.tree.heading(i, text=i, anchor="w")

        for index, row in self.df.iterrows():
            self.tree.insert("", 0, text=index, values=list(row))
        self.tree["show"] = "headings"
        master.wait_window(self.top)

    def get_coords(self):
        self.instruc_label.destroy()
        self.button1.destroy()
        self.tree.destroy()
        self.frmtreeborder.destroy()
        self.maincanvas.columnconfigure(0, weight=1)
        self.maincanvas.rowconfigure(0, weight=1)
        self.maincanvas.update()
        self.instruc_label = tk.Label(
            self.maincanvas,
            text="If you're happy with your group relationships, click the Render Chronological Graph button.",
        )
        self.instruc_label.config(bg="white", font=("helvetica", 12, "bold"), wraplength=130)
        self.instruc_label.place(relx=0.01, rely=0.05, relwidth=0.12, relheight=0.85)

        y_list = []
        for i in self.label_dict.keys():
            yx = self.label_dict[i].winfo_y()
            my = self.label_dict[i].winfo_height()
            y_cent = yx + 0.5 * my
            y_list.append((i, y_cent))
        y_final = sorted(y_list, key=lambda x: x[1])
        y_final.reverse()
        ref_y = y_final[0][1]
        ref_h = self.label_dict[y_final[0][0]].winfo_height()
        ref_w = self.label_dict[y_final[0][0]].winfo_width()
        ref_gap = 0.25 * ref_w
        orig_x = [self.label_dict[j[0]].winfo_x() for j in y_final[1:]]
        orig_x_prev = [self.label_dict[j[0]].winfo_x() + ref_w for j in y_final[:-1]]
        self.prev_dict = {}
        self.post_dict = {}
        self.menudict = {}
        for ind, j in enumerate(y_final[1:]):
            x = orig_x[ind]
            x_prev = orig_x_prev[ind]
            if ind < len(y_final) - 1:
                x_prev_curr = self.label_dict[y_final[ind][0]].winfo_x() + ref_w
                if x - x_prev < -15:
                    x = x_prev_curr - ref_gap
                    self.prev_dict[str(j[0])] = "overlap"
                    self.post_dict[str(y_final[ind][0])] = "overlap"
                    self.menudict[(str(j[0]), str(y_final[ind][0]))] = "overlap"

                elif x - x_prev > 15:
                    x = x_prev_curr + ref_gap
                    self.prev_dict[str(j[0])] = "gap"
                    self.post_dict[str(y_final[ind][0])] = "gap"
                    self.menudict[(str(j[0]), str(y_final[ind][0]))] = "gap"
                else:
                    x = x_prev_curr
                    self.prev_dict[str(j[0])] = "abutting"
                    self.post_dict[str(y_final[ind][0])] = "abutting"
                    self.menudict[(str(j[0]), str(y_final[ind][0]))] = "abutting"
                y = ref_y - (0.5 + ind + 1) * ref_h  # ceter of top box + (half and scalefactor) times height
                self.label_dict[j[0]].place(x=x, y=y)
                self.canvas.update()
        col1, col2, col3 = [], [], []
        rels_df = pd.DataFrame()
        for i in self.menudict.keys():
            col1.append(i[0])
            col2.append(i[1])
            col3.append(self.menudict[i])
        rels_df["Younger group"] = col1
        rels_df["Older group"] = col2
        rels_df["Relationship"] = col3
        cols = list(rels_df.columns)
        self.frmtreeborder = tk.LabelFrame(self.maincanvas, bg="white")
        self.frmtreeborder.columnconfigure(0, weight=1)
        self.frmtreeborder.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(self.frmtreeborder)
        self.frmtreeborder.place(relx=0.67, rely=0.25, relheight=0.65, relwidth=0.32)
        self.tree.grid(column=0, row=0, sticky="nsew", padx=6, pady=6)
        self.tree["columns"] = cols
        for i in cols:
            self.tree.column(i, anchor="w", width=100)
            self.tree.heading(i, text=i, anchor="w")

        for index, row in rels_df.iterrows():
            self.tree.insert("", 0, text=index, values=list(row))
        self.tree["show"] = "headings"
        self.button_b = tk.Button(
            self.maincanvas,
            text="Render Chronological graph",
            command=lambda: self.full_chronograph_func(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.button_b.place(relx=0.75, rely=0.91)
        self.button_a = tk.Button(
            self.maincanvas,
            text="Change relationships",
            command=lambda: self.back_func(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.button_a.place(relx=0.55, rely=0.91)

    def back_func(self):
        self.button_b.destroy()
        self.instruc_label.destroy()
        self.button_a.destroy()
        self.maincanvas.update()
        self.button1 = tk.Button(
            self.maincanvas,
            text="Confirm groups",
            command=lambda: self.get_coords(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.button1.place(relx=0.8, rely=0.91)
        self.instruc_label = tk.Label(
            self.maincanvas,
            text="Instructions: \n Place the oldest group in the bottom left corner then for each subseqent group, place it directly above and move it to be overlapping, abutting or to have a gap.",
        )
        self.instruc_label.config(bg="white", font=("helvetica", 12, "bold"), wraplength=130)
        self.instruc_label.place(relx=0.01, rely=0.05, relwidth=0.18, relheight=0.85)

    def on_move(self, event):
        component = event.widget
        locx, locy = component.winfo_x(), component.winfo_y()  # top left coords for where the object is
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()  # width of master canvas
        mx, my = component.winfo_width(), component.winfo_height()  # width of boxes
        xpos = (locx + event.x) - (15)
        ypos = (locy + event.y) - int(my / 2)
        if (
            xpos >= 0
            and ypos >= 0
            and w - abs(xpos) >= 0
            and xpos <= (w - mx)
            and h - abs(ypos) >= 0
            and ypos <= (h - my)
        ):
            component.place(x=xpos, y=ypos)

    def full_chronograph_func(self):
        """renders the chronological graph and forms the prev_phase and past_phase vectors"""
        self.prev_phase = ["start"]
        self.post_phase = []
        phase_list = self.step_1[2]
        if len(self.step_1[0][1][3]) != 0:
            self.graphcopy, self.phi_ref, self.null_phases = chrono_edge_add(
                self.graphcopy,
                self.step_1[0],
                self.step_1[1],
                self.menudict,
                self.phases,
                self.post_dict,
                self.prev_dict,
            )
            self.post_phase.append(self.post_dict[self.phi_ref[0]])
            # adds the phase relationships to prev_phase and post_phase
            for i in range(1, len(self.phi_ref) - 1):
                self.prev_phase.append(self.prev_dict[self.phi_ref[i]])
                self.post_phase.append(self.post_dict[self.phi_ref[i]])
            self.prev_phase.append(self.prev_dict[self.phi_ref[len(self.phi_ref) - 1]])
        else:
            self.phi_ref = list(self.step_1[0][1][2])
        self.post_phase.append("end")
        del_phases = [i for i in self.phi_ref if i not in phase_list]
        ref_list = []
        for i in del_phases:
            ref = np.where(np.array(self.phi_ref) == i)[0][0]
            ref_list.append(ref)
        # deletes missing context references from phi_ref
        for index in sorted(ref_list, reverse=True):
            del self.phi_ref[index]
        # change to new phase rels
        for i in ref_list:
            self.prev_phase[i] = "gap"
            self.post_phase[i] = "gap"
        self.graphcopy.graph["graph"] = {"splines": "ortho"}
        atribs = nx.get_node_attributes(self.graphcopy, "Group")
        nodes = self.graphcopy.nodes()
        edge_add = []
        edge_remove = []
        for i, j in enumerate(self.context_no_unordered):
            ####find paths in that phase

            phase = atribs[j]
            root = [i for i in nodes if "b_" + str(phase) in i][0]
            leaf = [i for i in nodes if "a_" + str(phase) in i][0]
            all_paths = []
            all_paths.extend(nx.all_simple_paths(self.graphcopy, source=root, target=leaf))

            if self.CONT_TYPE[i] == "residual":
                for f in all_paths:
                    if j in f:
                        ind = np.where(np.array(f) == str(j))[0][0]
                        edge_add.append((f[ind - 1], f[ind + 1]))
                for k in self.graphcopy.edges():
                    if k[0] == j:
                        edge_remove.append((k[0], k[1]))
            elif self.CONT_TYPE[i] == "intrusive":
                for f in all_paths:
                    if j in f:
                        ind = np.where(np.array(f) == str(j))[0][0]
                        edge_add.append((f[ind - 1], f[ind + 1]))
                for k in self.graphcopy.edges():
                    if k[1] == j:
                        edge_remove.append((k[0], k[1]))
        for a in edge_add:
            self.graphcopy.add_edge(a[0], a[1], arrowhead="none")
        for b in edge_remove:
            self.graphcopy.remove_edge(b[0], b[1])
        write_dot(self.graphcopy, "fi_new_chrono")
        self.top.destroy()


# mainframe is the parent class that holds all the other classes
class MainFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        """initilaises the main frame for tkinter app"""
        tk.Tk.__init__(self, *args, **kwargs)
        os.chdir(POLYCHRON_PROJECTS_DIR)
        load_Window(self)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames = {}

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        frame.tkraise()
        frame.config()

    def get_page(self, page_class):
        """Shows the desired frame"""
        return self.frames[page_class]


class popupWindow4(object):
    def __init__(self, master, controller, resid_list, intru_list, node_track, graph):
        """initialised window 4"""
        self.top = tk.Toplevel(controller)
        self.top.configure(bg="#AEC7D6")
        self.top.title("Managing intrusive and residual contexts")
        self.top.geometry("1000x400")
        self.node_del_tracker = node_track
        self.controller = controller
        self.resid_list = resid_list
        self.intru_list = intru_list
        self.button = tk.Button(
            self.top,
            text="Go back",
            command=lambda: self.top.destroy(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.button.grid(column=30, row=4)
        self.button2 = tk.Button(
            self.top,
            text="Proceed to render chronological graph",
            command=lambda: self.move_to_graph(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.button2.grid(column=30, row=6)
        self.test(resid_list, intru_list)
        controller.wait_window(self.top)

    def move_to_graph(self):
        """gets everything ready for popup3 and load the chronograph"""
        startpage = self.controller.get_page("StartPage")
        self.controller.show_frame("StartPage")
        self.popup3 = popupWindow3(
            startpage,
            startpage.graph,
            startpage.littlecanvas2,
            startpage.phase_rels,
            self.dropdown_ns,
            self.dropdown_intru,
            self.resid_list,
            self.intru_list,
        )
        # inputs for MCMC function
        self.CONT_TYPE = self.popup3.CONT_TYPE
        self.prev_phase = self.popup3.prev_phase
        self.post_phase = self.popup3.post_phase
        self.phi_ref = self.popup3.phi_ref
        self.context_no_unordered = self.popup3.context_no_unordered
        self.graphcopy = self.popup3.graphcopy
        self.node_del_tracker = self.popup3.node_del_tracker
        self.top.destroy()

    def test(self, resid_list, intru_list):
        """Sets up drop down menus for defining what to do with residual or intrusive contexts"""
        self.dropdowns = {}
        self.dropdown_ns = {}
        self.dropdown_intru = {}
        self.nodetype2 = {}
        for i, j in enumerate(resid_list):
            ttk.Label(self.top, text=str(j)).grid(column=0, row=i, padx=30, pady=25)
            self.dropdown_ns[j] = tk.StringVar()
            self.dropdowns[j] = ttk.Combobox(self.top, width=27, textvariable=self.dropdown_ns[j], state="readonly")
            # Adding combobox drop down list
            self.dropdowns[j]["values"] = ("Exclude from modelling", "Treat as TPQ")
            self.dropdowns[j]["background"] = "#ff0000"
            self.dropdowns[j].grid(column=1, row=i)
        for k, l in enumerate(intru_list):
            ttk.Label(self.top, text=str(l)).grid(column=21, row=k, padx=30, pady=25)
            self.dropdown_intru[l] = tk.StringVar()
            self.nodetype2[l] = ttk.Combobox(self.top, width=27, textvariable=self.dropdown_intru[l], state="readonly")
            # Adding combobox drop down list
            self.nodetype2[l]["values"] = ("Exclude from modelling", "Treat as TAQ")
            self.nodetype2[l].current(0)
            #    nodetype2.current(0)
            self.nodetype2[l].grid(column=22, row=k)


class popupWindow5(object):
    def __init__(self, master):
        top = self.top = tk.Toplevel(master)
        top.configure(bg="white")
        self.top.geometry("1000x400")
        self.top.title("Removal of context")
        self.l = tk.Label(
            top,
            text="Why are you removing this context from your stratigraphy?",
            bg="white",
            font="helvetica 12",
            fg="#2f4858",
        )
        self.l.place(relx=0.3, rely=0.1)
        self.e = tk.Text(top, font="helvetica 12", fg="#2f4858")
        self.e.place(relx=0.3, rely=0.2, relheight=0.5, relwidth=0.5)
        self.b = tk.Button(top, text="OK", command=self.cleanup, bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.b.place(relx=0.3, rely=0.7)

    def cleanup(self):
        self.value = self.e.get("1.0", "end")
        self.top.destroy()


class popupWindow6(object):
    def __init__(self, master):
        top = self.top = tk.Toplevel(master)
        top.configure(bg="white")
        self.top.geometry("1000x400")
        self.top.title("Removal of stratigraphic relationship")
        self.l = tk.Label(
            top,
            text="Why are you deleting the stratigraphic relationship between these contexts?",
            bg="white",
            font="helvetica 12",
            fg="#2f4858",
        )
        self.l.place(relx=0.3, rely=0.1)
        self.e = tk.Text(top, font="helvetica 12", fg="#2f4858")
        self.e.place(relx=0.3, rely=0.2, relheight=0.5, relwidth=0.5)
        self.b = tk.Button(top, text="OK", command=self.cleanup, bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.b.place(relx=0.3, rely=0.7)

    def cleanup(self):
        self.value = self.e.get("1.0", "end")
        self.top.destroy()


class popupWindow7(object):
    def __init__(self, master, df):
        top = self.top = tk.Toplevel(master)
        self.canvas = tk.Canvas(top, bg="white")
        top.title("Data preview")
        self.canvas.pack()
        self.l = tk.Label(self.canvas, text="Data Preview")
        self.l.pack()
        cols = list(df.columns)

        tree = ttk.Treeview(self.canvas)
        tree.pack()
        tree["columns"] = cols
        for i in cols:
            tree.column(i, anchor="w")
            tree.heading(i, text=i, anchor="w")

        for index, row in df.iterrows():
            tree.insert("", 0, text=index, values=list(row))
        tree["show"] = "headings"
        self.b = tk.Button(
            top, text="Load data", command=self.cleanup1, bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.b.pack()
        self.c = tk.Button(
            top, text="Cancel", command=self.cleanup2, bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.c.pack()

    def cleanup1(self):
        self.value = "load"
        self.top.destroy()

    def cleanup2(self):
        self.value = "cancel"
        self.top.destroy()


class popupWindow8(object):
    def __init__(self, master, path):
        self.master = master
        self.path = path
        model_list_prev = [d for d in os.listdir(path) if os.path.isdir(path + "/" + d)]
        model_list = []
        for i in model_list_prev:
            mod_path = str(path) + "/" + str(i) + "/python_only/save.pickle"
            with open(mod_path, "rb") as f:
                data = pickle.load(f)
                load_check = data["load_check"]
            if load_check == "loaded":
                model_list.append(i)

        self.top = tk.Toplevel(master)
        self.top.configure(bg="white")
        self.top.title("Model calibration")
        self.top.geometry("1000x400")
        self.l = tk.Label(
            self.top, text="Which model/s would you like calibrate?", bg="white", font="helvetica 12", fg="#2f4858"
        )
        self.l.place(relx=0.3, rely=0.1)
        self.e = tk.Listbox(self.top, font="helvetica 12", fg="#2f4858", selectmode="multiple")
        self.e.place(relx=0.3, rely=0.2, relheight=0.5, relwidth=0.5)
        #       self.e.bind('<<ListboxSelect>>',tk.CurSelet)
        for items in model_list:
            self.e.insert("end", items)
        self.b = tk.Button(
            self.top, text="OK", command=self.cleanup, bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.b.place(relx=0.3, rely=0.7)
        self.b = tk.Button(
            self.top, text="Select all", command=self.selectall, bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.b.place(relx=0.6, rely=0.7)

    def selectall(self):
        self.e.select_set(0, "end")

    def save_state_1(self, j):
        global mcmc_check, load_check, FILE_INPUT

        vars_list_1 = dir(self)
        var_list = [
            var
            for var in vars_list_1
            if (("__" and "grid" and "get" and "tkinter" and "children") not in var) and (var[0] != "_")
        ]
        data = {}
        check_list = ["tkinter", "method", "__main__", "PIL"]
        for i in var_list:
            v = getattr(self, i)
            if not any(x in str(type(v)) for x in check_list):
                data[i] = v
        data["all_vars"] = list(data.keys())
        data["load_check"] = load_check
        data["mcmc_check"] = mcmc_check
        data["file_input"] = FILE_INPUT
        path = self.path + "/" + str(j) + "/python_only/save.pickle"
        try:
            with open(path, "wb") as f:
                pickle.dump(data, f)
            tk.messagebox.showinfo("Success", "Your model has been saved")
        except Exception:
            tk.messagebox.showerror("Error", "File not saved")

    def load_cal_data(self, j):
        global mcmc_check, load_check, FILE_INPUT
        with open(self.path + "/" + str(j) + "/python_only/save.pickle", "rb") as f:
            data = pickle.load(f)
            vars_list = data["all_vars"]
            for i in vars_list:
                setattr(self, i, data[i])
            FILE_INPUT = data["file_input"]
            load_check = data["load_check"]
            mcmc_check = data["mcmc_check"]

    def cleanup(self):
        global mcmc_check
        values = [self.e.get(idx) for idx in self.e.curselection()]
        for i in values:
            self.load_cal_data(i)
            (
                self.CONTEXT_NO,
                self.ACCEPT,
                self.PHI_ACCEPT,
                self.PHI_REF,
                self.A,
                self.P,
                self.ALL_SAMPS_CONT,
                self.ALL_SAMPS_PHI,
                self.resultsdict,
                self.all_results_dict,
            ) = self.master.MCMC_func()
            mcmc_check = "mcmc_loaded"
            self.save_state_1(i)
        self.top.destroy()


class popupWindow9(object):
    def __init__(self, master, path):
        global mcmc_check
        self.master = master
        self.path = path
        model_list_labels = [
            (str(path) + "/graph_theory_tests_" + str(i), i, "graph_theory_tests_" + str(i))
            for i in self.master.graph.nodes()
        ]
        #        model_list = []
        ref_wd = os.getcwd()
        base_cont_type = self.master.CONT_TYPE
        base_key_ref = self.master.key_ref
        base_context_no = self.master.CONTEXT_NO
        base_graph = self.master.graph
        base_chrono_graph = self.master.chrono_dag
        base_phi_ref = self.master.phi_ref
        base_prev_phase = self.master.prev_phase
        base_post_phase = self.master.post_phase
        base_context_no_unordered = self.master.context_no_unordered
        # RCD_EST = [int(list(self.master.datefile["date"])[list(self.master.datefile["context"]).index(i)]) for i in base_context_no]
        # RCD_ERR = [int(list(self.master.datefile["error"])[list(self.master.datefile["context"]).index(i)]) for i in base_context_no]
        # A = max(min(RCD_EST) - 4*max(RCD_EST), 0)
        # P = min(max(RCD_EST) + 4*max(RCD_EST), 50000)

        self.rc_llhds_dict = {}
        for i, j, k in model_list_labels:
            if k not in os.listdir(path):
                os.chdir(ref_wd)
                self.master.CONT_TYPE = base_cont_type.copy()
                self.master.key_ref = base_key_ref.copy()
                self.master.CONTEXT_NO = base_context_no.copy()
                self.master.graph = base_graph.copy()
                self.master.chrono_dag = base_chrono_graph.copy()
                self.master.phi_ref = base_phi_ref.copy()
                self.master.prev_phase = base_prev_phase.copy()
                self.master.post_phase = base_post_phase.copy()
                self.master.context_no_unordered = base_context_no_unordered.copy()
                # remove_node_section
                self.master.chrono_dag = node_del_fixed(self.master.chrono_dag, j)
                self.master.graph = node_del_fixed(self.master.graph, j)
                ref = np.where(np.array(base_context_no) == str(j))[0][0]
                ref2 = np.where(np.array(base_context_no_unordered) == str(j))[0][0]
                phase = self.master.key_ref[ref]
                phase_ref = np.where(np.array(base_phi_ref) == str(phase))[0][0]
                self.master.CONT_TYPE.pop(ref)
                self.master.key_ref.pop(ref)
                self.master.CONTEXT_NO.pop(ref)
                self.master.context_no_unordered.pop(ref2)
                ## ###correcting phases for removed nodes
                # change to new phase rels
                self.graph_adjust(phase, phase_ref)
                ######## sorting floating nodes
                group_conts = [self.master.CONTEXT_NO[i] for i, j in enumerate(self.master.key_ref) if j == phase]
                for m in group_conts:
                    if len(self.master.chrono_dag.out_edges(m)) == 0:
                        alph = [i for i in self.master.chrono_dag.nodes() if "a_" + phase in i]
                        self.master.chrono_dag.add_edge(m, alph[0], arrowhead="none")
                    if len(self.master.chrono_dag.in_edges(m)) == 0:
                        bet = [i for i in self.master.chrono_dag.nodes() if "b_" + phase in i]
                        self.master.chrono_dag.add_edge(bet[0], m, arrowhead="none")
                #############################    setting up the directorys
                dirs4 = self.make_directories(i)
                write_dot(self.master.chrono_dag, "fi_new_chrono")
                imgrender2(self.master.littlecanvas2.winfo_width(), self.master.littlecanvas2.winfo_height())
                imgrender(
                    self.master.graph, self.master.littlecanvas.winfo_width(), self.master.littlecanvas.winfo_height()
                )
                self.master.ACCEPT = [[]]
                while min([len(i) for i in self.master.ACCEPT]) < 20000:
                    (
                        self.master.CONTEXT_NO,
                        self.master.ACCEPT,
                        self.master.PHI_ACCEPT,
                        self.master.PHI_REF,
                        self.master.A,
                        self.master.P,
                        self.master.ALL_SAMPS_CONT,
                        self.master.ALL_SAMPS_PHI,
                        self.master.resultsdict,
                        self.master.all_results_dict,
                    ) = self.master.MCMC_func()
                mcmc_check = "mcmc_loaded"
                self.save_state_1(self.master, dirs4)

    def prob_overlap(self, ll1, ll2):
        ### hellenger distance
        dist_probs = np.array([(np.sqrt(ll2[1][i]) - np.sqrt(j)) ** 2 for i, j in enumerate(ll1[1])])
        h = 1 - 1 / np.sqrt(2) * (np.sqrt(np.sum(dist_probs)))
        return h

    # def prob_from_samples(self, x_temp, A, P, lim=0.95, probs=0):
    #   if probs == 0:
    #       x_temp = np.array(x_temp)
    #       n = P - A + 1
    #       probs, x_vals = np.histogram(x_temp, range = (A, P), bins=n, density=1)
    #   df = pd.DataFrame({'Theta':x_vals[1:], 'Posterior':probs})
    #   y = df.sort_values(by=['Theta'], ascending=False)
    #   posterior_theta = np.array(y['Theta'])
    #   return posterior_theta

    def node_importance(self, graph):
        G = graph.to_undirected()  # setting up undirected graph
        df_prob_overlap = pd.concat(
            [
                pd.DataFrame(
                    [[str(i), str(j), self.prob_overlap(self.rc_llhds_dict[j], self.rc_llhds_dict[i])]],
                    columns=["node", "neighbour", "overlap_measure"],
                )
                for i in G.nodes()
                for j in list(G.neighbors(i))
            ]
        )
        # katz
        df_prob_overlap.to_csv("overlap_df.csv")
        dd = nx.pagerank(
            G, alpha=0.85, personalization=None, max_iter=100, tol=1e-06, nstart=None, weight="weight", dangling=None
        )
        df = pd.DataFrame.from_dict(dd, orient="index")
        df.reset_index(inplace=True)
        df.columns = ["context", "pagerank"]
        df.to_csv("katz_centr.csv")

    def graph_adjust(self, phase, phase_ref):
        graph_check = nx.transitive_reduction(self.master.chrono_dag)
        if self.master.chrono_dag.edges() != graph_check.edges():
            edges1 = list(self.master.chrono_dag.edges()).copy()
            for k in edges1:
                if k not in graph_check.edges():
                    self.master.chrono_dag.remove_edge(k[0], k[1])
        if phase not in self.master.key_ref:
            self.master.phi_ref.pop(phase_ref)
            if self.master.prev_phase[phase_ref] == "start":
                phase_node = [i for i in self.master.chrono_dag.nodes() if "b_" + str(phase) in i]
                self.master.chrono_dag.remove_node("a_" + str(phase))
                old_label = str(phase_node[0])
                new_label = "a_" + str(self.master.phi_ref[phase_ref + 1])
                mapping = {old_label: new_label}
                self.master.prev_phase.pop(phase_ref)
                self.master.post_phase.pop(phase_ref)
                self.master.prev_phase[phase_ref] = "start"
            elif self.master.post_phase[phase_ref] == "end":
                phase_node = [i for i in self.master.chrono_dag.nodes() if "a_" + str(phase) in i]
                self.master.chrono_dag.remove_node("b_" + str(phase))
                old_label = str(phase_node[0])
                new_label = "b_" + str(self.master.phi_ref[phase_ref - 1])
                mapping = {old_label: new_label}
                self.master.prev_phase.pop(phase_ref)
                self.master.post_phase.pop(phase_ref)
                self.master.post_phase[phase_ref] = "end"
            else:
                phase_nodes = [i for i in self.master.chrono_dag.nodes() if phase in i]
                self.master.chrono_dag.remove_edge(phase_nodes[0], phase_nodes[1])
                self.master.chrono_dag = nx.contracted_nodes(self.master.chrono_dag, phase_nodes[0], phase_nodes[1])
                new_label_1 = str(phase_nodes[0])
                new_label = new_label_1.replace("a_" + str(phase), "a_" + str(self.master.phi_ref[phase_ref + 1]))
                mapping = {phase_nodes[0]: new_label}
                self.master.prev_phase.pop(phase_ref)
                self.master.post_phase.pop(phase_ref)
                self.master.prev_phase[phase_ref] = "gap"
                self.master.post_phase[phase_ref] = "gap"
            self.master.chrono_dag = nx.relabel_nodes(self.master.chrono_dag, mapping)
            self.master.chrono_dag = phase_relabel(self.master.chrono_dag)
        self.master.chrono_dag.graph["graph"] = {"splines": "ortho"}
        atribs = nx.get_node_attributes(self.master.chrono_dag, "Group")
        nodes = self.master.chrono_dag.nodes()
        edge_add = []
        edge_remove = []
        for v, w in enumerate(self.master.CONTEXT_NO):
            ####find paths in that phase
            if self.master.CONT_TYPE[v] == "residual":
                phase = atribs[w]
                root = [i for i in nodes if "b_" + str(phase) in i][0]
                leaf = [i for i in nodes if "a_" + str(phase) in i][0]
                all_paths = []
                all_paths.extend(nx.all_simple_paths(self.master.chrono_dag, source=root, target=leaf))
                for f in all_paths:
                    ind = np.where(np.array(f) == str(w))[0][0]
                    edge_add.append((f[ind - 1], f[ind + 1]))
                for k in self.master.chrono_dag.edges():
                    if k[0] == w:
                        edge_remove.append((k[0], k[1]))
            elif self.master.CONT_TYPE[v] == "intrusive":
                for k in self.master.chrono_dag.edges():
                    if k[1] == w:
                        edge_remove.append((k[0], k[1]))
        for a in edge_add:
            self.master.chrono_dag.add_edge(a[0], a[1], arrowhead="none")
        for b in edge_remove:
            self.master.chrono_dag.remove_edge(b[0], b[1])

    def make_directories(self, i):
        dirs2 = os.path.join(i, "stratigraphic_graph")
        dirs3 = os.path.join(i, "chronological_graph")
        dirs4 = os.path.join(i, "python_only")
        dirs5 = os.path.join(i, "mcmc_results")
        os.makedirs(dirs2)
        os.makedirs(dirs3)
        os.makedirs(dirs4)
        os.makedirs(dirs5)
        os.chdir(i)
        return dirs4

    def selectall(self):
        self.e.select_set(0, "end")

    def save_state_1(self, master, j):
        global mcmc_check, load_check, FILE_INPUT

        vars_list_1 = dir(self.master)
        var_list = [
            var
            for var in vars_list_1
            if (("__" and "grid" and "get" and "tkinter" and "children") not in var) and (var[0] != "_")
        ]
        data = {}
        check_list = ["tkinter", "method", "__main__", "PIL"]
        for i in var_list:
            v = getattr(master, i)
            if not any(x in str(type(v)) for x in check_list):
                data[i] = v
        data["all_vars"] = list(data.keys())
        data["load_check"] = load_check
        data["mcmc_check"] = mcmc_check
        data["file_input"] = FILE_INPUT
        path = j + "/save.pickle"
        if mcmc_check == "mcmc_loaded":
            results = data["all_results_dict"]
            df = pd.DataFrame()
            for i in results.keys():
                df[i] = results[i][10000:]
            results_path = os.getcwd() + "/mcmc_results/full_results_df"
            df.to_csv(results_path)
            phasefile = data["phasefile"]
            context_no = data["CONTEXT_NO"]
            key_ref = [list(phasefile["Group"])[list(phasefile["context"]).index(i)] for i in context_no]
            df1 = pd.DataFrame(key_ref)
            df1.to_csv("mcmc_results/key_ref.csv")
            df2 = pd.DataFrame(context_no)
            df2.to_csv("mcmc_results/context_no.csv")

        try:
            with open(path, "wb") as f:
                pickle.dump(data, f)
        except Exception:
            tk.messagebox.showerror("Error", "File not saved")

    def load_cal_data(self, j):
        global mcmc_check, load_check, FILE_INPUT
        with open(self.path + "/" + str(j) + "/python_only/save.pickle", "rb") as f:
            data = pickle.load(f)
            vars_list = data["all_vars"]
            for i in vars_list:
                setattr(self, i, data[i])
            FILE_INPUT = data["file_input"]
            load_check = data["load_check"]
            mcmc_check = data["mcmc_check"]


class popupWindow10(object):
    def __init__(self, master, path):
        global mcmc_check
        self.master = master
        self.path = path
        # for i in range(20,140):
        #     katz_df_subset = katz_df_test.sort_values(by='pagerank', ascending = False).head(i)
        #   ref_wd = os.getcwd()
        #     con_list = list(katz_df_test['context'])
        base_cont_type = self.master.CONT_TYPE
        base_key_ref = self.master.key_ref
        base_context_no = self.master.CONTEXT_NO
        base_graph = self.master.graph
        base_chrono_graph = self.master.chrono_dag
        base_phi_ref = self.master.phi_ref
        base_prev_phase = self.master.prev_phase
        base_post_phase = self.master.post_phase
        base_context_no_unordered = self.master.context_no_unordered

        for num in range(5, 6):
            # for loop would start here
            os.chdir(path)
            self.master.CONT_TYPE = base_cont_type.copy()
            self.master.key_ref = base_key_ref.copy()
            self.master.CONTEXT_NO = base_context_no.copy()
            self.master.graph = base_graph.copy()
            self.master.chrono_dag = base_chrono_graph.copy()
            self.master.phi_ref = base_phi_ref.copy()
            self.master.prev_phase = base_prev_phase.copy()
            self.master.post_phase = base_post_phase.copy()
            self.master.context_no_unordered = base_context_no_unordered.copy()
            katz_df_test = self.top_nodes(num, self.master.phi_ref, self.master.CONTEXT_NO, self.master.key_ref, path)
            # remove_node_section
            remove_conts = [i for i in self.master.CONTEXT_NO if i not in katz_df_test]
            print("remove contexts")

            print(len(remove_conts))
            for j in remove_conts:
                self.master.chrono_dag.remove_node(j)
                self.master.graph.remove_node(j)
                ref = np.where(np.array(self.master.CONTEXT_NO) == str(j))[0][0]
                ref2 = np.where(np.array(self.master.context_no_unordered) == str(j))[0][0]
                phase = self.master.key_ref[ref]
                phase_ref = np.where(np.array(base_phi_ref) == str(phase))[0][0]
                self.master.CONT_TYPE.pop(ref)
                self.master.key_ref.pop(ref)
                self.master.CONTEXT_NO.pop(ref)
                self.master.context_no_unordered.pop(ref2)
                ## ###correcting phases for removed nodes
                # change to new phase rels
                self.graph_adjust(phase, phase_ref)
                ######## sorting floating nodes
                group_conts = [self.master.CONTEXT_NO[i] for i, j in enumerate(self.master.key_ref) if j == phase]
                for m in group_conts:
                    if len(self.master.chrono_dag.out_edges(m)) == 0:
                        alph = [i for i in self.master.chrono_dag.nodes() if "a_" + phase in i]
                        self.master.chrono_dag.add_edge(m, alph[0], arrowhead="none")
                    if len(self.master.chrono_dag.in_edges(m)) == 0:
                        bet = [i for i in self.master.chrono_dag.nodes() if "b_" + phase in i]
                        self.master.chrono_dag.add_edge(bet[0], m, arrowhead="none")
            #############################    setting up the directorys
            dirs4 = self.make_directories("testing" + str(num))
            write_dot(self.master.chrono_dag, "fi_new_chrono")
            imgrender2(self.master.littlecanvas2.winfo_width(), self.master.littlecanvas2.winfo_height())
            imgrender(
                self.master.graph, self.master.littlecanvas.winfo_width(), self.master.littlecanvas.winfo_height()
            )
            self.master.ACCEPT = [[]]
            while min([len(i) for i in self.master.ACCEPT]) < 50000:
                (
                    self.master.CONTEXT_NO,
                    self.master.ACCEPT,
                    self.master.PHI_ACCEPT,
                    self.master.PHI_REF,
                    self.master.A,
                    self.master.P,
                    self.master.ALL_SAMPS_CONT,
                    self.master.ALL_SAMPS_PHI,
                    self.master.resultsdict,
                    self.master.all_results_dict,
                ) = self.master.MCMC_func()
            mcmc_check = "mcmc_loaded"
            self.save_state_1(self.master, dirs4)

    def katz_plus_overlap(self, path, refmodel, mode="strat"):
        if mode == "strat":
            katz_df_test = pd.read_csv(
                path + "/" + refmodel + "/katz_centr_strat.csv"
            )  # katz centrality worked out for the reference model
        elif mode == "chrono":
            katz_df_test = pd.read_csv(path + "/" + refmodel + "/katz_centr_chrono.csv")
        katz_df_test = katz_df_test[["context", "pagerank"]]
        katz_df_test["context"] = katz_df_test["context"].astype(str)
        katz_df_test = katz_df_test.loc[(not katz_df_test["context"].str.contains("a"))]
        katz_df_test = katz_df_test.loc[(not katz_df_test["context"].str.contains("b"))]
        katz_df_test = katz_df_test.transpose()
        katz_df = katz_df_test.rename(columns=katz_df_test.iloc[0]).drop(katz_df_test.index[0]).reset_index(drop=True)
        ll_over_df = pd.read_csv(path + "/" + refmodel + "/overlap_df.csv")
        ll_over_df = pd.DataFrame(
            ll_over_df[["node", "neighbour", "overlap_measure"]]
        )  # overlap df for the reference model
        ll_over_df["neighbour"] = ll_over_df["neighbour"].astype(str)
        ll_over_df["node"] = ll_over_df["node"].astype(str)
        return katz_df, ll_over_df

    def katz_w_weight(self, path):
        with open(path + "/reference_model/python_only/save.pickle", "rb") as f:
            data = pickle.load(f)
        ref_graph = data["graph"]
        katz_df, ll_over_df = self.katz_plus_overlap(path, "reference_model", mode="chrono")
        ll_over_df["neighbour"] = ll_over_df["neighbour"].astype(str)
        ll_over_df["node"] = ll_over_df["node"].astype(str)
        for v, w in ref_graph.edges:
            ref_graph.edges[v, w]["weight"] = float(
                ll_over_df.loc[(ll_over_df["node"] == v) & (ll_over_df["neighbour"] == w)]["overlap_measure"]
            )
        weighted_katz = nx.pagerank(ref_graph.to_undirected())
        return weighted_katz

    def top_nodes(self, num, phi_ref, context_no, key_ref, path):
        contexts = []
        weighted_katz = self.katz_w_weight(path)
        katz_vals = [weighted_katz[label] for i, label in enumerate(context_no)]
        df = pd.DataFrame()
        df["context"] = context_no
        df["key_ref"] = key_ref
        df["katz_vals"] = katz_vals
        print("num")
        print(num)
        for i in phi_ref:
            df_subset = df.loc[df["key_ref"] == i]
            if len(df_subset) > num:
                df_subset.sort_values(by="katz_vals", ascending=False)
                conts = df_subset["context"][0:num]
                [contexts.append(i) for i in conts]
            else:
                conts = df_subset["context"]
                [contexts.append(i) for i in conts]
        return contexts

    def graph_adjust(self, phase, phase_ref):
        if phase not in self.master.key_ref:
            self.master.phi_ref.pop(phase_ref)
            if self.master.prev_phase[phase_ref] == "start":
                phase_node = [i for i in self.master.chrono_dag.nodes() if "b_" + str(phase) in i]
                self.master.chrono_dag.remove_node("a_" + str(phase))
                old_label = str(phase_node[0])
                new_label = "a_" + str(self.master.phi_ref[phase_ref + 1])
                mapping = {old_label: new_label}
                self.master.prev_phase.pop(phase_ref)
                self.master.post_phase.pop(phase_ref)
                self.master.prev_phase[phase_ref] = "start"
            elif self.master.post_phase[phase_ref] == "end":
                phase_node = [i for i in self.master.chrono_dag.nodes() if "a_" + str(phase) in i]
                self.master.chrono_dag.remove_node("b_" + str(phase))
                old_label = str(phase_node[0])
                new_label = "b_" + str(self.master.phi_ref[phase_ref - 1])
                mapping = {old_label: new_label}
                self.master.prev_phase.pop(phase_ref)
                self.master.post_phase.pop(phase_ref)
                self.master.post_phase[phase_ref] = "end"
            else:
                phase_nodes = [i for i in self.master.chrono_dag.nodes() if phase in i]
                self.master.chrono_dag = nx.contracted_nodes(self.master.chrono_dag, phase_nodes[0], phase_nodes[1])
                new_label_1 = str(phase_nodes[0])
                new_label = new_label_1.replace("a_" + str(phase), "a_" + str(self.master.phi_ref[phase_ref + 1]))
                mapping = {phase_nodes[0]: new_label}
                self.master.prev_phase.pop(phase_ref)
                self.master.post_phase.pop(phase_ref)
                self.master.prev_phase[phase_ref] = "gap"
                self.master.post_phase[phase_ref] = "gap"
            self.master.chrono_dag = nx.relabel_nodes(self.master.chrono_dag, mapping)
            self.master.chrono_dag = phase_relabel(self.master.chrono_dag)
        self.master.chrono_dag.graph["graph"] = {"splines": "ortho"}
        atribs = nx.get_node_attributes(self.master.chrono_dag, "Group")
        nodes = self.master.chrono_dag.nodes()
        edge_add = []
        edge_remove = []
        for v, w in enumerate(self.master.CONTEXT_NO):
            ####find paths in that phase
            if self.master.CONT_TYPE[v] == "residual":
                phase = atribs[w]
                root = [i for i in nodes if "b_" + str(phase) in i][0]
                leaf = [i for i in nodes if "a_" + str(phase) in i][0]
                all_paths = []
                all_paths.extend(nx.all_simple_paths(self.master.chrono_dag, source=root, target=leaf))
                for f in all_paths:
                    ind = np.where(np.array(f) == str(w))[0][0]
                    edge_add.append((f[ind - 1], f[ind + 1]))
                for k in self.master.chrono_dag.edges():
                    if k[0] == w:
                        edge_remove.append((k[0], k[1]))
            elif self.master.CONT_TYPE[v] == "intrusive":
                for k in self.master.chrono_graph.edges():
                    if k[1] == w:
                        edge_remove.append((k[0], k[1]))
        for a in edge_add:
            self.master.chrono_graph.add_edge(a[0], a[1], arrowhead="none")
        for b in edge_remove:
            self.master.chrono_graph.remove_edge(b[0], b[1])

    def make_directories(self, i):
        dirs2 = os.path.join(i, "stratigraphic_graph")
        dirs3 = os.path.join(i, "chronological_graph")
        dirs4 = os.path.join(i, "python_only")
        dirs5 = os.path.join(i, "mcmc_results")
        os.makedirs(dirs2)
        os.makedirs(dirs3)
        os.makedirs(dirs4)
        os.makedirs(dirs5)
        os.chdir(i)
        return dirs4

    def selectall(self):
        self.e.select_set(0, "end")

    def save_state_1(self, master, j):
        global mcmc_check, load_check, FILE_INPUT

        vars_list_1 = dir(self.master)
        var_list = [
            var
            for var in vars_list_1
            if (("__" and "grid" and "get" and "tkinter" and "children") not in var) and (var[0] != "_")
        ]
        data = {}
        check_list = ["tkinter", "method", "__main__", "PIL"]
        for i in var_list:
            v = getattr(master, i)
            if not any(x in str(type(v)) for x in check_list):
                data[i] = v
        data["all_vars"] = list(data.keys())
        data["load_check"] = load_check
        data["mcmc_check"] = mcmc_check
        data["file_input"] = FILE_INPUT
        path = os.getcwd() + "/python_only/save.pickle"
        if mcmc_check == "mcmc_loaded":
            results = data["all_results_dict"]
            df = pd.DataFrame()
            for i in results.keys():
                df[i] = results[i][10000:]
            results_path = os.getcwd() + "/mcmc_results/full_results_df"
            df.to_csv(results_path)
            phasefile = data["phasefile"]
            context_no = data["CONTEXT_NO"]
            key_ref = [list(phasefile["Group"])[list(phasefile["context"]).index(i)] for i in context_no]
            df1 = pd.DataFrame(key_ref)
            df1.to_csv("mcmc_results/key_ref.csv")
            df2 = pd.DataFrame(context_no)
            df2.to_csv("mcmc_results/context_no.csv")

        try:
            with open(path, "wb") as f:
                pickle.dump(data, f)
        except Exception:
            tk.messagebox.showerror("Error", "File not saved")

    def load_cal_data(self, j):
        global mcmc_check, load_check, FILE_INPUT
        with open(self.path + "/" + str(j) + "/python_only/save.pickle", "rb") as f:
            data = pickle.load(f)
            vars_list = data["all_vars"]
            for i in vars_list:
                setattr(self, i, data[i])
            FILE_INPUT = data["file_input"]
            load_check = data["load_check"]
            mcmc_check = data["mcmc_check"]


class load_Window(object):
    def __init__(self, master):
        root_x = master.winfo_rootx()
        root_y = master.winfo_rooty()
        self.master = master
        # add offset
        win_x = root_x + 500
        win_y = root_y + 200
        self.top = tk.Toplevel(master)
        self.top.attributes("-topmost", True)
        self.top.title("PolyChron loading page")
        # set toplevel in new position
        self.top.geometry(f"1000x400+{win_x}+{win_y}")
        self.folderPath = tk.StringVar()
        self.maincanvas = tk.Canvas(self.top, bg="white")
        self.maincanvas.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.canvas = tk.Canvas(self.top, bg="#AEC7D6")
        self.canvas.place(relx=0, rely=0, relheight=1, relwidth=0.2)
        self.greeting = None
        self.b = None
        self.c = None
        self.back = None
        self.back1 = None
        self.l = None
        self.selected_langs = None
        self.MyListBox = None
        self.text_1 = None
        self.user_input = None
        self.folder = None
        self.initscreen()

    def initscreen(self):
        [
            x.destroy()
            for x in [
                self.greeting,
                self.b,
                self.c,
                self.back,
                self.back1,
                self.l,
                self.MyListBox,
                self.text_1,
                self.user_input,
            ]
            if x is not None
        ]
        self.maincanvas.update()
        image1 = Image.open(SCRIPT_DIR / "logo.png")
        logo = ImageTk.PhotoImage(image1.resize((360, 70)))
        #       self.imagetk2 = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
        self.label1 = tk.Label(self.maincanvas, image=logo, bg="white")
        self.label1.image = logo
        # Position image
        self.label1.place(relx=0.2, rely=0.2, relheight=0.2, relwidth=0.4)
        self.greeting = tk.Label(
            self.maincanvas,
            text="Welcome to PolyChron, how would you like to proceed?",
            bg="white",
            font=("helvetica 12 bold"),
            fg="#2F4858",
            anchor="w",
        )
        self.greeting.place(relx=0.22, rely=0.45)
        self.b = tk.Button(
            self.maincanvas,
            text="Load existing project",
            command=lambda: self.load_proj(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.b.place(relx=0.8, rely=0.9)
        self.c = tk.Button(
            self.maincanvas,
            text="Create new project",
            command=lambda: self.new_proj(),
            bg="#eff3f6",
            font=("Helvetica 12 bold"),
            fg="#2F4858",
        )
        self.c.place(relx=0.62, rely=0.9)

    # def getFolderPath(self):
    #     self.top.attributes("-topmost", False)
    #     folder_selected = tk.filedialog.askdirectory()
    #     self.folderPath.set(folder_selected)
    #     os.chdir(self.folderPath.get())

    def load_proj(self):
        global proj_dir
        os.chdir(POLYCHRON_PROJECTS_DIR)
        [
            x.destroy()
            for x in [
                self.label1,
                self.greeting,
                self.b,
                self.c,
                self.back,
                self.l,
                self.back1,
                self.MyListBox,
                self.text_1,
                self.user_input,
            ]
            if x is not None
        ]
        self.maincanvas.update()

        self.l = tk.Label(self.maincanvas, text="Select project", bg="white", font=("helvetica 14 bold"), fg="#2F4858")
        self.l.place(relx=0.36, rely=0.1)
        myList = [d for d in os.listdir(POLYCHRON_PROJECTS_DIR) if os.path.isdir(d)]
        myList = [d for d in myList if (d != "__pycache__") and (d != "Data")]
        mylist_var = tk.StringVar(value=myList)
        self.MyListBox = tk.Listbox(
            self.maincanvas,
            listvariable=mylist_var,
            bg="#eff3f6",
            font=("Helvetica 11 bold"),
            fg="#2F4858",
            selectmode="browse",
        )
        scrollbar = ttk.Scrollbar(self.maincanvas, orient="vertical", command=self.MyListBox.yview)
        self.MyListBox["yscrollcommand"] = scrollbar.set
        self.MyListBox.place(relx=0.36, rely=0.17, relheight=0.4, relwidth=0.28)
        self.MyListBox.bind("<<ListboxSelect>>", self.items_selected)
        self.b = tk.Button(
            self.maincanvas,
            text="Load project",
            command=lambda: self.load_model(proj_dir),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.b.place(relx=0.8, rely=0.9, relwidth=0.19)
        self.top.bind("<Return>", (lambda event: self.load_model(proj_dir)))
        self.back = tk.Button(
            self.maincanvas,
            text="Back",
            command=lambda: self.initscreen(),
            bg="#eff3f6",
            font=("Helvetica 12 bold"),
            fg="#2F4858",
        )
        self.back.place(relx=0.21, rely=0.01)

    def load_model(self, direc):
        global proj_dir
        [
            x.destroy()
            for x in [self.greeting, self.label1, self.b, self.c, self.back, self.back1, self.l, self.MyListBox]
            if x is not None
        ]
        if self.selected_langs is None:
            path = direc
        else:
            path = os.getcwd() + "/" + self.selected_langs
        os.chdir(path)
        self.maincanvas.update()

        self.l = tk.Label(self.maincanvas, text="Model list", bg="white", font=("helvetica 14 bold"), fg="#2F4858")
        self.l.place(relx=0.36, rely=0.1)
        # myList_all = os.listdir(POLYCHRON_PROJECTS_DIR)
        myList = [d for d in os.listdir(path) if os.path.isdir(d)]
        self.model_list = tk.StringVar(value=myList)
        self.MyListBox = tk.Listbox(
            self.maincanvas,
            listvariable=self.model_list,
            bg="#eff3f6",
            font=("Helvetica 11 bold"),
            fg="#2F4858",
            selectmode="browse",
        )
        scrollbar = ttk.Scrollbar(self.maincanvas, orient="vertical", command=self.MyListBox.yview)
        self.MyListBox["yscrollcommand"] = scrollbar.set
        self.MyListBox.place(relx=0.36, rely=0.17, relheight=0.4, relwidth=0.28)
        self.MyListBox.bind("<<ListboxSelect>>", self.items_selected)
        self.b = tk.Button(
            self.maincanvas,
            text="Load selected model",
            command=lambda: self.cleanup2(),
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.top.bind("<Return>", (lambda event: self.cleanup2()))
        self.b.place(relx=0.8, rely=0.9, relwidth=0.195)
        self.back = tk.Button(
            self.maincanvas,
            text="Back",
            command=lambda: self.initscreen(),
            bg="#eff3f6",
            font=("Helvetica 12 bold"),
            fg="#2F4858",
        )
        self.back.place(relx=0.21, rely=0.01)
        self.back1 = tk.Button(
            self.maincanvas,
            text="Create new model",
            command=lambda: self.new_model(path),
            bg="#eff3f6",
            font=("Helvetica 12 bold"),
            fg="#2F4858",
        )
        self.back1.place(relx=0.62, rely=0.9, relwidth=0.17)
        proj_dir = path

    def items_selected(self, event):
        """handle item selected event"""
        # get selected indices
        selected_indices = self.MyListBox.curselection()
        # get selected items
        self.selected_langs = ",".join([self.MyListBox.get(i) for i in selected_indices])

    def create_file(self, folder_dir, load):
        global proj_dir
        dirs = os.path.join(POLYCHRON_PROJECTS_DIR, folder_dir, self.model.get())
        dirs2 = os.path.join(dirs, "stratigraphic_graph")
        dirs3 = os.path.join(dirs, "chronological_graph")
        dirs4 = os.path.join(dirs, "python_only")
        dirs5 = os.path.join(dirs, "mcmc_results")
        if not os.path.exists(dirs):
            #     os.makedirs(dirs)
            os.makedirs(dirs)
            os.makedirs(dirs2)
            os.makedirs(dirs3)
            os.makedirs(dirs4)
            os.makedirs(dirs5)
            os.chdir(dirs)
            proj_dir = os.path.join(POLYCHRON_PROJECTS_DIR, folder_dir)
            if load:
                for F in (StartPage, PageOne):
                    page_name = F.__name__
                    frame = F(parent=self.master.container, controller=self.master)
                    self.master.frames[page_name] = frame

                    # put all of the pages in the same location;
                    # the one on the top of the stacking order
                    # will be the one that is visible.
                    frame.grid(row=0, column=0, sticky="nsew")
                    self.master.show_frame("StartPage")
            self.cleanup()
            tk.messagebox.showinfo("Tips:", "model created successfully!")
            os.chdir(dirs)
        else:
            tk.messagebox.showerror("Tips", "The folder name exists, please change it")
            self.cleanup()

    def new_proj(self):
        [
            x.destroy()
            for x in [
                self.greeting,
                self.label1,
                self.b,
                self.back1,
                self.c,
                self.back,
                self.l,
                self.MyListBox,
                self.text_1,
                self.user_input,
            ]
            if x is not None
        ]
        self.maincanvas.update()
        self.folder = tk.StringVar()  # Receiving user's folder_name selection
        self.text_1 = tk.Label(
            self.maincanvas, text="Input project name:", bg="white", font=("helvetica 14 bold"), fg="#2F4858"
        )
        self.text_1.place(relx=0.4, rely=0.2)
        self.user_input = tk.Entry(self.maincanvas, textvariable=self.folder)
        self.user_input.place(relx=0.35, rely=0.4, relwidth=0.3, relheight=0.08)
        self.b = tk.Button(
            self.maincanvas,
            text="Submit ",
            command=lambda: self.new_model(self.folder.get()),
            bg="#ec9949",
            font=("Helvetica 12 bold"),
            fg="#2F4858",
        )
        self.top.bind("<Return>", (lambda event: self.new_model(self.folder.get())))
        self.b.place(relx=0.66, rely=0.4)
        self.back = tk.Button(
            self.maincanvas,
            text="Back",
            command=lambda: self.initscreen(),
            bg="#dcdcdc",
            font=("helvetica 12 bold"),
            fg="#2F4858",
        )
        self.back.place(relx=0.21, rely=0.01)

    def new_model(self, folder_dir, load=True):
        [
            x.destroy()
            for x in [
                self.greeting,
                self.label1,
                self.b,
                self.c,
                self.back,
                self.back1,
                self.l,
                self.MyListBox,
                self.text_1,
                self.user_input,
            ]
            if x is not None
        ]
        self.maincanvas.update()
        self.model = tk.StringVar()  # Receiving user's folder_name selection
        self.text_1 = tk.Label(
            self.maincanvas, text="Input model name:", bg="white", font=("helvetica 14 bold"), fg="#2F4858"
        )
        self.text_1.place(relx=0.4, rely=0.2)
        self.user_input = tk.Entry(self.maincanvas, textvariable=self.model)
        self.user_input.place(relx=0.35, rely=0.4, relwidth=0.3, relheight=0.08)
        self.b = tk.Button(
            self.maincanvas,
            text="Submit ",
            command=lambda: self.create_file(folder_dir, load),
            bg="#ec9949",
            font=("Helvetica 12 bold"),
            fg="#2F4858",
        )
        self.b.place(relx=0.66, rely=0.4)
        self.top.bind("<Return>", (lambda event: self.create_file(folder_dir, load)))
        self.back = tk.Button(
            self.maincanvas,
            text="Back",
            command=lambda: self.new_proj(),
            bg="#dcdcdc",
            font=("helvetica 12 bold"),
            fg="#2F4858",
        )
        self.back.place(relx=0.21, rely=0.01)
        return self.top

    def cleanup(self):
        self.top.destroy()

    def cleanup2(self):
        path = os.getcwd() + "/" + self.selected_langs
        os.chdir(path)
        for F in (StartPage, PageOne):
            page_name = F.__name__
            frame = F(parent=self.master.container, controller=self.master)
            self.master.frames[page_name] = frame
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        self.master.show_frame("StartPage")
        self.top.destroy()


class StartPage(tk.Frame):
    """Main frame for tkinter app"""

    def __init__(self, parent, controller):
        global load_check, mcmc_check, FILE_INPUT, proj_dir
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(background="white")
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg="#AEC7D6")
        self.canvas.place(relx=0, rely=0.03, relwidth=1, relheight=0.97)
        self.button1 = tk.Button(
            self,
            text="Stratigraphy and supplementary data",
            font="helvetica 12 bold",
            fg="#2F4858",
            command=lambda: controller.show_frame("StartPage"),
            bd=0,
            highlightthickness=0,
            bg="#AEC7D6",
        )
        self.button1.place(relx=0.38, rely=0.0, relwidth=0.17, relheight=0.03)
        self.button1_a = tk.Button(
            self,
            text="Dating Results",
            font="helvetica 12 bold",
            fg="#8F4300",
            command=lambda: controller.show_frame("PageOne"),
            bd=0,
            highlightthickness=0,
            bg="#FFE9D6",
        )
        self.button1_a.place(relx=0.55, rely=0.0, relwidth=0.15, relheight=0.03)
        # define all variables that are used
        self.h_1 = 0
        self.w_1 = 0

        self.transx = 0
        self.transy = 0
        self.meta1 = ""
        self.mode = ""
        self.node_del_tracker = []
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
        self.image2 = "noimage"
        self.resultsdict = {}
        self.all_results_dict = {}
        self.treeview_df = pd.DataFrame()
        self.file_menubar = ttk.Menubutton(self, text="File")
        self.strat_check = False
        self.phase_check = False
        self.phase_rel_check = False
        self.date_check = False
        # Adding File Menu and commands
        file = tk.Menu(self.file_menubar, tearoff=0, bg="white", font=("helvetica 12 bold"))
        self.file_menubar["menu"] = file
        file.add_separator()
        FILE_INPUT = None
        file.add_command(
            label="Load stratigraphic diagram file (.dot)", command=lambda: self.open_file1(), font="helvetica 12 bold"
        )
        file.add_command(
            label="Load stratigraphic relationship file (.csv)",
            command=lambda: self.open_file2(),
            font="helvetica 12 bold",
        )
        file.add_command(
            label="Load scientific dating file (.csv)", command=lambda: self.open_file3(), font="helvetica 12 bold"
        )
        file.add_command(
            label="Load context grouping file (.csv)", command=lambda: self.open_file4(), font="helvetica 12 bold"
        )
        file.add_command(
            label="Load group relationship file (.csv)", command=lambda: self.open_file5(), font="helvetica 12 bold"
        )
        file.add_command(
            label="Load context equalities file (.csv)", command=lambda: self.open_file6(), font="helvetica 12 bold"
        )
        file.add_command(label="Load new project", command=lambda: load_Window(MAIN_FRAME), font="helvetica 12 bold")
        file.add_command(
            label="Load existing model",
            command=lambda: load_Window.load_model(load_Window(MAIN_FRAME), proj_dir),
            font="helvetica 12 bold",
        )
        file.add_command(
            label="Save changes as current model", command=lambda: self.save_state_1(), font="helvetica 12 bold"
        )
        file.add_command(
            label="Save changes as new model",
            command=lambda: self.refresh_4_new_model(controller, proj_dir, load=False),
            font="helvetica 12 bold",
        )
        file.add_separator()
        file.add_command(label="Exit", command=lambda: self.destroy1)
        self.file_menubar.place(relx=0.00, rely=0, relwidth=0.1, relheight=0.03)
        self.view_menubar = ttk.Menubutton(self, text="View")
        # Adding File Menu and commands
        file1 = tk.Menu(self.view_menubar, tearoff=0, bg="white", font=("helvetica", 11))
        self.view_menubar["menu"] = file1
        file1.add_command(
            label="Display Stratigraphic diagram in phases", command=lambda: self.phasing(), font="helvetica 11"
        )
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)

        self.tool_menubar = ttk.Menubutton(self, text="Tools")
        # Adding File Menu and commands
        file2 = tk.Menu(self.tool_menubar, tearoff=0, bg="white", font=("helvetica", 11))
        self.tool_menubar["menu"] = file2
        # file2.add_separator()
        file2.add_command(
            label="Render chronological graph", command=lambda: self.chronograph_render_wrap(), font="helvetica 12 bold"
        )
        file2.add_command(label="Calibrate model", command=lambda: self.load_mcmc(), font="helvetica 12 bold")
        file2.add_command(
            label="Calibrate multiple projects from project",
            command=lambda: popupWindow8(self, proj_dir),
            font="helvetica 12 bold",
        )
        file2.add_command(
            label="Calibrate node delete variations (alpha)",
            command=lambda: popupWindow9(self, proj_dir),
            font="helvetica 12 bold",
        )
        file2.add_command(
            label="Calibrate important variations (alpha)",
            command=lambda: popupWindow10(self, proj_dir),
            font="helvetica 12 bold",
        )

        # file2.add_separator()
        self.tool_menubar.place(relx=0.14, rely=0, relwidth=0.1, relheight=0.03)
        #############################
        self.behindcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas.place(relx=0.003, rely=0.038, relwidth=0.37, relheight=0.96)
        ############################
        self.behindcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas2.place(relx=0.38, rely=0.038, relwidth=0.37, relheight=0.96)
        ######################
        self.labelcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas.place(relx=0.003, rely=0.011, relwidth=0.18, relheight=0.027)
        self.labelcanvas1_id = self.labelcanvas.create_text(10, 3, anchor="nw", fill="white")
        self.labelcanvas.itemconfig(self.labelcanvas1_id, text="Stratigraphic graph", font="helvetica 12 bold")
        #########################
        self.littlecanvas = tk.Canvas(
            self.behindcanvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_id = self.littlecanvas.create_text(10, 10, anchor="nw", fill="#2f4845")
        self.littlecanvas.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        self.littlecanvas.itemconfig(
            self.littlecanvas_id,
            text="No stratigraphic graph loaded. \n \n \nTo load, go to File > Load stratigraphic diagram",
            font="helvetica 12 bold",
        )
        self.littlecanvas.update()
        ##############################

        #################
        self.littlecanvas2 = tk.Canvas(
            self.behindcanvas2, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas2_id = self.littlecanvas2.create_text(10, 10, anchor="nw", fill="#2f4845")
        self.littlecanvas2.itemconfig(
            self.littlecanvas2_id,
            text="No chronological graph loaded. \n \n \nYou must load a stratigraphic graph first. \nTo load, go to File > Load stratigraphic diagram \nTo load your chronological graph, go to Tools > Render chronological graph",
            font="helvetica 12 bold",
        )
        self.littlecanvas2.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        ##########################
        self.labelcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas2.place(relx=0.38, rely=0.011, relwidth=0.18, relheight=0.027)
        self.labelcanvas2_id = self.labelcanvas2.create_text(10, 3, anchor="nw", fill="white")
        self.labelcanvas2.itemconfig(self.labelcanvas2_id, text="Chronological graph", font="helvetica 12 bold")
        ###################
        self.littlecanvas.bind("<MouseWheel>", self.wheel)
        self.littlecanvas.bind("<Button-4>", self.wheel)  # only with Linux, wheel scroll down
        self.littlecanvas.bind("<Button-5>", self.wheel)
        self.littlecanvas.bind("<Button-1>", self.move_from)
        self.littlecanvas.bind("<B1-Motion>", self.move_to)

        self.littlecanvas2.bind("<MouseWheel>", self.wheel2)
        self.littlecanvas2.bind("<Button-4>", self.wheel2)  # only with Linux, wheel scroll down
        self.littlecanvas2.bind("<Button-5>", self.wheel2)
        self.littlecanvas2.bind("<Button-1>", self.move_from2)
        self.littlecanvas2.bind("<B1-Motion>", self.move_to2)
        # placing image on littlecanvas from graph
        self.littlecanvas.rowconfigure(0, weight=1)
        self.littlecanvas.columnconfigure(0, weight=1)
        self.littlecanvas2.rowconfigure(0, weight=1)
        self.littlecanvas2.columnconfigure(0, weight=1)
        self.littlecanvas2.update()

        ######node delete##########
        self.OptionList = [
            "Delete context",
            "Delete stratigraphic relationship",
            "Get supplementary data for this context",
            "Equate context with another",
            "Place above other context",
            "Add new contexts",
            "Supplementary data menu (BROKEN)",
        ]
        self.variable = tk.StringVar(self.littlecanvas)
        self.variable.set("Node Action")
        self.testmenu = ttk.OptionMenu(
            self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes
        )
        # meta data table
        self.labelcanvas3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas3.place(relx=0.755, rely=0.695, relwidth=0.17, relheight=0.029)
        self.behindcanvas3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas3.place(relx=0.755, rely=0.719, relwidth=0.23, relheight=0.278)
        self.metatext_id = self.labelcanvas3.create_text(10, 5, anchor="nw", fill="white")
        self.labelcanvas3.itemconfig(self.metatext_id, text="Supplementary data", font="helvetica 12 bold")
        self.tree1 = ttk.Treeview(self.canvas)
        self.tree1["columns"] = ["Data"]
        self.tree1.place(relx=0.758, rely=0.725)
        self.tree1.column("Data", anchor="w")
        self.tree1.heading("Data", text="Data")
        # deleted contexts table
        self.labelcanvas4 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas4.place(relx=0.755, rely=0.04, relwidth=0.17, relheight=0.029)
        self.behindcanvas4 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas4.place(relx=0.755, rely=0.069, relwidth=0.23, relheight=0.278)
        self.delcontext_id = self.labelcanvas4.create_text(10, 5, anchor="nw", fill="white")
        self.labelcanvas4.itemconfig(self.delcontext_id, text="Deleted Contexts", font="helvetica 12 bold")
        self.tree2 = ttk.Treeview(self.canvas)

        self.tree2.heading("#0", text="Context")
        self.tree2["columns"] = ["Meta"]
        self.tree2.place(relx=0.758, rely=0.0729)
        self.tree2.column("Meta", anchor="w")
        self.tree2.heading("Meta", text="Reason for deleting")

        # deleted edges table
        self.labelcanvas5 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.labelcanvas5.place(relx=0.755, rely=0.371, relwidth=0.17, relheight=0.029)
        self.behindcanvas5 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#33658a")
        self.behindcanvas5.place(relx=0.755, rely=0.399, relwidth=0.23, relheight=0.278)
        self.deledge_id = self.labelcanvas5.create_text(10, 5, anchor="nw", fill="white")
        self.labelcanvas5.itemconfig(
            self.deledge_id, text="Deleted Stratigraphic Relationships", font="helvetica 12 bold"
        )
        self.tree3 = ttk.Treeview(self.canvas)
        self.tree3.heading("#0", text="Stratigraphic relationship")
        self.tree3["columns"] = ["Meta"]
        self.tree3.place(relx=0.758, rely=0.405)
        self.tree3.heading("Meta", text="Reason for deleting")
        f = dir(self)
        self.f_1 = [var for var in f if ("__" or "grid" or "get") not in var]
        self.littlecanvas.update()
        try:
            self.restore_state()
        except FileNotFoundError:
            self.save_state_1()
        self.databutton = tk.Button(
            self,
            text="Data loaded  ↙",
            font="helvetica 12 bold",
            fg="white",
            command=lambda: self.display_data_func(),
            bd=0,
            highlightthickness=0,
            bg="#33658a",
        )
        self.databutton.place(relx=0.303, rely=0.04, relwidth=0.07, relheight=0.028)
        self.datacanvas = tk.Canvas(self.behindcanvas, bd=0, highlightthickness=0, bg="#33658a")
        self.datacanvas.place(relx=0.55, rely=0.0, relwidth=0.45, relheight=0.2)
        self.datalittlecanvas = tk.Canvas(
            self.datacanvas, bd=8, bg="white", highlightbackground="#33658a", highlightthickness=5
        )
        self.datalittlecanvas.place(relx=0.015, rely=0.015, relwidth=0.97, relheight=0.97)
        self.display_data_var = "hidden"
        self.check_list_gen()
        tk.Misc.lift(self.littlecanvas)

    def refresh_4_new_model(self, controller, proj_dir, load):
        extra_top = load_Window.new_model(load_Window(MAIN_FRAME), proj_dir, load)
        self.wait_window(extra_top)

    #       self.save_state_1()

    def display_data_func(self):
        if self.display_data_var == "hidden":
            tk.Misc.lift(self.datacanvas)
            self.databutton["text"] = "Data loaded ↗"
            self.display_data_var = "onshow"
        else:
            if self.display_data_var == "onshow":
                tk.Misc.lift(self.littlecanvas)
                self.databutton["text"] = "Data loaded  ↙"
                self.display_data_var = "hidden"

    def check_list_gen(self):
        if self.strat_check:
            strat = "‣ Stratigraphic relationships"
            col1 = "green"
        else:
            strat = "‣ Stratigraphic relationships"
            col1 = "black"
        if self.date_check:
            date = "‣ Radiocarbon dates"
            col2 = "green"
        else:
            date = "‣ Radiocarbon dates"
            col2 = "black"
        if self.phase_check:
            phase = "‣ Groups for contexts"
            col3 = "green"
        else:
            phase = "‣ Groups for contexts"
            col3 = "black"
        if self.phase_rel_check:
            rels = "‣ Relationships between groups"
            col4 = "green"
        else:
            rels = "‣ Relationships between groups"
            col4 = "black"
        self.datalittlecanvas.delete("all")
        self.datalittlecanvas.create_text(
            10, 20, anchor="nw", text=strat + "\n\n", font=("Helvetica 12 bold"), fill=col1
        )
        self.datalittlecanvas.pack()
        self.datalittlecanvas.create_text(
            10, 50, anchor="nw", text=date + "\n\n", font=("Helvetica 12 bold"), fill=col2
        )
        self.datalittlecanvas.pack()
        self.datalittlecanvas.create_text(
            10, 80, anchor="nw", text=phase + "\n\n", font=("Helvetica 12 bold"), fill=col3
        )
        self.datalittlecanvas.pack()
        self.datalittlecanvas.create_text(10, 110, anchor="nw", text=rels, font=("Helvetica 12 bold"), fill=col4)
        self.datalittlecanvas.pack()

    def destroy1(self):
        """destroys self.testmenu"""
        self.menubar.place_forget()

    def resid_check(self):
        """Loads a text box to check if the user thinks any samples are residual"""
        global load_check
        MsgBox = tk.messagebox.askquestion(
            "Residual and Intrusive Contexts",
            "Do you suspect any of your samples are residual or intrusive?",
            icon="warning",
        )
        if MsgBox == "yes":
            pagetwo = PageTwo(self, self.controller)
            self.popup3 = pagetwo.popup4

        else:
            self.popup3 = popupWindow3(self, self.graph, self.littlecanvas2, self.phase_rels)

        def destroy(self):
            """destroys self.testmenu"""
            self.testmenu.place_forget()

        #    # This is the function that removes the selected item when the label is clicked.
        def delete(self, *args):
            """uses destroy then sets self.variable"""
            self.destroy()
            self.testmenu.place_forget()
            self.variable.set("Node Action")

    def save_state_1(self):
        global mcmc_check, load_check, FILE_INPUT
        # converting metadata treeview to dataframe
        row_list = []
        columns = ("context", "Reason for deleting")
        for child in self.tree2.get_children():
            row_list.append((self.tree2.item(child)["text"], self.tree2.item(child)["values"]))
        self.treeview_df = pd.DataFrame(row_list, columns=columns)
        vars_list_1 = dir(self)
        #      self.node_importance(self.graph)
        var_list = [
            var
            for var in vars_list_1
            if (("__" and "grid" and "get" and "tkinter" and "children") not in var) and (var[0] != "_")
        ]
        data = {}
        # Type names to not pickle when saving state. PolyChron is excluded to avoid classes which inherit from tk, this may be a bit too strong.
        check_list = ["tkinter", "method", "__main__", "PIL", "PolyChron"]

        for i in var_list:
            v = getattr(self, i)
            if not any(x in str(type(v)) for x in check_list):
                data[i] = v
        data["all_vars"] = list(data.keys())
        data["load_check"] = load_check
        data["mcmc_check"] = mcmc_check
        data["file_input"] = FILE_INPUT
        if mcmc_check == "mcmc_loaded":
            results = data["all_results_dict"]
            df = pd.DataFrame()
            for i in results.keys():
                df[i] = results[i][10000:]
            results_path = os.getcwd() + "/mcmc_results/full_results_df"
            df.to_csv(results_path)
            phasefile = data["phasefile"]
            context_no = data["CONTEXT_NO"]
            key_ref = [list(phasefile["Group"])[list(phasefile["context"]).index(i)] for i in context_no]
            df1 = pd.DataFrame(key_ref)
            df1.to_csv("mcmc_results/key_ref.csv")
            df2 = pd.DataFrame(context_no)
            df2.to_csv("mcmc_results/context_no.csv")
        path = os.getcwd() + "/python_only/save.pickle"
        path2 = os.getcwd() + "/stratigraphic_graph/deleted_contexts_meta"
        self.treeview_df.to_csv(path2)
        try:
            with open(path, "wb") as f:
                pickle.dump(data, f)
        except Exception as e:
            print("error saving state:", str(e))

    def restore_state(self):
        global mcmc_check, load_check, FILE_INPUT
        with open("python_only/save.pickle", "rb") as f:
            data = pickle.load(f)
            vars_list = data["all_vars"]
            for i in vars_list:
                setattr(self, i, data[i])
            FILE_INPUT = data["file_input"]
            load_check = data["load_check"]
            mcmc_check = data["mcmc_check"]
        if self.graph is not None:
            self.littlecanvas.delete("all")
            self.rerender_stratdag()
            for i, j in enumerate(self.treeview_df["context"]):
                self.tree2.insert("", "end", text=j, values=self.treeview_df["Reason for deleting"][i])

        if load_check == "loaded":
            FILE_INPUT = None
            # manaually work this out as canvas hasn't rendered enough at this point to have a height and width in pixels
            height = 0.96 * 0.99 * 0.97 * 1000 * 0.96
            width = 0.99 * 0.37 * 2000 * 0.96
            self.image2 = imgrender2(width, height)
            if self.image2 != "No_image":
                self.littlecanvas2.delete("all")
                self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
                self.littlecanvas2_img = self.littlecanvas2.create_image(
                    0, 0, anchor="nw", image=self.littlecanvas2.img
                )

                self.width2, self.height2 = self.image2.size
                #  self.imscale2 = 1.0  # scale for the canvaas image
                self.delta2 = 1.1  # zoom magnitude
                # Put image into container rectangle and use it to set proper coordinates to the image
                self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
                self.imscale2 = min(921 / self.image2.size[0], 702 / self.image2.size[1])
                self.littlecanvas.scale("all", 0, 0, self.delta2, self.delta2)  # rescale all canvas objects
                self.show_image2()

                self.littlecanvas2.bind("<Configure>", self.resize2)

    def onRight(self, *args):
        """makes test menu appear after right click"""
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
        self.testmenuWidth = len(max(self.OptionList, key=len))
        self.testmenu.config(width=self.testmenuWidth)
        # This function is for removing the canvas when an option is clicked.

    def preClick(self, *args):
        """makes test menu appear and removes any previous test menu"""
        try:
            self.testmenu.place_forget()
            self.onRight()
        except Exception:
            self.onRight()

    # Hide menu when left clicking
    def onLeft(self, *args):
        """hides menu when left clicking"""
        try:
            self.testmenu.place_forget()
        except Exception:
            pass

    def file_popup(self, file):
        self.nodedel = popupWindow7(self.canvas, file)
        self.canvas["state"] = "disabled"
        self.master.wait_window(self.nodedel.top)
        self.canvas["state"] = "normal"
        return self.nodedel.value

    def open_file1(self):
        """opens dot file"""
        global node_df, FILE_INPUT, phase_true
        file = askopenfile(mode="r", filetypes=[("Python Files", "*.dot")])
        FILE_INPUT = file.name
        self.graph = nx.DiGraph(imagefunc(file.name), graph_attr={"splines": "ortho"})
        if phase_true == 1:
            self.image = imgrender_phase(self.graph)
        else:
            self.image = imgrender(self.graph)
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw", image=self.littlecanvas.img)

        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
        #  self.imscale  = min(921/self.image.size[0], 702/self.image.size[1])
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.bind("<Configure>", self.resize)
        self.littlecanvas.scale("all", 0, 0, self.delta, self.delta)  # rescale all canvas objects
        self.show_image()
        self.littlecanvas.bind("<Configure>", self.resize)
        self.delnodes = []
        self.delnodes_meta = []
        self.canvas.delete("all")
        self.littlecanvas.bind("<Button-3>", self.preClick)

    def rerender_stratdag(self):
        global phase_true
        """rerenders stratdag after reloading previous project"""
        height = 0.96 * 0.99 * 0.97 * 1000
        width = 0.99 * 0.37 * 2000 * 0.96
        if phase_true == 1:
            self.image = imgrender_phase(self.graph)
        else:
            self.image = imgrender(self.graph, width, height)

        #       self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw", image=self.littlecanvas.img)

        self.width, self.height = self.image.size
        #   self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.imscale = min(width / self.image.size[0], height / self.image.size[1])

        self.delnodes = []
        self.delnodes_meta = []
        self.littlecanvas.bind("<Button-3>", self.preClick)
        self.littlecanvas.update()
        self.littlecanvas.scale("all", 0, 0, self.delta, self.delta)  # rescale all canvas objects
        self.show_image()

    def chronograph_render_wrap(self):
        """wraps chronograph render so we can assign a variable when runing the func using a button"""
        global load_check
        if (self.phase_rels is None) or (self.phasefile is None) or (self.datefile is None):
            tk.messagebox.showinfo("Error", "You haven't loaded in all the data required for a chronological graph")
        if load_check == "loaded":
            answer = askquestion(
                "Warning!",
                "Chronological DAG already loaded, are you sure you want to write over it? You can copy this model in the file menu if you want to consider multiple models",
            )
            if answer == "yes":
                self.refresh_4_new_model(self.controller, proj_dir, load=False)
                load_check = "not_loaded"
                self.littlecanvas2.delete("all")
                self.chrono_dag = self.chronograph_render()
                startpage = self.controller.get_page("StartPage")
                startpage.CONT_TYPE = self.popup3.CONT_TYPE
                startpage.prev_phase = self.popup3.prev_phase
                startpage.post_phase = self.popup3.post_phase
                startpage.phi_ref = self.popup3.phi_ref
                startpage.context_no_unordered = self.popup3.context_no_unordered
                startpage.graphcopy = self.popup3.graphcopy
                startpage.node_del_tracker = self.popup3.node_del_tracker

        else:
            self.littlecanvas2.delete("all")
            self.chrono_dag = self.chronograph_render()
            startpage = self.controller.get_page("StartPage")
            startpage.CONT_TYPE = self.popup3.CONT_TYPE
            startpage.prev_phase = self.popup3.prev_phase
            startpage.post_phase = self.popup3.post_phase
            startpage.phi_ref = self.popup3.phi_ref
            startpage.context_no_unordered = self.popup3.context_no_unordered
            startpage.graphcopy = self.popup3.graphcopy
            startpage.node_del_tracker = self.popup3.node_del_tracker

    def open_file2(self):
        """opens plain text strat file"""
        global FILE_INPUT, phase_true
        file = askopenfile(mode="r", filetypes=[("Python Files", "*.csv")])
        if file is not None:
            try:
                FILE_INPUT = None
                self.littlecanvas.delete("all")
                self.stratfile = pd.read_csv(file, dtype=str)
                load_it = self.file_popup(self.stratfile)
                if load_it == "load":
                    self.strat_check = True
                    G = nx.DiGraph(graph_attr={"splines": "ortho"})
                    set1 = set(self.stratfile.iloc[:, 0])
                    set2 = set(self.stratfile.iloc[:, 1])
                    set2.update(set1)
                    node_set = {x for x in set2 if x == x}
                    for i in set(node_set):
                        G.add_node(i, shape="box", fontname="helvetica", fontsize="30.0", penwidth="1.0", color="black")
                        G.nodes()[i].update({"Determination": [None, None]})
                        G.nodes()[i].update({"Group": None})
                    edges = []
                    for i in range(len(self.stratfile)):
                        a = tuple(self.stratfile.iloc[i, :])
                        if not pd.isna(a[1]):
                            edges.append(a)
                    G.add_edges_from(edges, arrowhead="none")
                    self.graph = G
                    if phase_true == 1:
                        self.image = imgrender_phase(self.graph)
                    else:
                        self.image = imgrender(
                            self.graph, self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height()
                        )

                        #     scale_factor = min(self.littlecanvas.winfo_width()/self.image_ws.size[0], self.littlecanvas.winfo_height()/self.image_ws.size[1])
                        #     self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
                        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
                        self.littlecanvas_img = self.littlecanvas.create_image(
                            0, 0, anchor="nw", image=self.littlecanvas.img
                        )
                        self.width, self.height = self.image.size
                        #     self.imscale = 1.0#, self.littlecanvas.winfo_height()/self.image.size[1])# scale for the canvaas image
                        self.delta = 1.1  # zoom magnitude
                        # Put image into container rectangle and use it to set proper coordinates to the image
                        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
                        self.bind("<Configure>", self.resize)
                        self.littlecanvas.bind("<Configure>", self.resize)
                        self.delnodes = []
                        self.delnodes_meta = []
                        self.littlecanvas.bind("<Button-3>", self.preClick)
                        self.imscale = min(921 / self.image.size[0], 702 / self.image.size[1])
                        self.littlecanvas.scale("all", 0, 0, self.delta, self.delta)  # rescale all canvas objects
                        self.show_image()
                    tk.messagebox.showinfo("Success", "Stratigraphic data loaded")
                    self.check_list_gen()
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_file3(self):
        """opens scientific dating file"""
        file = askopenfile(mode="r", filetypes=[("Python Files", "*.csv")])
        if file is not None:
            try:
                self.datefile = pd.read_csv(file)
                self.datefile = self.datefile.applymap(str)
                load_it = self.file_popup(self.datefile)
                if load_it == "load":
                    for i, j in enumerate(self.datefile["context"]):
                        self.graph.nodes()[str(j)].update(
                            {"Determination": [self.datefile["date"][i], self.datefile["error"][i]]}
                        )
                    self.context_no_unordered = list(self.graph.nodes())
                self.date_check = True
                self.check_list_gen()
                tk.messagebox.showinfo("Success", "Scientific dating data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_file4(self):
        """opens phase file"""
        file = askopenfile(mode="r", filetypes=[("Pythotransxn Files", "*.csv")])
        if file is not None:
            try:
                self.phasefile = pd.read_csv(file)
                self.phasefile = self.phasefile.applymap(str)
                load_it = self.file_popup(self.phasefile)
                if load_it == "load":
                    for i, j in enumerate(self.phasefile["context"]):
                        self.graph.nodes()[str(j)].update({"Group": self.phasefile["Group"][i]})
                self.phase_check = True
                self.check_list_gen()
                tk.messagebox.showinfo("Success", "Grouping data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_file5(self):
        """opens phase relationship files"""
        file = askopenfile(mode="r", filetypes=[("Python Files", "*.csv")])
        if file is not None:
            try:
                phase_rel_df = pd.read_csv(file)
                self.phase_rels = [
                    (str(phase_rel_df["above"][i]), str(phase_rel_df["below"][i])) for i in range(len(phase_rel_df))
                ]
                self.file_popup(pd.DataFrame(self.phase_rels, columns=["Younger group", "Older group"]))
                self.phase_rel_check = True
                self.check_list_gen()
                tk.messagebox.showinfo("Success", "Group relationships data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_file6(self):
        """opens files determining equal contexts (in time)"""
        global phase_true
        file = askopenfile(mode="r", filetypes=[("Python Files", "*.csv")])
        if file is not None:
            try:
                equal_rel_df = pd.read_csv(file)
                self.equal_rel_df = equal_rel_df.applymap(str)
                context_1 = list(self.equal_rel_df.iloc[:, 0])
                context_2 = list(self.equal_rel_df.iloc[:, 1])
                for k, j in enumerate(context_1):
                    self.graph = nx.contracted_nodes(self.graph, j, context_2[k])
                    x_nod = list(self.graph)
                    newnode = str(j) + " = " + str(context_2[k])
                    y_nod = [newnode if i == j else i for i in x_nod]
                    mapping = dict(zip(x_nod, y_nod))
                    self.graph = nx.relabel_nodes(self.graph, mapping)
                if phase_true == 1:
                    imgrender_phase(self.graph)
                else:
                    imgrender(self.graph, self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
                self.image = Image.open("testdag.png")
                #   scale_factor = min(self.littlecanvas.winfo_width()/self.image_ws.size[0], self.littlecanvas.winfo_height()/self.image_ws.size[1])
                #   self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
                self.width, self.height = self.image.size
                self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
                self.show_image()
                tk.messagebox.showinfo("Success", "Equal contexts data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def cleanup(self):
        """destroys mcmc loading page when done"""
        self.top.destroy()

    def load_mcmc(self):
        """loads mcmc loading page"""
        global mcmc_check
        self.top = tk.Toplevel(self.littlecanvas)
        self.backcanvas = tk.Canvas(self.top, bg="#AEC7D6")
        self.backcanvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.top.geometry("%dx%d%+d%+d" % (700, 200, 600, 400))
        self.l = tk.Label(
            self.backcanvas, text="MCMC in progress", font=("helvetica 14 bold"), fg="#2F4858", bg="#AEC7D6"
        )
        self.l.place(relx=0.35, rely=0.26)
        outputPanel = tk.Label(self.backcanvas, font=("helvetica 14 bold"), fg="#2F4858", bg="#AEC7D6")
        outputPanel.place(relx=0.4, rely=0.4)
        pb1 = ttk.Progressbar(self.backcanvas, orient=tk.HORIZONTAL, length=400, mode="indeterminate")
        pb1.place(relx=0.2, rely=0.56)
        old_stdout = sys.stdout
        sys.stdout = StdoutRedirector(outputPanel, pb1)
        self.ACCEPT = [[]]
        while min([len(i) for i in self.ACCEPT]) < 50000:
            (
                self.CONTEXT_NO,
                self.ACCEPT,
                self.PHI_ACCEPT,
                self.PHI_REF,
                self.A,
                self.P,
                self.ALL_SAMPS_CONT,
                self.ALL_SAMPS_PHI,
                self.resultsdict,
                self.all_results_dict,
            ) = self.MCMC_func()
        mcmc_check = "mcmc_loaded"
        sys.stdout = old_stdout
        self.controller.show_frame("PageOne")
        f = dir(self)
        self.f_2 = [var for var in f if ("__" or "grid" or "get") not in var]
        self.newvars = [var for var in self.f_2 if var not in self.f_1]
        self.cleanup()

    def addedge(self, edgevec):
        """adds an edge relationship (edgevec) to graph and rerenders the graph"""
        global node_df, phase_true
        x_1 = edgevec[0]
        x_2 = edgevec[1]
        self.graph.add_edge(x_1, x_2, arrowhead="none")
        self.graph_check = nx.transitive_reduction(self.graph)
        if self.graph.edges() != self.graph_check.edges():
            self.graph.remove_edge(x_1, x_2)
            tk.messagebox.showerror(
                "Redundant relationship",
                "That stratigraphic relationship is already implied by other relationships in the graph",
            )
        if phase_true == 1:
            imgrender_phase(self.graph)
        else:
            imgrender(self.graph, self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
        self.image = Image.open("testdag.png")
        self.show_image()

    def chronograph_render(self):
        """initiates residual checking function then renders the graph when thats done"""
        global load_check
        if load_check != "loaded":
            load_check = "loaded"
            self.resid_check()
            self.image2 = imgrender2(self.littlecanvas2.winfo_width(), self.littlecanvas2.winfo_height())
            if self.image2 != "No_image":
                try:
                    self.littlecanvas2.delete("all")
                    self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
                    self.littlecanvas2_img = self.littlecanvas2.create_image(
                        0, 0, anchor="nw", image=self.littlecanvas2.img
                    )

                    self.width2, self.height2 = self.image2.size
                    # self.imscale2 = 1.0  # scale for the canvaas image
                    self.delta2 = 1.1  # zoom magnitude
                    # Put image into container rectangle and use it to set proper coordinates to the image
                    self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
                    self.imscale2 = min(921 / self.image2.size[0], 702 / self.image2.size[1])
                    self.littlecanvas2.scale("all", 0, 0, self.delta2, self.delta2)  # rescale all canvas objects
                    self.show_image2()
                    self.littlecanvas2.bind("<Configure>", self.resize2)
                except (RuntimeError, TypeError, NameError):
                    load_check = "not_loaded"
        return self.popup3.graphcopy

    def stratfunc(self, node):
        """obtains strat relationships for node"""
        rellist = list(nx.line_graph(self.graph))
        above = ()
        below = ()
        for i in enumerate(rellist):
            if str(node) in rellist[i[0]]:
                if str(node) == rellist[i[0]][0]:
                    below = np.append(below, rellist[i[0]][1])
                elif str(node) == rellist[i[0]][1]:
                    above = np.append(above, rellist[i[0]][0])
        if len(above) == 0:
            str1 = ""
        else:
            str1 = above[0]
            for i in above[1:]:
                str1 = str1 + ", " + i
        if len(below) == 0:
            str2 = ""
        else:
            str2 = below[0]
            for j in below[1:]:
                str2 = str2 + ", " + j
        return [str1, str2]

    def MCMC_func(self):
        """gathers all the inputs for the mcmc module and then runs it and returns resuslts dictionaries"""
        context_no = [x for x in list(self.context_no_unordered) if x not in self.node_del_tracker]
        TOPO = list(nx.topological_sort(self.chrono_dag))
        self.TOPO_SORT = [x for x in TOPO if (x not in self.node_del_tracker) and (x in context_no)]
        self.TOPO_SORT.reverse()
        context_no = self.TOPO_SORT
        self.key_ref = [list(self.phasefile["Group"])[list(self.phasefile["context"]).index(i)] for i in context_no]
        self.CONT_TYPE = [self.CONT_TYPE[list(self.context_no_unordered).index(i)] for i in self.TOPO_SORT]
        strat_vec = []
        resids = [j for i, j in enumerate(context_no) if self.CONT_TYPE[i] == "residual"]
        intrus = [j for i, j in enumerate(context_no) if self.CONT_TYPE[i] == "intrusive"]
        for i, j in enumerate(context_no):
            if self.CONT_TYPE[i] == "residual":
                low = []
                up = list(self.graph.predecessors(j))
            elif self.CONT_TYPE[i] == "intrusive":
                low = list(self.graph.successors(j))
                up = []
            else:
                up = [k for k in self.graph.predecessors(j) if k not in resids]
                low = [k for k in self.graph.successors(j) if k not in intrus]
            strat_vec.append([up, low])
        # strat_vec = [[list(self.graph.predecessors(i)), list(self.graph.successors(i))] for i in context_no]
        self.RCD_EST = [int(list(self.datefile["date"])[list(self.datefile["context"]).index(i)]) for i in context_no]
        self.RCD_ERR = [int(list(self.datefile["error"])[list(self.datefile["context"]).index(i)]) for i in context_no]
        rcd_est = self.RCD_EST
        rcd_err = self.RCD_ERR
        self.prev_phase, self.post_phase = self.prev_phase, self.post_phase
        input_1 = [
            strat_vec,
            rcd_est,
            rcd_err,
            self.key_ref,
            context_no,
            self.phi_ref,
            self.prev_phase,
            self.post_phase,
            self.TOPO_SORT,
            self.CONT_TYPE,
        ]
        f = open("input_file", "w")
        writer = csv.writer(f)
        #  for i in input_1:
        writer.writerow(input_1)
        f.close()
        CONTEXT_NO, ACCEPT, PHI_ACCEPT, PHI_REF, A, P, ALL_SAMPS_CONT, ALL_SAMPS_PHI = mcmc.run_MCMC(
            CALIBRATION,
            strat_vec,
            rcd_est,
            rcd_err,
            self.key_ref,
            context_no,
            self.phi_ref,
            self.prev_phase,
            self.post_phase,
            self.TOPO_SORT,
            self.CONT_TYPE,
        )
        phase_nodes, resultsdict, all_results_dict = phase_labels(PHI_REF, self.post_phase, PHI_ACCEPT, ALL_SAMPS_PHI)
        for i, j in enumerate(CONTEXT_NO):
            resultsdict[j] = ACCEPT[i]
        for k, l in enumerate(CONTEXT_NO):
            all_results_dict[l] = ALL_SAMPS_CONT[k]

        return (
            CONTEXT_NO,
            ACCEPT,
            PHI_ACCEPT,
            PHI_REF,
            A,
            P,
            ALL_SAMPS_CONT,
            ALL_SAMPS_PHI,
            resultsdict,
            all_results_dict,
        )

    def nodecheck(self, x_current, y_current):
        """returns the node that corresponds to the mouse cooridinates"""
        node_inside = "no node"
        if phase_true == 1:
            (graph,) = pydot.graph_from_dot_file("fi_new.txt")
            node_df_con = node_coords_fromjson(graph)
        else:
            node_df_con = node_coords_fromjson(self.graph)
        node_df = node_df_con[0]

        xmax, ymax = node_df_con[1]
        # forms a dataframe from the dicitonary of coords
        x, y = self.image.size
        cavx = x * self.imscale
        cany = y * self.imscale
        xscale = (x_current) * (xmax) / cavx
        yscale = (cany - y_current) * (ymax) / cany
        for n_ind in range(node_df.shape[0]):
            if (node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and (
                node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper
            ):
                node_inside = node_df.iloc[n_ind].name
                self.graph[node_inside]
        return node_inside

    def edge_render(self):
        """renders string for deleted edges"""
        self.edges_del = self.edge_nodes
        ednodes = str(self.edges_del[0]) + " above " + str(self.edges_del[1])
        self.temp = str(self.temp).replace("[", "")
        self.temp = str(self.temp).replace("]", "")
        self.temp = self.temp + str(ednodes.replace("'", ""))

    def node_del_popup(self):
        self.nodedel = popupWindow5(self.canvas)
        self.canvas["state"] = "disabled"
        self.master.wait_window(self.nodedel.top)
        self.canvas["state"] = "normal"
        return self.nodedel.value

    def edge_del_popup(self):
        self.nodedel = popupWindow6(self.canvas)
        self.canvas["state"] = "disabled"
        self.master.wait_window(self.nodedel.top)
        self.canvas["state"] = "normal"
        return self.nodedel.value

    def nodes(self, currentevent):
        """performs action using the node and redraws the graph"""
        global load_check, phase_true
        self.testmenu.place_forget()
        # deleting a single context
        if self.variable.get() == "Delete context":
            if self.node != "no node":
                if load_check == "loaded":
                    load_check = "not_loaded"
                    answer = askquestion(
                        "Warning!",
                        "Chronological DAG already loaded, do you want to save this as a new model first? \n\n Click Yes to save as new model and No to overwrite existing model",
                    )
                    if answer == "yes":
                        self.refresh_4_new_model(self.controller, proj_dir, load=False)
                    self.littlecanvas2.delete("all")
                #   self.graph.remove_node(self.node)
                self.graph = node_del_fixed(self.graph, self.node)
                self.nodedel_meta = self.node_del_popup()
                self.delnodes = np.append(self.delnodes, self.node)
                self.delnodes_meta.append(self.nodedel_meta)
                self.tree2.insert("", "end", text=self.node, values=[self.nodedel_meta])
        # presents popup list to label new context
        if self.variable.get() == "Add new contexts":
            if load_check == "loaded":
                answer = askquestion(
                    "Warning!",
                    "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
                )
                if answer == "yes":
                    self.refresh_4_new_model(self.controller, proj_dir, load=False)
                self.littlecanvas2.delete("all")
                load_check = "not_loaded"
            self.w = popupWindow(self)
            self.wait_window(self.w.top)
            self.node = self.w.value
            self.graph.add_node(self.node, shape="box", fontsize="30.0", fontname="helvetica", penwidth="1.0")
        # checks if any nodes are in edge node to see if we want to add/delete a context
        if len(self.edge_nodes) == 1:
            # first case deletes strat relationships
            if self.variable.get() == "Delete stratigraphic relationship with " + str(self.edge_nodes[0]):
                self.edge_nodes = np.append(self.edge_nodes, self.node)
                self.reason = self.edge_del_popup()
                if load_check == "loaded":
                    answer = askquestion(
                        "Warning!",
                        "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
                    )
                    if answer == "yes":
                        self.refresh_4_new_model(self.controller, proj_dir, load=False)
                    self.littlecanvas2.delete("all")
                    load_check = "not_loaded"
                try:
                    self.graph.remove_edge(self.edge_nodes[0], self.edge_nodes[1])
                    self.edge_render()
                    self.tree3.insert("", 0, text=self.temp, values=self.reason)
                    self.tree3.update()
                except (KeyError, nx.exception.NetworkXError):
                    try:
                        self.graph.remove_edge(self.edge_nodes[1], self.edge_nodes[0])
                        self.edge_render()
                    except (KeyError, nx.exception.NetworkXError):
                        tk.messagebox.showinfo("Error", "An edge doesnt exist between those nodes")

                self.OptionList.remove("Delete stratigraphic relationship with " + str(self.edge_nodes[0]))
                self.testmenu = ttk.OptionMenu(
                    self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes
                )
                self.edge_nodes = []
            # second case is adding a strat relationship
            elif self.variable.get() == ("Place " + str(self.edge_nodes[0]) + " Above"):
                if load_check == "loaded":
                    answer = askquestion(
                        "Warning!",
                        "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
                    )
                    if answer == "yes":
                        self.refresh_4_new_model(self.controller, proj_dir, load=False)
                self.littlecanvas2.delete("all")
                load_check = "not_loaded"
                self.edge_nodes = np.append(self.edge_nodes, self.node)
                self.addedge(self.edge_nodes)
                self.OptionList.remove("Place " + str(self.edge_nodes[0]) + " Above")
                self.testmenu = ttk.OptionMenu(
                    self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes
                )
                self.edge_nodes = []
        # sets up the menu to delete the strat relationship once user picks next node
        if self.variable.get() == "Delete stratigraphic relationship":
            if len(self.edge_nodes) == 1:
                self.OptionList.remove("Delete stratigraphic relationship with " + str(self.edge_nodes[0]))
                self.edge_nodes = []
            self.edge_nodes = np.append(self.edge_nodes, self.node)
            self.OptionList.append("Delete stratigraphic relationship with " + str(self.edge_nodes[0]))
            self.testmenu = ttk.OptionMenu(
                self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes
            )
        # equates too contexts
        if len(self.comb_nodes) == 1:
            if self.variable.get() == "Equate context with " + str(self.comb_nodes[0]):
                if load_check == "loaded":
                    answer = askquestion(
                        "Warning!",
                        "Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model",
                    )
                self.comb_nodes = np.append(self.comb_nodes, self.node)
                graph_temp = nx.contracted_nodes(self.graph, self.comb_nodes[0], self.comb_nodes[1])
                x_nod = list(graph_temp)
                newnode = str(self.comb_nodes[0]) + " = " + str(self.comb_nodes[1])
                y_nod = [newnode if i == self.comb_nodes[0] else i for i in x_nod]
                mapping = dict(zip(x_nod, y_nod))
                graph_temp = nx.relabel_nodes(graph_temp, mapping)
                try:
                    self.graph_check = nx.transitive_reduction(graph_temp)
                    self.graph = graph_temp
                except Exception as e:
                    if e.__class__.__name__ == "NetworkXError":
                        tk.messagebox.showinfo("Error!", "This creates a cycle so you cannot equate these contexts")
                self.OptionList.remove("Equate context with " + str(self.comb_nodes[0]))
                self.testmenu = ttk.OptionMenu(
                    self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes
                )
                self.comb_nodes = []
        # sets up menu to equate context for when user picks next node
        if self.variable.get() == "Equate context with another":
            if len(self.comb_nodes) == 1:
                self.OptionList.remove("Equate context with " + str(self.comb_nodes[0]))
                self.testmenu = ttk.OptionMenu(
                    self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes
                )
                self.comb_nodes = []
            self.comb_nodes = np.append(self.comb_nodes, self.node)
            self.OptionList.append("Equate context with " + str(self.comb_nodes[0]))
            self.testmenu = ttk.OptionMenu(
                self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes
            )

        if self.variable.get() == "Supplementary menu":
            self.w = popupWindow2(self, self.graph, self.canvas)
        if self.variable.get() == "Get supplementary data for this context":
            self.stratinfo = self.stratfunc(self.node)
            self.metadict2 = {}
            self.metadict = self.graph.nodes()[str(self.node)]
            self.metadict2["Contexts above"] = [self.stratinfo[0]]
            self.metadict2["Contexts below"] = [self.stratinfo[1]]
            self.meta1 = pd.DataFrame.from_dict(self.metadict, orient="index")
            self.meta2 = pd.DataFrame.from_dict(self.metadict2, orient="index")
            self.meta = pd.concat([self.meta1, self.meta2])
            self.meta = self.meta.loc["Determination":"Contexts below"]
            self.meta.columns = ["Data"]
            if self.meta.loc["Determination"][0] != "None":
                self.meta.loc["Determination"][0] = (
                    str(self.meta.loc["Determination"][0][0])
                    + " +- "
                    + str(self.meta.loc["Determination"][0][1])
                    + " Carbon BP"
                )
            self.canvas.itemconfig(
                self.metatext_id, text="Supplementary of node " + str(self.node), font="helvetica 12 bold"
            )
            cols = list(self.meta.columns)
            #     self.tree1 = ttk.Treeview(self.canvas)
            clear_all(self.tree1)
            self.tree1["columns"] = cols
            self.tree1.place(relx=0.758, rely=0.725, relwidth=0.225)
            self.tree1.column("Data", anchor="w")
            self.tree1.heading("Data", text="Data", anchor="w")
            for index, row in self.meta.iterrows():
                self.tree1.insert("", 0, text=index, values=list(row))
            self.tree1.update()
        # sets up menu to add strat relationships for when user picks next node
        if self.variable.get() == "Place above other context":
            if len(self.edge_nodes) == 1:
                self.OptionList.remove("Place " + str(self.edge_nodes[0]) + " Above")
                self.testmenu = ttk.OptionMenu(
                    self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes
                )
                self.edge_nodes = []
            self.edge_nodes = np.append(self.edge_nodes, self.node)
            self.OptionList.append("Place " + str(self.edge_nodes[0]) + " Above")
            self.testmenu = ttk.OptionMenu(
                self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes
            )
        if self.variable.get() == "Get stratigraphic information":
            self.stratfunc(self.node)
        if phase_true == 1:
            imgrender_phase(self.graph)
        else:
            imgrender(self.graph, self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
        self.image = Image.open("testdag.png")
        self.width, self.height = self.image.size
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.show_image()
        self.variable.set("Node Action")
        self.littlecanvas.unbind("<Button-1>")
        self.littlecanvas.bind("<Button-1>", self.move_from)
        self.littlecanvas.bind("<MouseWheel>", self.wheel)

    def move_from(self, event):
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image != "noimage":
            self.littlecanvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        """Drag (move) canvas to the new position"""
        if self.image != "noimage":
            self.littlecanvas.scan_dragto(event.x, event.y, gain=1)
            self.show_image()

        # redraw the image

    def move_from2(self, event):
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image2 != "noimage":
            self.littlecanvas2.scan_mark(event.x, event.y)

    def move_to2(self, event):
        """Drag (move) canvas to the new position"""
        if self.image2 != "noimage":
            self.littlecanvas2.scan_dragto(event.x, event.y, gain=1)
            self.show_image()

    def wheel(self, event):
        """Zoom with mouse wheel"""
        x_zoom = self.littlecanvas.canvasx(event.x)
        y_zoom = self.littlecanvas.canvasy(event.y)
        bbox = self.littlecanvas.bbox(self.container)  # get image area
        if bbox[0] < x_zoom < bbox[2] and bbox[1] < y_zoom < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
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
        #    print(scale)
        self.littlecanvas.scale("all", 0, 0, scale, scale)  # rescale all canvas objects
        self.show_image()

    def wheel2(self, event):
        """Zoom with mouse wheel"""
        x_zoom = self.littlecanvas2.canvasx(event.x)
        y_zoom = self.littlecanvas2.canvasy(event.y)
        bbox = self.littlecanvas2.bbox(self.container2)  # get image area
        if bbox[0] < x_zoom < bbox[2] and bbox[1] < y_zoom < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
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
        self.littlecanvas2.scale("all", 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def show_image(self):
        """Show image on the Canvas"""

        bbox1 = [0, 0, int(self.image.size[0] * self.imscale), int(self.image.size[1] * self.imscale)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (
            self.littlecanvas.canvasx(0),  # get visible area of the canvas
            self.littlecanvas.canvasy(0),
            self.littlecanvas.canvasx(self.littlecanvas.winfo_width()),
            self.littlecanvas.canvasy(self.littlecanvas.winfo_height()),
        )
        if int(bbox2[3]) == 1:
            bbox2 = [0, 0, 0.96 * 0.99 * 0.97 * 1000, 0.99 * 0.37 * 2000 * 0.96]
        bbox = [
            min(bbox1[0], bbox2[0]),
            min(bbox1[1], bbox2[1]),  # get scroll region box
            max(bbox1[2], bbox2[2]),
            max(bbox1[3], bbox2[3]),
        ]
        bbox1 = [0, 0, int(self.image.size[0] * self.imscale), int(self.image.size[1] * self.imscale)]
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
            x_img = min(int(x_2 / self.imscale), self.width)  # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x_1 / self.imscale), int(y_1 / self.imscale), x_img, y_img))
            self.imagetk = ImageTk.PhotoImage(image.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.littlecanvas.delete(self.littlecanvas_img)
            self.imageid = self.littlecanvas.create_image(
                max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]), anchor="nw", image=self.imagetk
            )
            self.transx, self.transy = bbox2[0], bbox2[1]
            self.littlecanvas.imagetk = self.imagetk

    def show_image2(self):
        """Show image on the Canvas"""
        bbox1 = [0, 0, int(self.image2.size[0] * self.imscale2), int(self.image2.size[1] * self.imscale2)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (
            self.littlecanvas2.canvasx(0),  # get visible area of the canvas
            self.littlecanvas2.canvasy(0),
            self.littlecanvas2.canvasx(self.littlecanvas2.winfo_width()),
            self.littlecanvas2.canvasy(self.littlecanvas2.winfo_height()),
        )
        if int(bbox2[3]) == 1:
            bbox2 = [0, 0, 0.96 * 0.99 * 0.97 * 1000, 0.99 * 0.37 * 2000 * 0.96]
        bbox = [
            min(bbox1[0], bbox2[0]),
            min(bbox1[1], bbox2[1]),  # get scroll region box
            max(bbox1[2], bbox2[2]),
            max(bbox1[3], bbox2[3]),
        ]
        bbox1 = [0, 0, int(self.image2.size[0] * self.imscale2), int(self.image2.size[1] * self.imscale2)]
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
            x_img = min(int(x_2 / self.imscale2), self.width2)  # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale2), self.height2)  # ...and sometimes not
            image2 = self.image2.crop((int(x_1 / self.imscale2), int(y_1 / self.imscale2), x_img, y_img))
            self.imagetk2 = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.littlecanvas2.delete(self.littlecanvas2_img)
            self.imageid2 = self.littlecanvas2.create_image(
                max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]), anchor="nw", image=self.imagetk2
            )
            self.transx2, self.transy2 = bbox2[0], bbox2[1]
            self.littlecanvas2.imagetk2 = self.imagetk2

    def phasing(self):
        """runs image render function with phases on seperate levels"""
        global phase_true, node_df
        phase_true = 1
        self.image = imgrender_phase(self.graph)
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw", image=self.littlecanvas.img)
        self.width, self.height = self.image.size
        #  self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.imscale = min(921 / self.image.size[0], 702 / self.image.size[1])
        self.littlecanvas.scale("all", 0, 0, self.delta, self.delta)  # rescale all canvas objects
        self.show_image()
        self.bind("<Configure>", self.resize)
        self.littlecanvas.bind("<Configure>", self.resize)
        self.delnodes = []
        self.delnodes_meta = []
        self.canvas.delete("all")
        self.littlecanvas.bind("<Button-3>", self.preClick)
        self.show_image()

    def resize(self, event):
        """resizes image on canvas"""
        img = Image.open("testdag.png")  # .resize((event.width, event.height), Image.ANTIALIAS)
        self.littlecanvas.img = ImageTk.PhotoImage(img)
        self.w_1 = event.width
        self.h_1 = event.height
        self.littlecanvas.itemconfig(self.littlecanvas_img, image=self.littlecanvas.img)

    def resize2(self, event):
        """resizes image on canvas"""
        img = Image.open("testdag_chrono.png")  # .resize((event.width, event.height), Image.ANTIALIAS)
        self.littlecanvas2.img = ImageTk.PhotoImage(img)
        self.w_1 = event.width
        self.h_1 = event.height
        self.littlecanvas2.itemconfig(self.littlecanvas2_img, image=self.littlecanvas2.img)


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        """initilises page one"""
        tk.Frame.__init__(self, parent)
        self.controller = controller
        startpage = self.controller.get_page("StartPage")
        self.configure(background="#fcfdfd")
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg="#FFE9D6")
        self.canvas.place(relx=0, rely=0.03, relwidth=1, relheight=0.97)
        self.button1 = tk.Button(
            self,
            text="Stratigraphy and supplementary data",
            font="helvetica 12 bold",
            fg="#2F4858",
            command=lambda: controller.show_frame("StartPage"),
            bd=0,
            highlightthickness=0,
            bg="#AEC7D6",
        )
        self.button1.place(relx=0.38, rely=0.0, relwidth=0.17, relheight=0.03)
        self.button1_a = tk.Button(
            self,
            text="Dating Results",
            font="helvetica 12 bold",
            fg="#8F4300",
            command=lambda: controller.show_frame("PageOne"),
            bd=0,
            highlightthickness=0,
            bg="#FFE9D6",
        )
        self.button1_a.place(relx=0.55, rely=0.0, relwidth=0.15, relheight=0.03)
        # define all variables that are used
        self.h_1 = 0
        self.w_1 = 0
        self.transx2 = 0
        self.transy2 = 0
        self.meta1 = ""
        #        self.metatext = ""
        self.mode = ""
        ##### intial values for all the functions
        self.delnodes = []
        self.delnodes_meta = []
        self.edge_nodes = []
        self.comb_nodes = []
        self.edges_del = []
        self.temp = []
        self.results_list = []
        self.cont_canvas_list = ""
        self.x_1 = 1
        self.image = "noimage"
        self.phase_rels = None
        self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1
        self.results_text = None
        self.canvas_plt = None
        self.phase_len_nodes = []
        self.fig = None
        self.file_menubar = ttk.Menubutton(
            self,
            text="File",
        )
        # Adding File Menu and commands
        file = tk.Menu(self.file_menubar, tearoff=0, bg="#fcfdfd")  # , font = ('helvetica',11))
        self.file_menubar["menu"] = file
        file.add_separator()
        file.add_command(
            label="Save project progress", command=lambda: startpage.save_state_1(), font=("helvetica 11 bold")
        )
        self.file_menubar.place(relx=0.0, rely=0, relwidth=0.1, relheight=0.03)
        self.view_menubar = ttk.Menubutton(self, text="View")
        # Adding File Menu and commands
        file1 = tk.Menu(self.view_menubar, tearoff=0, bg="#fcfdfd")  # , font = ('helvetica',11))
        self.view_menubar["menu"] = file1
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)
        self.tool_menubar = ttk.Menubutton(
            self,
            text="Tools",
        )
        # Adding File Menu and commands
        file2 = tk.Menu(self.tool_menubar, tearoff=0, bg="#fcfdfd")  # , font = ('helvetica',11))
        self.tool_menubar["menu"] = file2
        self.tool_menubar.place(relx=0.15, rely=0, relwidth=0.1, relheight=0.03)
        # forming and placing canvas and little canvas
        self.behindcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas.place(relx=0.6, rely=0.038, relwidth=0.39, relheight=0.96)
        #######################
        self.littlecanvas2_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas2_label.place(relx=0.003, rely=0.011, relwidth=0.18, relheight=0.027)
        self.littlecanvas2_label_id = self.littlecanvas2_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas2_label.itemconfig(
            self.littlecanvas2_label_id, text="Chronological graph", font="helvetica 12 bold"
        )
        #######################
        self.littlecanvas = tk.Canvas(
            self.behindcanvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        ##########################################
        self.behindcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas2.place(relx=0.003, rely=0.038, relwidth=0.37, relheight=0.96)
        ##########################################
        self.littlecanvas_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_label.place(relx=0.6, rely=0.011, relwidth=0.18, relheight=0.027)
        self.littlecanvas_label_id = self.littlecanvas_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas_label.itemconfig(
            self.littlecanvas_label_id, text="Posterior densities", font="helvetica 12 bold"
        )
        #########################################
        self.littlecanvas_a_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_a_label.place(relx=0.375, rely=0.518, relwidth=0.08, relheight=0.027)
        self.littlecanvas_a_label_id = self.littlecanvas_a_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas_a_label.itemconfig(
            self.littlecanvas_a_label_id, text="Context list", font="helvetica 12 bold"
        )
        ############################################
        self.behindcanvas_a = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas_a.place(relx=0.375, rely=0.038, relwidth=0.223, relheight=0.45)
        ######################################
        self.littlecanvas_a = tk.Canvas(
            self.behindcanvas_a, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas_a.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        #####################################################
        self.behindcanvas_3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg="#CC5F00")
        self.behindcanvas_3.place(relx=0.375, rely=0.545, relwidth=0.223, relheight=0.45)
        ########################################3
        self.littlecanvas2 = tk.Canvas(
            self.behindcanvas2, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas2.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        #######################################################
        ################################
        self.littlecanvas3 = tk.Canvas(
            self.behindcanvas_3, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas3.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.901)
        self.littlecanvas3_id = self.littlecanvas3.create_text(10, 10, anchor="nw", fill="#0A3200")
        self.littlecanvas3.itemconfig(
            self.littlecanvas3_id,
            text="No contexts chosen for results. \n\nTo add a context to the results list right click on \nthe context you want then select 'add to list'",
            font="helvetica 12 bold",
        )

        ###############################################
        self.littlecanvas3_label = tk.Canvas(
            self.canvas, bd=0, bg="#CC5F00", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.littlecanvas3_label.place(relx=0.375, rely=0.011, relwidth=0.14, relheight=0.027)
        self.littlecanvas3_label_id = self.littlecanvas3_label.create_text(10, 5, anchor="nw", fill="white")
        self.littlecanvas3_label.itemconfig(
            self.littlecanvas3_label_id, text="Calendar date range estimates", font="helvetica 12 bold"
        )

        #################################
        self.littlecanvas2.bind("<MouseWheel>", self.wheel2)
        self.littlecanvas2.bind("<Button-4>", self.wheel2)  # only with Linux, wheel scroll down
        self.littlecanvas2.bind("<Button-5>", self.wheel2)
        self.littlecanvas2.bind("<Button-3>", self.onRight)
        self.littlecanvas2.bind("<Button-1>", self.move_from2)
        self.littlecanvas2.bind("<B1-Motion>", self.move_to2)
        # placing image on littlecanvas from graph
        self.littlecanvas2.rowconfigure(0, weight=1)
        self.littlecanvas2.columnconfigure(0, weight=1)
        self.littlecanvas2.update()
        # placing image on littlecanvas from graph
        self.littlecanvas.rowconfigure(0, weight=1)
        self.littlecanvas.columnconfigure(0, weight=1)

        #########deleted nodes##################
        self.button2 = ttk.Button(self.behindcanvas_3, text="Posterior densities", command=self.mcmc_output)
        self.button2.place(relx=0.008, rely=0.92, relwidth=0.402, relheight=0.07)
        self.button2a = ttk.Button(self.behindcanvas_3, text="HPD intervals", command=self.get_hpd_interval)
        self.button2a.place(relx=0.415, rely=0.92, relwidth=0.322, relheight=0.07)
        self.button3 = ttk.Button(self.behindcanvas_3, text="Clear list", command=self.clear_results_list)
        self.button3.place(relx=0.74, rely=0.92, relwidth=0.252, relheight=0.07)
        self.ResultList = [
            "Add to results list",
            "Get time elapsed",
        ]
        self.variable = tk.StringVar(self.littlecanvas)
        self.variable.set("Add to results list")
        self.testmenu2 = ttk.OptionMenu(
            self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder
        )

    def clear_results_list(self):
        """deletes nodes from results lists"""
        self.results_list = []
        self.littlecanvas3.delete(self.results_text)
        self.canvas_plt.get_tk_widget().pack_forget()
        for item in self.tree_phases.get_children():
            self.tree_phases.delete(item)

    def node_finder(self, currentevent):
        """finds nodes in the chronodag on results page"""
        self.testmenu2.place_forget()
        startpage = self.controller.get_page("StartPage")
        self.chronograph = startpage.chrono_dag
        x = str(self.chrono_nodes(currentevent))

        if self.variable.get() == "Add to results list":
            self.littlecanvas3.delete(self.results_text)
            # ref = np.where(np.array(startpage.CONTEXT_NO) == x)[0][0]
            if x != "no node":
                self.results_list.append(x)

        if len(self.phase_len_nodes) == 1:
            if (
                self.variable.get()
                == "Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context"
            ):
                self.phase_len_nodes = np.append(self.phase_len_nodes, x)
                if self.canvas_plt is not None:
                    self.canvas_plt.get_tk_widget().pack_forget()
                #        font = {'size': 11}
                # using rc function

                self.fig = Figure()
                #     self.fig.rc('font', **font)
                LENGTHS = phase_length_finder(
                    self.phase_len_nodes[0], self.phase_len_nodes[1], startpage.all_results_dict
                )
                plot1 = self.fig.add_subplot(111)
                plot1.hist(LENGTHS, bins="auto", color="#0504aa", rwidth=1, density=True)
                #  plot1.xlabel('Time elapsed in calibrated years (cal BP)')
                #  plot1.ylabel('Probability density')
                plot1.spines["right"].set_visible(False)
                plot1.spines["top"].set_visible(False)
                # plot1.set_ylim([0, 0.05])
                # plot1.set_xlim([0, 400])
                plot1.title.set_text(
                    "Time elapsed between " + str(self.phase_len_nodes[0]) + " and " + str(self.phase_len_nodes[1])
                )
                interval = list(mcmc.HPD_interval(np.array(LENGTHS[1000:])))
                columns = ("context_1", "context_2", "hpd_interval")
                #       self.fig.set_tight_layout(True)
                self.canvas_plt = FigureCanvasTkAgg(self.fig, master=self.littlecanvas)
                self.canvas_plt.get_tk_widget().place(relx=0, rely=0, relwidth=1)
                self.canvas_plt.draw_idle()
                # show hpd intervlls -----------
                self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show="headings")
                # define headings
                self.tree_phases.heading("context_1", text="Context 1")
                self.tree_phases.heading("context_2", text="Context 2")
                self.tree_phases.heading("hpd_interval", text="HPD interval")
                intervals = []
                hpd_str = ""
                refs = [k for k in range(len(interval)) if k % 2]
                for i in refs:
                    hpd_str = hpd_str + str(np.abs(interval[i - 1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
                # add data to the treeview
                intervals.append((self.phase_len_nodes[0], self.phase_len_nodes[1], hpd_str))
                for contact in intervals:
                    self.tree_phases.insert("", tk.END, values=contact)
                self.tree_phases.place(relx=0, rely=0, relwidth=1)
                # add a scrollbar
                scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
                self.tree_phases.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky="nsew")
            self.ResultList.remove("Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context")
            self.testmenu2 = ttk.OptionMenu(
                self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder
            )
            self.phase_len_nodes = []

        if self.variable.get() == "Get time elapsed":
            if len(self.phase_len_nodes) == 1:
                self.ResultList.remove(
                    "Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context"
                )
                self.testmenu2 = ttk.OptionMenu(
                    self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder
                )
                self.phase_len_nodes = []
            self.phase_len_nodes = np.append(self.phase_len_nodes, x)
            self.ResultList.append("Get time elapsed between " + str(self.phase_len_nodes[0]) + " and another context")
            self.testmenu2 = ttk.OptionMenu(
                self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder
            )
        self.littlecanvas3.delete(self.results_text)
        self.littlecanvas3.delete(self.littlecanvas3_id)
        self.cont_canvas_list = ""
        for i in set(self.results_list):
            self.cont_canvas_list = self.cont_canvas_list + str(i) + "\n"
        self.results_text = self.littlecanvas3.create_text(
            5, 10, anchor="nw", text=self.cont_canvas_list, fill="#0A3200", font=("Helvetica 12 bold")
        )
        self.variable.set("Add to results list")

    def onRight(self, *args):
        """makes test menu appear after right click"""
        self.littlecanvas2.unbind("Button-1>")
        self.littlecanvas2.bind("<Button-1>", self.onLeft)
        # Here we fetch our X and Y coordinates of the cursor RELATIVE to the window
        self.cursorx2 = int(self.littlecanvas2.winfo_pointerx() - self.littlecanvas2.winfo_rootx())
        self.cursory2 = int(self.littlecanvas2.winfo_pointery() - self.littlecanvas2.winfo_rooty())

        # Now we define our right click menu canvas
        # And here is where we use our X and Y variables, to place the menu where our cursor is,
        # That's how right click menus should be placed.
        self.testmenu2.place(x=self.cursorx2, y=self.cursory2, relwidth=0.2)
        # This is for packing our options onto the canvas, to prevent the canvas from resizing.
        # This is extremely useful if you split your program into multiple canvases or frames
        # and the pack method is forcing them to resize.
        self.testmenu2.pack_propagate(0)
        # Here is our label on the right click menu for deleting a row, notice the cursor
        # value, which will give us a pointy finger when you hover over the option.
        self.testmenu2.config(width=10)
        # This function is for removing the canvas when an option is clicked.

    def preClick(self, *args):
        """makes test menu appear and removes any previous test menu"""
        try:
            self.testmenu2.place_forget()
            self.onRight()
        except Exception:
            self.onRight()

    # Hide menu when left clicking
    def onLeft(self, *args):
        """hides menu when left clicking"""
        try:
            self.testmenu2.place_forget()
        except Exception:
            pass

    def mcmc_output(self):
        """loads posterior density plots into the graph"""
        global mcmc_check
        startpage = self.controller.get_page("StartPage")
        if mcmc_check == "mcmc_loaded":
            if self.canvas_plt is not None:
                self.canvas_plt.get_tk_widget().pack_forget()
                self.toolbar.destroy()
            fig = Figure(figsize=(8, min(30, len(self.results_list) * 3)), dpi=100)
            for i, j in enumerate(self.results_list):
                if len(self.results_list) < 10:
                    n = len(self.results_list)
                else:
                    n = 10
                plt.rcParams["text.usetex"]

                plot_index = int(str(n) + str(1) + str(i + 1))
                plot1 = fig.add_subplot(plot_index)
                plot1.hist(startpage.resultsdict[j], bins="auto", color="#0504aa", alpha=0.7, rwidth=1, density=True)
                plot1.spines["right"].set_visible(False)
                plot1.spines["top"].set_visible(False)
                fig.gca().invert_xaxis()
                plot1.set_ylim([0, 0.02])
                nodes = list(nx.topological_sort(startpage.chrono_dag))
                uplim = nodes[0]
                lowlim = nodes[-1]
                min_plot = min(startpage.resultsdict[uplim])
                max_plot = max(startpage.resultsdict[lowlim])
                plot1.set_xlim(min_plot, max_plot)
                node = str(j)
                if ("a" in node) or ("b" in node):
                    if "a" in node:
                        node = node.replace("a_", r"\alpha_{")
                    if "b" in node:
                        node = node.replace("b_", r"\beta_{")
                    if "=" in node:
                        node = node.replace("=", "} = ")
                    plot1.title.set_text(r"Group boundary " + r"$" + node + "}$")
                else:
                    plot1.title.set_text(r"Context " + r"$" + node + "}$")

            fig.set_tight_layout(True)
            self.canvas_plt = FigureCanvasTkAgg(fig, master=self.littlecanvas)
            self.canvas_plt.draw()
            # creating the Matplotlib toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas_plt, self.littlecanvas)  #
            self.toolbar.update()  #
            self.canvas_plt.get_tk_widget().pack()

    def get_hpd_interval(self):
        """loads hpd intervals into the results page"""
        global mcmc_check
        if len(self.results_list) != 0:
            startpage = self.controller.get_page("StartPage")
            USER_INP = simpledialog.askstring(
                title="HPD interval percentage",
                prompt="Please input HPD interval percentage. Note, 95% is used as standard \n \n Percentage:",
            )

            self.lim = np.float64(USER_INP) / 100
            if mcmc_check == "mcmc_loaded":
                hpd_str = ""
                columns = ("context", "hpd_interval")
                self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show="headings")
                self.tree_phases.heading("context", text="Context")
                self.tree_phases.heading("hpd_interval", text=str(USER_INP) + "% HPD interval")
                intervals = []
                for i, j in enumerate(list(set(self.results_list))):
                    node = str(j)
                    interval = list(mcmc.HPD_interval(np.array(startpage.resultsdict[j][1000:]), lim=self.lim))
                    # define headings
                    hpd_str = ""
                    refs = [k for k in range(len(interval)) if k % 2]
                    for i in refs:
                        hpd_str = hpd_str + str(np.abs(interval[i - 1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
                    # add data to the treeview
                    intervals.append((node, hpd_str))
                for contact in intervals:
                    self.tree_phases.insert("", tk.END, values=contact)
                self.tree_phases.place(relx=0, rely=0, relwidth=0.99)
                # add a scrollbar
                scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
                self.tree_phases.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky="nsew")
                self.littlecanvas_a.create_text(150, 80, text=hpd_str, fill="#0A3200")

    def chronograph_render_post(self):
        global load_check
        if load_check == "loaded":
            self.image2 = imgrender2(self.littlecanvas2.winfo_width(), self.littlecanvas2.winfo_height())
            #    scale_factor = min(self.littlecanvas2.winfo_width()/self.image_ws.size[0], self.littlecanvas2.winfo_height()/self.image_ws.size[1])
            #    self.image2 = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)

            self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
            self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw", image=self.littlecanvas2.img)

            self.width2, self.height2 = self.image2.size
            #   self.imscale2 = 1.0  # scale for the canvaas image
            self.delta2 = 1.1  # zoom magnitude
            # Put image into container rectangle and use it to set proper coordinates to the image
            self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
            self.imscale2 = min(921 / self.image2.size[0], 702 / self.image2.size[1])
            self.littlecanvas2.scale("all", 0, 0, self.delta2, self.delta2)  # rescale all canvas objects
            self.show_image2()

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
        else:
            return  # zoom only inside image area
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
        self.littlecanvas2.scale("all", 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def show_image2(self):
        """Show image on the Canvas"""
        bbox1 = [0, 0, int(self.image2.size[0] * self.imscale2), int(self.image2.size[1] * self.imscale2)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (
            self.littlecanvas2.canvasx(0),  # get visible area of the canvas
            self.littlecanvas2.canvasy(0),
            self.littlecanvas2.canvasx(self.littlecanvas2.winfo_width()),
            self.littlecanvas2.canvasy(self.littlecanvas2.winfo_height()),
        )
        if int(bbox2[3]) == 1:
            bbox2 = [0, 0, 0.96 * 0.99 * 0.97 * 1000, 0.99 * 0.37 * 2000 * 0.96]
        bbox = [
            min(bbox1[0], bbox2[0]),
            min(bbox1[1], bbox2[1]),  # get scroll region box
            max(bbox1[2], bbox2[2]),
            max(bbox1[3], bbox2[3]),
        ]
        bbox1 = [0, 0, int(self.image2.size[0] * self.imscale2), int(self.image2.size[1] * self.imscale2)]
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
            x_img = min(int(x_2 / self.imscale2), self.width2)  # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale2), self.height2)  # ...and sometimes not
            image2 = self.image2.crop((int(x_1 / self.imscale2), int(y_1 / self.imscale2), x_img, y_img))
            self.imagetk2 = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.littlecanvas2.delete(self.littlecanvas2_img)
            self.imageid2 = self.littlecanvas2.create_image(
                max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]), anchor="nw", image=self.imagetk2
            )
            self.transx2, self.transy2 = bbox2[0], bbox2[1]
            self.littlecanvas.imagetk2 = self.imagetk2

    def nodecheck(self, x_current, y_current):
        """returns the node that corresponds to the mouse cooridinates"""
        global node_df
        node_inside = "no node"
        node_df_con = node_coords_fromjson(self.chronograph)
        node_df = node_df_con[0]
        xmax, ymax = node_df_con[1]
        # forms a dataframe from the dicitonary of coords
        x, y = self.image2.size
        cavx = x * self.imscale2
        cany = y * self.imscale2
        xscale = (x_current) * (xmax) / cavx
        yscale = (cany - y_current) * (ymax) / cany
        outline = nx.get_node_attributes(self.chronograph, "color")
        for n_ind in range(node_df.shape[0]):
            if (node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and (
                node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper
            ):
                node_inside = node_df.iloc[n_ind].name
                outline[node_inside] = "red"
                nx.set_node_attributes(self.chronograph, outline, "color")
        return node_inside

    def chrono_nodes(self, current):
        """scales the nodes on chronodag"""
        x_scal = self.cursorx2 + self.transx2
        y_scal = self.cursory2 + self.transy2
        node = self.nodecheck(x_scal, y_scal)
        return node


class PageTwo(object):
    def __init__(self, master, controller):
        """initilaising page two"""
        self.top = tk.Toplevel(controller)
        self.top.geometry("2000x1000")
        self.intru_list = []
        self.resid_list = []
        self.controller = controller
        self.h_1 = 0
        self.w_1 = 0
        self.transx2 = 0
        self.transy2 = 0
        self.modevariable = None
        self.meta1 = ""
        #        self.metatext = ""
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
        # self.imscale2 = 1.0  # scale for the canvaas image
        self.delta2 = 1.1
        self.results_text = None
        self.canvas_plt = None
        self.phase_len_nodes = []
        self.canvas = tk.Canvas(self.top, bd=0, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        startpage = self.controller.get_page("StartPage")
        self.graphcanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.graphcanvas.place(relx=0.02, rely=0.05, relwidth=0.35, relheight=0.9)
        label = tk.Message(
            self.top,
            text="Using this page: \n\n Please click on the buttons below to set into residual or intrusive mode. Then double right click on any context to set as residual/intrusive. \n\n Note that orange boxes denote intrusive contexts and blue boxes denote residual contexts. \n\n If you have clicked on a context by mistake, double right click to remove any label attributed to the context.",
        )
        label.place(relx=0.4, rely=0.05)
        label2 = ttk.Label(self.canvas, text="Residual Contexts")
        label2.place(relx=0.4, rely=0.4)
        self.graphcanvas.update()
        self.residcanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.residcanvas.place(relx=0.4, rely=0.42, relwidth=0.35, relheight=0.08)
        self.intrucanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.intrucanvas.place(relx=0.4, rely=0.54, relwidth=0.35, relheight=0.08)

        self.resid_label = ttk.Label(self.residcanvas, text=self.resid_list)
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        scroll_bar1 = ttk.Scrollbar(self.residcanvas)
        scroll_bar1.pack(side=tk.RIGHT)
        self.intru_label = ttk.Label(self.intrucanvas, text=self.intru_list)
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        scroll_bar2 = ttk.Scrollbar(self.intrucanvas)
        scroll_bar2.pack(side=tk.RIGHT)
        label3 = ttk.Label(self.canvas, text="Intrusive Contexts")
        label3.place(relx=0.4, rely=0.52)
        if startpage.graph is not None:
            self.graphcopy = self.load_graph()
            self.imscale2 = min(921 / self.image.size[0], 702 / self.image.size[1])
            self.graphcanvas.scale("all", 0, 0, self.delta2, self.delta2)  # rescale all canvas objects
            self.show_image2()
        self.graphcanvas.update()
        button = ttk.Button(self.top, text="Proceed", command=lambda: self.popup4_wrapper(controller))

        button1 = tk.Button(self.top, text="Residual mode", command=lambda: self.mode_set("resid"))
        button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
        button3 = tk.Button(self.top, text="Intrusive mode", command=lambda: self.mode_set("intru"))
        button.place(relx=0.48, rely=0.65, relwidth=0.09, relheight=0.03)
        button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)
        self.graphcanvas.bind("<MouseWheel>", self.wheel2)
        self.graphcanvas.bind("<Button-4>", self.wheel2)  # only with Linux, wheel scroll down
        self.graphcanvas.bind("<Button-5>", self.wheel2)
        self.graphcanvas.bind("<Double-Button-3>", self.resid_node_click)
        self.graphcanvas.bind("<Button-1>", self.move_from2)
        self.graphcanvas.bind("<B1-Motion>", self.move_to2)
        master.wait_window(self.top)
        # placing image on littlecanvas from graph

    def popup4_wrapper(self, controller):
        """wraps popup4 so we can get the variables from self.popup4"""
        self.popup4 = popupWindow4(
            self, controller, self.resid_list, self.intru_list, self.node_del_tracker, self.graphcopy
        )
        self.top.destroy()

    def mode_set(self, var_set):
        """sets the mode to residual or intrusive and highlights the colour of the  button"""
        self.modevariable = var_set
        if var_set == "resid":
            button1 = tk.Button(
                self.top, text="Residual mode", command=lambda: self.mode_set("resid"), background="orange"
            )
            button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
            button3 = tk.Button(self.top, text="Intrusive mode", command=lambda: self.mode_set("intru"))
            button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)
        if var_set == "intru":
            button1 = tk.Button(self.top, text="Residual mode", command=lambda: self.mode_set("resid"))
            button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
            button3 = tk.Button(
                self.top, text="Intrusive mode", command=lambda: self.mode_set("intru"), background="lightgreen"
            )
            button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)

    def tkraise(self, aboveThis=None):
        """runs loads graph"""
        self.load_graph()
        super().tkraise(aboveThis)

    def load_graph(self):
        """loads graph on results page"""
        # loads start page so we get get variables from that class
        startpage = self.controller.get_page("StartPage")
        self.graphcopy = copy.deepcopy(startpage.graph)
        datadict = nx.get_node_attributes(self.graphcopy, "Determination")
        nodes = self.graphcopy.nodes()
        self.node_del_tracker = []
        for i in nodes:
            if datadict[i] == [None, None]:
                self.node_del_tracker.append(i)
        color = nx.get_node_attributes(self.graphcopy, "color")
        fill = nx.get_node_attributes(self.graphcopy, "fontcolor")
        for j in self.node_del_tracker:
            color[j] = "gray"
            fill[j] = "gray"
        nx.set_node_attributes(self.graphcopy, color, "color")
        nx.set_node_attributes(self.graphcopy, fill, "fontcolor")
        if phase_true == 1:
            self.image = imgrender_phase(self.graphcopy)
        else:
            self.image = imgrender(self.graphcopy, self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height())
        #    scale_factor = min(self.graphcanvas.winfo_width()/self.image_ws.size[0], self.graphcanvas.winfo_height()/self.image_ws.size[1])
        #     self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
        self.icon = ImageTk.PhotoImage(self.image)
        self.graphcanvas_img = self.graphcanvas.create_image(0, 0, anchor="nw", image=self.icon)
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
        else:
            return  # zoom only inside image area
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
        #    print(scale2)
        self.graphcanvas.scale("all", 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def autozoom(self, event):
        """Zoom with mouse wheel"""
        x_zoom = self.graphcanvas.canvasx(event.x)
        y_zoom = self.graphcanvas.canvasy(event.y)
        bbox = self.graphcanvas.bbox(self.container)  # get image area
        if bbox[0] < x_zoom < bbox[2] and bbox[1] < y_zoom < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
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
        self.graphcanvas.scale("all", 0, 0, scale2, scale2)  # rescale all canvas objects
        self.show_image2()

    def show_image2(self):
        """Show image on the Canvas"""
        startpage = self.controller.get_page("StartPage")
        startpage.update_idletasks()
        bbox1 = [0, 0, int(self.image.size[0] * self.imscale2), int(self.image.size[1] * self.imscale2)]
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (
            self.graphcanvas.canvasx(0),  # get visible area of the canvas
            self.graphcanvas.canvasy(0),
            self.graphcanvas.canvasx(self.graphcanvas.winfo_width()),
            self.graphcanvas.canvasy(self.graphcanvas.winfo_height()),
        )
        bbox = [
            min(bbox1[0], bbox2[0]),
            min(bbox1[1], bbox2[1]),  # get scroll region box
            max(bbox1[2], bbox2[2]),
            max(bbox1[3], bbox2[3]),
        ]
        bbox1 = [0, 0, int(self.image.size[0] * self.imscale2), int(self.image.size[1] * self.imscale2)]
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
            x_img = min(int(x_2 / self.imscale2), self.width2)  # sometimes it is larger on 1 pixel
            y_img = min(int(y_2 / self.imscale2), self.height2)  # ...and sometimes not
            image2 = self.image.crop((int(x_1 / self.imscale2), int(y_1 / self.imscale2), x_img, y_img))
            self.graphcanvas.delete(self.icon)
            self.icon = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
            self.imageid2 = self.graphcanvas.create_image(
                max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]), anchor="nw", image=self.icon
            )
            self.transx2, self.transy2 = bbox2[0], bbox2[1]

    def nodecheck(self, x_current, y_current):
        """returns the node that corresponds to the mouse cooridinates"""
        global node_df
        startpage = self.controller.get_page("StartPage")
        # updates canvas to get the right coordinates
        startpage.update_idletasks()

        node_inside = "no node"
        if self.graphcopy is not None:
            # gets node coordinates from the graph
            node_df_con = node_coords_fromjson(self.graphcopy)
            # forms a dataframe from the dicitonary of coords
            node_df = node_df_con[0]
            xmax, ymax = node_df_con[1]
            # scales the coordinates using the canvas and image size
            x, y = self.image.size
            cavx = x * self.imscale2
            cany = y * self.imscale2
            xscale = (x_current) * (xmax) / cavx
            yscale = (cany - y_current) * (ymax) / cany
            # gets current node colours
            outline = nx.get_node_attributes(self.graphcopy, "color")
            for n_ind in range(node_df.shape[0]):
                if (node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and (
                    node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper
                ):
                    node_inside = node_df.iloc[n_ind].name
                    nx.set_node_attributes(self.graphcopy, outline, "color")
        return node_inside

    def resid_node_click(self, event):
        """Gets node that you're clicking on and sets it as the right colour depending on if it's residual or intrusive"""
        startpage = self.controller.get_page("StartPage")
        startpage.update_idletasks()
        self.cursorx2 = int(self.graphcanvas.winfo_pointerx() - self.graphcanvas.winfo_rootx())
        self.cursory2 = int(self.graphcanvas.winfo_pointery() - self.graphcanvas.winfo_rooty())
        x_scal = self.cursorx2 + self.transx2
        y_scal = self.cursory2 + self.transy2
        node = self.nodecheck(x_scal, y_scal)
        outline = nx.get_node_attributes(self.graphcopy, "color")
        # changes colour of the node outline to represent: intrustive (green), residual (orange) or none (black)
        if (node in self.resid_list) and (self.modevariable != "intru"):
            self.resid_list.remove(node)
            outline[node] = "black"
        elif (node in self.resid_list) and (self.modevariable == "intru"):
            self.resid_list.remove(node)
            outline[node] = "green"
            self.intru_list.append(node)
        elif (node in self.intru_list) and (self.modevariable != "resid"):
            self.intru_list.remove(node)
            outline[node] = "black"
        elif (node in self.intru_list) and (self.modevariable == "resid"):
            self.intru_list.remove(node)
            self.resid_list.append(node)
            outline[node] = "orange"
        elif (self.modevariable == "resid") and (node not in self.resid_list):
            self.resid_list.append(node)
            outline[node] = "orange"
        elif self.modevariable == "intru" and (node not in self.intru_list):
            self.intru_list.append(node)
            outline[node] = "green"
        self.resid_label = ttk.Label(self.residcanvas, text=str(self.resid_list).replace("'", "")[1:-1])
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.intru_label = ttk.Label(self.intrucanvas, text=str(self.intru_list).replace("'", "")[1:-1])
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        # adds scrollbars to the canvas
        scroll_bar1 = ttk.Scrollbar(self.residcanvas)
        scroll_bar1.pack(side=tk.RIGHT)
        scroll_bar2 = ttk.Scrollbar(self.intrucanvas)
        scroll_bar2.pack(side=tk.RIGHT)
        # updates the node outline colour
        nx.set_node_attributes(self.graphcopy, outline, "color")
        if phase_true == 1:
            imgrender_phase(self.graphcopy)
        else:
            imgrender(self.graphcopy, self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height())
        # rerends the image of the strat DAG with right colours
        self.image = Image.open("fi_new.png")
        self.width2, self.height2 = self.image.size
        self.container = self.graphcanvas.create_rectangle(0, 0, self.width2, self.height2, width=0)
        self.show_image2()
        return node


# Global scoping of MAIN_FRAME is currently required for state saving behaviour, prior to refactoring.
MAIN_FRAME = MainFrame()
style = ThemedStyle(MAIN_FRAME)
style.set_theme("arc")
# f = tkFont.Font(family='helvetica', size=10, weight='bold')
# s = ttk.Style()
# s.configure('.', font=f)
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=12, weight="bold")
style = ttk.Style(MAIN_FRAME)
style.configure("TEntry", font=("Helvetica", 12, "bold"))
style.configure("TButton", font=("Helvetica", 12, "bold"))
style.configure("TLabel", font=("Helvetica", 12, "bold"))
style.configure("TOptionMenu", font=("Helvetica", 12, "bold"))
style.configure("TTreeView", font=("Helvetica", 12, "bold"))
MAIN_FRAME.option_add("*Font", default_font)
MAIN_FRAME.geometry("2000x1000")
MAIN_FRAME.title(f"PolyChron {version('PolyChron')}")


def parse_cli(argv=None):
    """Parse and return command line arguments

    Args:
        argv (list[str] or None): optional list of command line parameters to parse. If None, sys.argv is used by `argparse.ArgumentParser.parse_args`

    Returns:
        (argparse.Namespace): Namespace object with arguments set as attributes, as returned by `argparse.ArgumentParser.parse_args()`
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true", help="show version information and exit")
    args = parser.parse_args(argv)
    return args


def print_version():
    """Print the version of PolyChron to stdout

    Note:
        For editable installs the printed value may be incorrect
    """
    print(f"PolyChron {version('PolyChron')}")


def main():
    """Main method as the entry point for launching the GUI"""
    args = parse_cli()
    if args.version:
        print_version()
    else:
        MAIN_FRAME.mainloop()


# If this script is executed directly, run the main method
if __name__ == "__main__":
    main()
