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
#from ttkbootstrap import Style
#from networkx.readwrite import json_graph

old_stdout = sys.stdout

class StdoutRedirector(object):

    def __init__(self, text_area):
        self.text_area = text_area

    def write(self, str):
        self.text_area.update_idletasks()
        self.text_area.insert(tk.END, str)
        self.text_area.see(tk.END)

phase_true = 0
load_check = 'not_loaded'
CALIBRATION = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True)    
def trim(im_trim):
    # t0 = time.time()
    """Trims images down"""
    bg_trim = Image.new(im_trim.mode, im_trim.size)
    diff = ImageChops.difference(im_trim, bg_trim)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()    
 #   print("trim", str(time.time() - t0))
    return im_trim.crop(bbox)

def polygonfunc(i):
    x = re.findall(r'points="(.*?)"', i)[0].replace(' ', ',')
    a = x.split(",")
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
 #   print((sys._getframe().f_code.co_name), str(time.time() - t0))
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
#    print((sys._getframe().f_code.co_name), str(time.time() - t0))  
    return node_info

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
        node_info[k[0]].update({"Date":"None", "Find_Type":"None", "Phase":node_info[k[0]]['fillcolor']})
    individ_attrs = zip(node_list, node_info)
    attrs = dict(individ_attrs)#add the dictionary of attributed to a node
    nx.set_node_attributes(file, attrs)
 #   print((sys._getframe().f_code.co_name), str(time.time() - t0))
    return file

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
        for i, j in enumerate(elist):
            file_graph.add_edge("b_" + str(j), evenlist[i], arrows=False)    
        for i, j in enumerate(olist):
            file_graph.add_edge(oddlist[i], "a_" + str(j.replace("_below", "")), arrows=False)
        #add boundary nodes
        #add dges between nodes using y_l as reference
        #figure out top and bottom nodes
        #figure out floating nodes
   # elif len(phaselist > 1)
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
    return graph_data, [xs, ys]



def chrono_edge_add(file_graph, graph_data, xs_ys, phasedict, phase_trck):
    xs = xs_ys[0]
    ys = xs_ys[1]
    phase_norm, node_list = graph_data[1][0], graph_data[1][1]
    all_node_phase = dict(zip(node_list, phase_norm))
   # print(node_list, phase_norm)     
    for i in node_list:
        if (i in xs) == False:
            if (i in ys) == False:
                file_graph.add_edge("b_" + str(all_node_phase[i]), i, arrows=False)
                file_graph.add_edge(i, "a_" + str(all_node_phase[i]), arrows=False)
            else:
                file_graph.add_edge(i, "a_" + str(all_node_phase[i]), arrows=False)
        elif (i in xs) == True:
            if (i in ys) == False:
                #print(i)
                file_graph.add_edge("b_" + str(all_node_phase[i]), i, arrows=False)
    if phasedict != None:
        for p in list(set(phase_trck)):
            relation = phasedict[p]
            if relation == 'gap':
                file_graph.add_edge("a_" + str(p[0]), "b_" + str(p[1]))
            if relation == 'overlap':
                file_graph.add_edge("b_" + str(p[1]), "a_" + str(p[0]))
            if relation == "abuting":
                x_bef = list(file_graph)
                file_graph = nx.contracted_nodes(file_graph, "a_" + str(p[0]), "b_" + str(p[1]))
                x_nod = list(file_graph)
                newnode = str("a_" + str(p[0]) + " = " +"b_" + str(p[1]))
                y_nod = [newnode if i=="a_" + str(p[0]) else i for i in x_nod]
                mapping = dict(zip(x_nod, y_nod))
                file_graph = nx.relabel_nodes(file_graph, mapping)
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
    return(file_graph, phi_ref)



def imgrender(file):
    """renders png from dotfile"""
    write_dot(file, 'fi_new')
    render('dot', 'png', 'fi_new')
    inp = Image.open("fi_new.png")
    inp = trim(inp)
    inp.save("testdag.png")
    outp = Image.open("testdag.png")
