"""Collection of utility functions / classes."""

import ast
import re

import networkx as nx
import numpy as np
import pandas as pd
import pydot
from graphviz import render
from networkx.drawing.nx_pydot import read_dot, write_dot
from PIL import Image, ImageChops

from . import globals


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
    globals.node_df = node_coords_fromjson(file)
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
    #     fig = sg.fromfile('fi_new.svg') # requires import svgutils.transform as sg
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
    #     globals.node_df = node_coords_fromjson(file)
    return outp


def imgrender2(canv_width, canv_height):
    """renders png from dotfile"""
    if globals.load_check == "loaded":
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
    if globals.FILE_INPUT is not None:
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
    if globals.FILE_INPUT is not None:
        phase = nx.get_node_attributes(file_graph, "fillcolor")
        phase_norm = [phase[ph][phase[ph].rfind("/") + 1 : len(phase[ph])] for ph in phase]
        # ####code to get colours####
        f_str = open(str(globals.FILE_INPUT), "r")
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
    globals.node_df = node_coords_fromjson(graph)
    return outp