#    print((sys._getframe().f_code.co_name), str(time.time() - t0))
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
#    print((sys._getframe().f_code.co_name), str(time.time() - t0))
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
#    print((sys._getframe().f_code.co_name), str(time.time() - t0))
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
#    print((sys._getframe().f_code.co_name), str(time.time() - t0))
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
  #  print((sys._getframe().f_code.co_name), str(time.time() - t0))    
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
 #   print((sys._getframe().f_code.co_name), str(time.time() - t0))
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
    inp.save("testdag.png")
    outp = Image.open("testdag.png")
  #  print((sys._getframe().f_code.co_name), str(time.time() - t0))
    return outp



class popupWindow(object):
    def __init__(self,master):
        top=self.top=tk.Toplevel(master)
        self.l=tk.Label(top,text="Context Number")
        self.l.pack()
        self.e=tk.Entry(top)
        self.e.pack()
        self.b=tk.Button(top,text='Ok',command=self.cleanup)
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
  #      self.b=tk.Button(top,text='Ok',command=self.cleanup)
        self.button3.place(relx = 0.1, rely = 0.7)
        
    def testdate_input(self, *args):
        if self.variable_b.get() == "Input date":          
            self.label4 = tk.Label(self.canvas2, text='Radiocarbon Date', bg = 'white')
            self.entry4 = tk.Entry(self.canvas2)
            self.canvas2.create_window(90, 130, window=self.entry4, width=50)
            self.canvas2.create_window(90, 90, window=self.label4)
            self.label5 = ttk.Label(self.canvas2, text='Error', bg = 'white')
            self.entry5 = tk.Entry(self.canvas2)
            self.canvas2.create_window(200, 130, window=self.entry5, width=50)
            self.canvas2.create_window(200, 90, window=self.label5)
        if self.variable_b.get() == "Input phase":          
            self.label6 = ttk.Label(self.canvas2, text='Phase', bg = 'white')
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
  #      print((sys._getframe().f_code.co_name), str(time.time() - t0))
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
#        print((sys._getframe().f_code.co_name), str(time.time() - t0))

                
    def cleanup(self):
        self.value=self.canvas2.get()
        self.top.destroy()
        
        
class popupWindow3(object):
    def __init__(self, master, graph, canvas, phase_rels):
        self.littlecanvas2 = canvas
        self.top=tk.Toplevel(master)
        self.top.geometry("1000x400")
        self.variable_1 = tk.StringVar(self.top)
        self.variable_2 = tk.StringVar(self.top)
        self.phases = phase_rels        
        self.menu_list1 = []
        self.menudict = {}
        self.prev_dict = {}
        self.post_dict = {}
        self.menu_list2 = ["abuting", "gap", "overlap"]            

        
        self.button_b = ttk.Button(self.top, text='Render Chronological graph', command=lambda:self.full_chronograph_func())         
        self.graph = graph
        self.graphcopy = copy.deepcopy(self.graph)
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
        if len(self.step_1[0][1][3]) != 0:
            self.graphcopy, self.phi_ref = chrono_edge_add(self.graphcopy, self.step_1[0], self.step_1[1], self.menudict, self.phases)
            self.post_phase.append(self.post_dict[self.phi_ref[0]])
            for i in range(1,len(self.phi_ref)-1):
                    self.prev_phase.append(self.prev_dict[self.phi_ref[i]])
                    self.post_phase.append(self.post_dict[self.phi_ref[i]])
            self.prev_phase.append(self.prev_dict[self.phi_ref[len(self.phi_ref)-1]])
        else:
            self.phi_ref = list(self.step_1[0][1][2])
        self.post_phase.append("end")
        write_dot(self.graphcopy, 'fi_new_chrono')
        self.top.destroy()

class MainFrame(tk.Tk):
    """ Main frame for tkinter app"""
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

     #   self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
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
            
class StartPage(tk.Frame):
    """ Main frame for tkinter app"""
    def __init__(self, parent, controller):
        global load_check
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
        
    #    self.button2 = ttk.Button(self.canvas, text="Go to Page Two", command=lambda: controller.show_frame("PageTwo"))
     #   self.button2.place(relx=0.78, rely=0.03, relwidth=0.1, relheight=0.03) 

        #########deleted nodes##################
        self.nodescanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = 'red')
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
#        container = ttk.Frame(self.canvas)
#        container.pack(side="top", fill="both", expand=True)
#        container.grid_rowconfigure(0, weight=1)
#        container.grid_columnconfigure(0, weight=1)


        def destroy(self):
            self.testmenu.place_forget()
    #    # This is the function that removes the selected item when the label is clicked.
        def delete(self, *args):
       # print(self.variable.get())
            self.destroy()  
            self.testmenu.place_forget()
            self.variable.set("Node Action")
        self.metacanvas = tk.Canvas(self.canvas, bg="white")
        self.metacanvas.place(relx=0.75, rely=0.52, relwidth=0.35, relheight=0.2)
        self.abovebelowcanvas = tk.Canvas(self.canvas, bg="white")
        self.abovebelowcanvas.place(relx=0.75, rely=0.75, relwidth=0.35, relheight=0.2)        


    def onRight(self, *args):
        '''makes test menu appear after right click '''
        self.littlecanvas.unbind("Button-1>")
        self.littlecanvas.bind("<Button-1>", self.onLeft)
        # Here we fetch our X and Y coordinates of the cursor RELATIVE to the window
        self.cursorx = int(self.littlecanvas.winfo_pointerx() - self.littlecanvas.winfo_rootx())
        self.cursory = int(self.littlecanvas.winfo_pointery() - self.littlecanvas.winfo_rooty())
    
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
        self.testbutton = ttk.Button(self.canvas, text ='Render Chronological DAG', command = lambda:self.chronograph_render()) #popupWindow3(self, self.graph, self.littlecanvas2))
        self.testbutton.place(relx=0.75, rely=0.01, relwidth=0.15, relheight=0.03) 
        self.littlecanvas.bind("<Button-3>", self.preClick)
    #    print((sys._getframe().f_code.co_name), str(time.time() - t0))
           
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
                G.add_node(i, shape="box", fontname="Helvetica", fontsize="30.0", penwidth="1.0")
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
                self.testbutton = ttk.Button(self.canvas, text ='Render Chronological DAG', command = lambda:self.chronograph_render()) #popupWindow3(self, self.graph, self.littlecanvas2))
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
            self.context_no = list(self.graph.nodes())

            
    def open_file4(self): 
    #    t0 = time.time()
        file = askopenfile(mode ='r', filetypes =[('Python Files', '*.csv')]) 
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
        self.top=tk.Toplevel(self.littlecanvas)
        self.top.geometry("1000x400")
 #       self.pbar_ind = ttk.Progressbar(self.top, orient="horizontal", length=400, mode="indeterminate", maximum=100)
  #      self.pbar_ind.pack()
     #   self.pbar_ind.grid(row=0, column=0, pady=2, padx=2, columnspan=3)
        self.l=ttk.Label(self.top,text="MCMC in progress")
        self.l.pack()
    #    self.create_window(40, 35, window=self.l)
        
        outputPanel = tk.Text(self.top, wrap='word', height = 11, width=50)
        outputPanel.pack()
        sys.stdout = StdoutRedirector(outputPanel)
 #       text = TextOut(self.top)
  #      sys.stdout = text
   #     text.update_idletasks()
    #    text.pack(expand=True, fill=tk.BOTH)
  #      self.pbar_ind.start()
       # MainFrame.update(self)
        self.MCMC_func()
    #    MainFrame.update(self)
  #      self.pbar_ind.stop()
        self.cleanup()
        self.controller.show_frame('PageOne')

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


##        #pt2
    def chronograph_render(self):
        global load_check
        self.popup3 = popupWindow3(self, self.graph, self.littlecanvas2, self.phase_rels)
        try: 
            load_check = 'loaded'
        except (RuntimeError, TypeError, NameError):
            load_check = 'not_loaded'
        self.image2 = imgrender2(load_check)
        print(self.image2)
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
        print(str(load_check) + ' chronorender')    
        
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
    #    CALIBRATION = pd.read_csv('spline_interpolation_new.txt', delim_whitespace=True) 
        context_no = list(self.graph.nodes())
        self.key_ref = [list(self.phasefile["phase"])[list(self.phasefile["context"]).index(i)] for i in context_no]
        strat_vec = [[list(self.graph.predecessors(i)), list(self.graph.successors(i))] for i in context_no]
        self.RCD_EST = [int(list(self.datefile["date"])[list(self.datefile["context"]).index(i)]) for i in context_no]
        self.RCD_ERR = [int(list(self.datefile["error"])[list(self.datefile["context"]).index(i)]) for i in context_no]        
        rcd_est = self.RCD_EST
        rcd_err = self.RCD_ERR
#        print("mcmc")
##        print(calibrate, "calibrate")
#        print(strat_vec, "strat_vec")
#        print(rcd_est, "rcd_est")
#        print(rcd_err, "rcd_est")
#        print(self.key_ref, "key_ref")
#        print(context_no, "context_no")
#        print(self.popup3.phi_ref, "phi_ref")
#        print(self.popup3.prev_phase, "prev_phase")
#        print(self.popup3.post_phase, "post_phase")
        TOPO_SORT = list(nx.topological_sort(self.graph))
        TOPO_SORT.reverse()
#        print(TOPO_SORT)
        mcmc.run_MCMC(CALIBRATION, strat_vec, rcd_est, rcd_err, self.key_ref, context_no, self.popup3.phi_ref, self.popup3.prev_phase, self.popup3.post_phase, TOPO_SORT)


        
        

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
        for n_ind in range(node_df.shape[0]):
            if ((node_df.iloc[n_ind].x_lower < xscale < node_df.iloc[n_ind].x_upper) and
                    (node_df.iloc[n_ind].y_lower < yscale < node_df.iloc[n_ind].y_upper)):
                node_inside = node_df.iloc[n_ind].name       
        return node_inside

#    def scroll_y(self, *args, **kwargs):
#        t0 = time.time()
#        """ Scroll canvas vertically and redraw the image"""
#        self.canvas.yview(*args, **kwargs)  # scroll vertically        
#        self.show_image()
#       # print((sys._getframe().f_code.co_name), str(time.time() - t0))
#        # redraw the image
#
#
#    def scroll_x(self, *args, **kwargs):
# #       t0 = time.time()
#        """Scroll canvas horizontally and redraw the image"""
#        self.canvas.xview(*args, **kwargs)  # scroll horizontally
#        self.show_image()  # redraw the image
##        print((sys._getframe().f_code.co_name), str(time.time() - t0))

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
#        print((sys._getframe().f_code.co_name), str(time.time() - t0))
#

    def nodes(self, currentevent):
        """performs action using the node and redraws the graph"""
        t0 = time.time()
        self.testmenu.place_forget()
        if self.image != "noimage":
            x_scal = self.cursorx + self.transx
            y_scal = self.cursory + self.transy
            node = self.nodecheck(x_scal, y_scal)
            if self.variable.get() == "Delete Node":
                if node != "no node":
                    self.graph.remove_node(node)
                    self.delnodes = np.append(self.delnodes, node)
            
            if self.variable.get() == "Add Nodes":
                self.w=popupWindow(self)
                self.wait_window(self.w.top)
                node = self.w.value 
                self.graph.add_node(node, shape="box", fontsize="30.0",
                                   fontname="Ubuntu", penwidth="1.0")                   
                           
            if self.variable.get() == "Metadata Menu":
                self.w=popupWindow2(self, self.graph, self.metacanvas)    
            if len(self.edge_nodes) == 1:       
                if self.variable.get() == "Delete Edge with "+ str(self.edge_nodes[0]):
                    self.edge_nodes = np.append(self.edge_nodes, node)
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
                    self.edge_nodes = np.append(self.edge_nodes, node) 
                    self.addedge(self.edge_nodes)
                    self.OptionList.remove("Place "+ str(self.edge_nodes[0]) + " Above")
                    self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command=self.nodes)
                    self.edge_nodes = []      
                    
            if self.variable.get() == "Delete Edge":
                if len(self.edge_nodes) == 1:
                    self.OptionList.remove("Delete Edge with "+ str(self.edge_nodes[0]))
                    self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command = self.nodes)
                    self.edge_nodes = []                    
                self.edge_nodes = np.append(self.edge_nodes, node)                
                self.OptionList.append("Delete Edge with "+ str(self.edge_nodes[0]))
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command = self.nodes)

            if len(self.comb_nodes) == 1:       
                if self.variable.get() == "Combine Node with "+ str(self.comb_nodes[0]):
                    self.comb_nodes = np.append(self.comb_nodes, node)
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
                self.comb_nodes = np.append(self.comb_nodes, node)                
                self.OptionList.append("Combine Node with "+ str(self.comb_nodes[0]))
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, *self.OptionList, command = self.nodes)       
                            
            if self.variable.get() == "Get Metadata":
                self.metatext = tk.Text(self.metacanvas, width=120, height=40)
                self.metacanvas.create_window((0, 0), window=self.metatext, anchor='nw')
                self.meta1 = pd.DataFrame.from_dict(self.graph.nodes()[str(node)], orient='index')
                self.meta2 = self.meta1.loc["Date":"Phase",]
                self.meta2.columns = ["Data"]
                #if self.meta2.loc["Date"] != "None":
                if self.meta2.loc["Date"][0] != "None":
                   self.meta2.loc["Date"][0] = str(self.meta2.loc["Date"][0][0]) + " +- " + str(self.meta2.loc["Date"][0][1]) + " Carbon BP"
               # self.nice_meta2 = tabulate(self.meta2, headers='keys', tablefmt='psql')
                self.metatext.insert('end', 'Metadata of node ' +
                                     str(node) + ':\n')
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
                self.edge_nodes = np.append(self.edge_nodes, node)                
                self.OptionList.append("Place "+ str(self.edge_nodes[0]) + " Above")
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command = self.nodes)
            if self.variable.get() == "Get stratigraphic information":
                self.stratfunc(node)
                
            if phase_true == 1:
                imgrender_phase(self.graph)
            else:
                imgrender(self.graph) 
            self.image = Image.open('testdag.png')
            self.width, self.height = self.image.size
            self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
            self.show_image()
            self.text = tk.Text(self.nodescanvas, width=120, height=40)
            self.nodescanvas.create_window((0, 0), window=self.text, anchor='nw', bg = 'white')
            nbnodes = str(self.delnodes)
            self.text.insert('end', 'Deleted Contexts:\n' + str(nbnodes.replace("'", ""))[1:-1])
            self.text.configure(state='normal')
            self.variable.set("Node Action")
            self.littlecanvas.unbind('<Button-1>')
            self.littlecanvas.bind('<Button-1>', self.move_from)
            self.littlecanvas.bind("<MouseWheel>", self.wheel)
        #    print(time.time() - t0)
   #     print((sys._getframe().f_code.co_name), str(time.time() - t0)) 

    def pos_update(self):
#        t0 = time.time()
        global node_df
        node_df = node_coords_fromjson(self.graph) 
    #    print((sys._getframe().f_code.co_name), str(time.time() - t0))


    def move_from(self, event):
#        t0 = time.time()
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image != "noimage":
            self.littlecanvas.scan_mark(event.x, event.y)
  #      print((sys._getframe().f_code.co_name), str(time.time() - t0))

    def move_to(self, event):
 #       t0 = time.time()
        """Drag (move) canvas to the new position"""
        if self.image != "noimage":
            self.littlecanvas.scan_dragto(event.x, event.y, gain=1)
            self.show_image()
      #      bbox = self.littlecanvas.bbox(self.container)
            
        # redraw the image
    def move_from2(self, event):
#        t0 = time.time()
        """Remembers previous coordinates for scrolling with the mouse"""
        if self.image != "noimage":
            self.littlecanvas2.scan_mark(event.x, event.y)
  #      print((sys._getframe().f_code.co_name), str(time.time() - t0))

    def move_to2(self, event):
 #       t0 = time.time()
        """Drag (move) canvas to the new position"""
        if self.image != "noimage":
            self.littlecanvas2.scan_dragto(event.x, event.y, gain=1)
            self.show_image()
     #       bbox2 = self.littlecanvas2.bbox(self.container)
            
            
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
#        print((sys._getframe().f_code.co_name), str(time.time() - t0))
        
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
    #    node_df = pd.DataFrame.from_dict(pos_dag, orient='index')
 #       print((sys._getframe().f_code.co_name), str(time.time() - t0))
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
   #     print((sys._getframe().f_code.co_name), str(time.time() - t0))



class PageOne(tk.Frame ):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
            
        label = tk.Label(self, text="This is page 1")
        label.pack(side="top", fill="x", pady=10)
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
#        self.littlecanvas.bind("<MouseWheel>", self.wheel)
#        self.littlecanvas.bind('<Button-4>', self.wheel)# only with Linux, wheel scroll down
#        self.littlecanvas.bind('<Button-5>', self.wheel)
#        self.littlecanvas.bind('<Button-1>', self.move_from)
#        self.littlecanvas.bind('<B1-Motion>', self.move_to)
        
        self.littlecanvas2.bind("<MouseWheel>", StartPage.wheel2)
        self.littlecanvas2.bind('<Button-4>', StartPage.wheel2)# only with Linux, wheel scroll down
        self.littlecanvas2.bind('<Button-5>', StartPage.wheel2)
        self.littlecanvas2.bind('<Button-1>', StartPage.move_from2)
        self.littlecanvas2.bind('<B1-Motion>', StartPage.move_to2)
        #placing image on littlecanvas from graph
        self.littlecanvas.rowconfigure(0, weight=1)
        self.littlecanvas.columnconfigure(0, weight=1)
        self.littlecanvas.update()

        self.button1 = ttk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        self.button1.place(relx=0.78, rely=0.01, relwidth=0.1, relheight=0.03) 
        self.chronograph_render_post()
        
                
    def chronograph_render_post(self):
        global load_check
        print(load_check)
        if load_check == 'loaded':
            self.image2 = imgrender2(load_check)
            print('hiiiiiiiiiii')
            self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
            self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw",
                                                                  image=self.littlecanvas2.img)
    
            self.width2, self.height2 = self.image2.size
            self.imscale2 = 1.0  # scale for the canvaas image
            self.delta2 = 1.1  # zoom magnitude
                # Put image into container rectangle and use it to set proper coordinates to the image
            self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
            self.littlecanvas2.bind("<Configure>", StartPage.resize2)  
    def tkraise(self, aboveThis=None):
            # Get a reference to StartPage
       # start_page = self.controller.frames['StartPage']
                # Get the selected item from start_page
        self.chronograph_render_post()   
            # Call the real .tkraise
        super().tkraise(aboveThis)   

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 2")
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

MAIN_FRAME = MainFrame() 
sys.stdout = old_stdout
style = ThemedStyle(MAIN_FRAME)
style.set_theme("breeze") 
MAIN_FRAME.geometry("2000x1000")
MAIN_FRAME.mainloop()