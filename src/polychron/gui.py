import os
import pathlib
import tkinter as tk
from tkinter import ttk
import copy
import matplotlib as plt
from PIL import Image, ImageTk
from networkx.drawing.nx_pydot import write_dot
import networkx as nx
import numpy as np
import pandas as pd
from tkinter.filedialog import askopenfile
import polychron.automated_mcmc_ordering_coupling_copy as mcmc
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import pickle
from tkinter import simpledialog
import csv
import packaging.version
# Get the absolute path to a directory in the users home dir
POLYCHRON_PROJECTS_DIR = (pathlib.Path.home() / "Documents/Pythonapp_tests/projects").resolve()
# Ensure the directory exists (this is a little aggressive)
POLYCHRON_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# @todo @future - not implementing yet, see https://github.com/bryonymoody/PolyChron/issues/69
class popupWindow2(object):
    def __init__(self, master, graph, canvas):

        #this popup window lets us change the metadata after popupwindow has gone
        self.graph = graph
        self.canvas2 = tk.Canvas(self.top)
        self.canvas2.place(relx=0, rely=0, relwidth=1, relheight=1)
#        #making node add section
#defining variables to keep track of what is being updated in the meta data
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
        self.label3 = ttk.Label(self.canvas2, text='Node')
        self.canvas2.create_window(40, 60, window=self.entry3, width=50)
        self.canvas2.create_window(40, 35, window=self.label3)
        #needs way more detail adding to this
        self.dict = {'Find Type': ['Find1', 'Find2', 'Find3'],
                     'Determination': ['None', 'Input date'],
                     'Group': ['None', 'Input Group']}
#       #defining variables to keep track of what is being updated in the meta data
        self.variable_a = tk.StringVar(self.top)
        self.variable_b = tk.StringVar(self.top)
        self.variable_c = tk.StringVar(self.top)
        self.variable_d = tk.StringVar(self.top)
        self.optionmenu_a = ttk.OptionMenu(self.top, self.variable_a, list(self.dict.keys())[0], *self.dict.keys())
        self.optionmenu_b = ttk.OptionMenu(self.top, self.variable_b, 'None', 'None')
        self.optionmenu_a.place(relx=0.3, rely=0.15)
        self.optionmenu_b.place(relx=0.6, rely=0.15)
        self.variable_a.trace('w', self.update_options)
        self.variable_b.trace('w', self.testdate_input)
        self.variable_c.trace('w', self.update_options)
        self.variable_d.trace('w', self.update_options)
        self.variable_a.set('Determination')
     #   self.button3.place(relx=0.1, rely=0.7)

    def testdate_input(self):
        '''formats the windows so that they have the right inputs depending of if it's a date or a phase'''
        if self.variable_b.get() == "Input date":
            self.label4 = ttk.Label(self.canvas2, text='Radiocarbon Date')
            self.entry4 = ttk.Entry(self.canvas2)
            self.canvas2.create_window(90, 130, window=self.entry4, width=50)
            self.canvas2.create_window(90, 90, window=self.label4)
            self.label5 = ttk.Label(self.canvas2, text='Error')
            self.entry5 = ttk.Entry(self.canvas2)
            self.canvas2.create_window(200, 130, window=self.entry5, width=50)
            self.canvas2.create_window(200, 90, window=self.label5)
        if self.variable_b.get() == "Input group":
            self.label6 = ttk.Label(self.canvas2, text='Group')
            self.entry6 = ttk.Entry(self.canvas2)
            self.canvas2.create_window(90, 130, window=self.entry6, width=50)
            self.canvas2.create_window(90, 90, window=self.label6)

    def update_options(self, *args):
        """updates metadata drop down menu 1"""
        meta_data = self.dict[self.variable_a.get()]
        self.variable_b.set(meta_data[0])
        menu = self.optionmenu_b['menu']
        menu.delete(0, 'end')
        for meta in meta_data:
            menu.add_command(label=meta,
                             command=lambda nation=meta: self.variable_b.set(nation))
    def cleanup(self):
        '''cleans up popup2'''
        self.top.destroy()

class popupWindow3(object):
    def __init__(self, master, graph, canvas, phase_rels, dropdown_ns=[], dropdown_intru=[], resid_list=[], intru_list=[]):
        '''initialises popup3'''
        #set up the canvas for checking if contexts are residual or intrusive
        self.littlecanvas2 = canvas
        self.top = tk.Toplevel(master)
        self.top.geometry("1500x400")
        self.maincanvas = tk.Canvas(self.top, bg ='#AEC7D6', highlightthickness=0,  borderwidth=0, highlightbackground = 'white')
        self.maincanvas.place(relx = 0, rely = 0, relwidth = 1, relheight =1)
        self.maincanvas.update()
        self.backcanvas = tk.Canvas(self.maincanvas, bg = 'white', highlightthickness=0,  borderwidth=0, highlightbackground = 'white')
        self.backcanvas.place(relx = 0.135, rely = 0.9, relheight = 0.13, relwidth = 0.53)
        self.backcanvas.create_line(150, 30, 600, 30, arrow=tk.LAST,  width=3)
        self.time_label = tk.Label(self.maincanvas, text = "Time")
        self.time_label.config( bg ='white', font=('helvetica', 12, 'bold'),fg = '#2f4858', wraplength=130)
        self.time_label.place(relx = 0.32, rely = 0.91, relwidth = 0.12, relheight = 0.05)
        self.top.title("Adding group relationships")
        self.graph = graph
        #makes a copy of the graph so I can edit it to chrnograph
        self.graphcopy = copy.deepcopy(self.graph)
        phasedict = nx.get_node_attributes(self.graphcopy, 'Group') #get all the phases for each node
        datadict = nx.get_node_attributes(self.graphcopy, 'Determination') # get all dates for each notes
        nodes = self.graphcopy.nodes() #all contexts
        self.node_del_tracker = [] #empty node tracker 
        #checks for each context and if there isn't node or phase info, it deletes it
        for i in nodes:
            if phasedict[i] is None:
                self.node_del_tracker.append(i)
            elif datadict[i] == [None, None]:
                self.node_del_tracker.append(i)
        for j in self.node_del_tracker:
            self.graphcopy = node_del_fixed(self.graphcopy, j)
        #sets up all the vairables we need for this class
        self.context_no_unordered = [x for x in list(self.graph.nodes()) if x not in self.node_del_tracker] # sets up a context list
        self.CONT_TYPE = ['normal' for i in self.context_no_unordered] #set up context types
        self.phases = phase_rels
        self.resid_list3 = resid_list
        self.intru_list3 = intru_list
        self.dropdown_ns = dropdown_ns
        self.dropdown_intru = dropdown_intru
        #checks if contexts are residual or intrusive and if we want to keep them or exclude from modelling
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
        self.COLORS = ['LavenderBlush2', 'powder blue', 'LavenderBlush3', 'LemonChiffon4', 'dark khaki', 'LightGoldenrod1', 'aquamarine2', 'hot pink', 'DarkOrchid4', 'pale turquoise', 'LightSteelBlue2', 'DeepPink4', 'firebrick4', 'khaki4', 'turquoise3', 'alice blue', 'DarkOrange4', 'LavenderBlush4', 'misty rose', 'pink1', 'OrangeRed2', 'chocolate2', 'OliveDrab2', 'LightSteelBlue3', 'firebrick2', 'dark orange', 'ivory2', 'yellow2', 'DeepPink3', 'aquamarine', 'LightPink2', 'DeepSkyBlue2', 'LightCyan4', 'RoyalBlue3', 'SeaGreen3', 'SlateGray1', 'IndianRed3', 'DarkGoldenrod3', 'HotPink1', 'navy', 'tan2', 'orange4', 'tomato', 'LightSteelBlue1', 'coral1', 'MediumOrchid4', 'light grey', 'DarkOrchid3', 'RosyBrown2', 'LightSkyBlue1', 'medium sea green', 'deep pink', 'OrangeRed3', 'sienna2', 'thistle2', 'linen', 'tan4', 'bisque2', 'MediumPurple4', 'DarkSlateGray4', 'mint cream', 'sienna3', 'lemon chiffon', 'ivory3', 'chocolate1', 'peach puff', 'DeepSkyBlue3', 'khaki2', 'SlateGray2', 'dark turquoise', 'deep sky blue', 'light sky blue', 'lime green', 'yellow', 'burlywood3', 'tomato4', 'orange3', 'wheat2', 'olive drab', 'brown3', 'burlywood1', 'LightPink1', 'light cyan', 'saddle brown', 'SteelBlue3', 'SpringGreen3', 'goldenrod4', 'dark salmon', 'DodgerBlue3', 'MediumPurple3', 'azure2', 'lavender blush', 'SteelBlue4', 'honeydew3', 'LightBlue1', 'DeepSkyBlue4', 'medium aquamarine', 'turquoise1', 'thistle', 'DarkGoldenrod2', 'wheat3', 'LemonChiffon2', 'turquoise', 'light sea green', 'maroon3', 'green4', 'SlateBlue1', 'DarkOliveGreen3', 'dark violet', 'LightYellow3', 'DarkGoldenrod1', 'PeachPuff3', 'DarkOrange1', 'goldenrod2', 'goldenrod1', 'SkyBlue4', 'ivory4', 'DarkSeaGreen3', 'aquamarine4', 'VioletRed3', 'orange red', 'CadetBlue3', 'DarkSlateGray2', 'seashell2', 'DarkOliveGreen4', 'SkyBlue2', 'DarkOrchid2', 'maroon1', 'orchid1', 'red3', 'LightSkyBlue4', 'HotPink4', 'LightBlue2', 'coral3', 'magenta4', 'bisque4', 'SteelBlue1', 'cornsilk3', 'dark sea green', 'RosyBrown3', 'salmon3', 'NavajoWhite2', 'PaleTurquoise4', 'SteelBlue2', 'OliveDrab1', 'ghost white', 'HotPink3', 'salmon', 'maroon', 'khaki3', 'AntiqueWhite1', 'PaleVioletRed2', 'maroon2', 'cyan3', 'MistyRose4', 'thistle3', 'gold3', 'tomato3', 'tan1', 'LightGoldenrod3', 'blue violet', 'tomato2', 'RoyalBlue4', 'pink3', 'cadet blue', 'slate gray', 'medium slate blue', 'PaleGreen3', 'DodgerBlue2', 'LightSkyBlue3', 'lawn green', 'PaleGreen1', 'forest green', 'thistle1', 'snow', 'LightSteelBlue4', 'medium violet red', 'pink2', 'PaleVioletRed4', 'VioletRed1', 'gainsboro', 'navajo white', 'DarkOliveGreen1', 'IndianRed2', 'RoyalBlue2', 'dark olive green', 'AntiqueWhite3', 'DarkSlateGray1', 'LightSalmon3', 'salmon4', 'plum3', 'orchid3', 'azure', 'bisque3', 'turquoise4', 'SeaGreen1', 'sienna4', 'pink', 'MediumOrchid1', 'thistle4', 'PaleVioletRed3', 'blanched almond', 'DarkOrange2', 'royal blue', 'blue2', 'chartreuse4', 'LightGoldenrod4', 'NavajoWhite4', 'dark orchid', 'plum1', 'SkyBlue1', 'OrangeRed4', 'khaki', 'PaleGreen2', 'yellow4', 'maroon4', 'turquoise2', 'firebrick3', 'bisque', 'LightCyan2', 'burlywood4', 'PaleTurquoise3', 'azure4', 'gold', 'yellow3', 'chartreuse3', 'RosyBrown1', 'white smoke', 'PaleVioletRed1', 'papaya whip', 'medium spring green', 'AntiqueWhite4', 'SlateGray4', 'LightYellow4', 'coral2', 'MediumOrchid3', 'CadetBlue2', 'LightBlue3', 'snow2', 'purple1', 'magenta3', 'OliveDrab4', 'DarkOrange3', 'seashell3', 'magenta2', 'green2', 'snow4', 'DarkSeaGreen4', 'slate blue', 'PaleTurquoise1', 'red2', 'LightSkyBlue2', 'snow3', 'green yellow', 'DeepPink2', 'orange2', 'cyan', 'light goldenrod', 'light pink', 'honeydew4', 'RoyalBlue1', 'sea green', 'pale violet red', 'AntiqueWhite2', 'blue', 'LightSalmon2', 'SlateBlue4', 'orchid4', 'dark slate gray', 'dark slate blue', 'purple', 'chartreuse2', 'khaki1', 'LightBlue4', 'light yellow', 'indian red', 'VioletRed2', 'gold4', 'light goldenrod yellow', 'rosy brown', 'IndianRed4', 'azure3', 'orange', 'VioletRed4', 'salmon2', 'SeaGreen2', 'pale goldenrod', 'pale green', 'plum2', 'dark green', 'coral4', 'LightGoldenrod2', 'goldenrod3', 'NavajoWhite3', 'MistyRose2', 'wheat1', 'medium turquoise', 'floral white', 'red4', 'firebrick1', 'burlywood2', 'DarkGoldenrod4', 'goldenrod', 'sienna1', 'MediumPurple1', 'purple2', 'LightPink4', 'dim gray', 'LemonChiffon3', 'light steel blue', 'seashell4', 'brown1', 'wheat4', 'MediumOrchid2', 'DarkOrchid1', 'RosyBrown4', 'blue4', 'cyan2', 'salmon1', 'MistyRose3', 'chocolate3', 'light salmon', 'coral', 'honeydew2', 'light blue', 'sandy brown', 'LightCyan3', 'brown2', 'midnight blue', 'CadetBlue1', 'LightYellow2', 'cornsilk4', 'cornsilk2', 'SpringGreen4', 'PeachPuff4', 'PaleGreen4', 'SlateBlue2', 'orchid2', 'purple3', 'light slate blue', 'purple4', 'lavender', 'cornflower blue', 'CadetBlue4', 'DodgerBlue4', 'SlateBlue3', 'DarkSlateGray3', 'medium orchid', 'gold2', 'pink4', 'DarkOliveGreen2', 'spring green', 'dodger blue', 'IndianRed1', 'violet red', 'MediumPurple2', 'old lace', 'LightSalmon4', 'brown4', 'SpringGreen2', 'yellow green', 'plum4', 'SlateGray3', 'steel blue', 'HotPink2', 'medium purple', 'LightPink3', 'PeachPuff2', 'sky blue', 'dark goldenrod', 'PaleTurquoise2']
        self.canvas = tk.Canvas(self.top, bg = 'white')
        self.canvas.place(relx = 0.135, rely = 0.05, relheight = 0.85, relwidth = 0.53)
        self.canvas.update()
        self.instruc_label = tk.Label(self.maincanvas, text = "Instructions: \n Place the oldest group in the bottom left corner then for each subseqent group, place it directly above and move it to be overlapping, abutting or to have a gap.")
        self.instruc_label.config(bg='white', font=('helvetica', 12, 'bold'),fg = '#2f4858', wraplength=130)
        self.instruc_label.place(relx = 0.01, rely = 0.05, relwidth = 0.12, relheight = 0.85)
        self.instruc_label2 = tk.Label(self.maincanvas, text = "User defined group relationships")
        self.instruc_label2.config(bg='white', font=('helvetica', 12, 'bold'), fg = '#2f4858')
        self.instruc_label2.place(relx = 0.67, rely = 0.17, relwidth = 0.32, relheight = 0.1)

        self.label_dict = {}
        phases = []
        for i in phase_rels:
            phases.append(i[0])
            phases.append(i[1])
        self.phase_labels = list(set(phases))
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        m = len(self.phase_labels)
        for ind, i in enumerate(self.phase_labels):    
            msg = tk.Label(self.canvas, text = str(i))
            msg.config(bg=self.COLORS[ind], font=('helvetica', 14, 'bold'))
            msg.bind('<B1-Motion>',self.on_move)
            msg.place(x= 0.05*w + (w/(2*m))*ind, y= 0.85*h - ((0.95*h)/m)*ind, relwidth = 0.76/m, relheight = min(0.1, 0.9/m))
            self.label_dict[i] = msg
        self.button1 = tk.Button(self.maincanvas, text = "Confirm groups", command = lambda: self.get_coords(),  bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6') 
        self.button1.place(relx = 0.8, rely = 0.91)   
        self.df = pd.DataFrame(phase_rels, columns = ['Younger group', 'Older group'])
        self.frmtreeborder = tk.LabelFrame(self.maincanvas, bg = 'white')
        self.frmtreeborder.columnconfigure(0, weight=1)
        self.frmtreeborder.rowconfigure(0, weight=1)
        cols = list(self.df.columns)
        self.tree = ttk.Treeview(self.frmtreeborder)
        self.frmtreeborder.place(relx = 0.67, rely = 0.25, relheight = 0.65, relwidth = 0.32)
        self.tree.grid(column=0,row=0,sticky='nsew',padx=6,pady=6)      
        self.tree["columns"] = cols
        for i in cols:
            self.tree.column(i, anchor="w")
            self.tree.heading(i, text=i, anchor='w')
        
        for index, row in self.df.iterrows():
            self.tree.insert("",0,text=index,values=list(row))
        self.tree['show'] = 'headings'
        master.wait_window(self.top)

    def get_coords(self):
        self.instruc_label.destroy()
        self.button1.destroy()
        self.tree.destroy()
        self.frmtreeborder.destroy()
        self.maincanvas.columnconfigure(0, weight=1)
        self.maincanvas.rowconfigure(0, weight=1)
        self.maincanvas.update()
        self.instruc_label = tk.Label(self.maincanvas, text = "If you're happy with your group relationships, click the Render Chronological Graph button.")
        self.instruc_label.config(bg='white', font=('helvetica', 12, 'bold'), wraplength=130)
        self.instruc_label.place(relx = 0.01, rely = 0.05, relwidth = 0.12, relheight = 0.85)
        
        y_list = []
        for i in self.label_dict.keys():
            yx = self.label_dict[i].winfo_y()
            my = self.label_dict[i].winfo_height()
            y_cent = yx + 0.5*my
            y_list.append((i, y_cent))
        y_final = sorted(y_list, key=lambda x: x[1])
        y_final.reverse()
        ref_y = y_final[0][1]
        ref_h = self.label_dict[y_final[0][0]].winfo_height()
        ref_w = self.label_dict[y_final[0][0]].winfo_width()
        ref_gap = 0.25*ref_w
        orig_x = [self.label_dict[j[0]].winfo_x() for j in y_final[1:]]
        orig_x_prev = [self.label_dict[j[0]].winfo_x() + ref_w for j in y_final[:-1]] 
        self.prev_dict = {}
        self.post_dict = {}
        self.menudict = {}
        for ind, j in enumerate(y_final[1:]):
            x = orig_x[ind]
            x_prev = orig_x_prev[ind]
            if ind < len(y_final)-1:
                x_prev_curr = self.label_dict[y_final[ind][0]].winfo_x() + ref_w
                if x - x_prev < -15:
                    x = x_prev_curr - ref_gap
                    self.prev_dict[str(j[0])] = 'overlap'
                    self.post_dict[str(y_final[ind][0])] = 'overlap'
                    self.menudict[(str(j[0]),str(y_final[ind][0]))] = 'overlap'
                    
                elif x - x_prev > 15:
                    x = x_prev_curr + ref_gap
                    self.prev_dict[str(j[0])] = 'gap'
                    self.post_dict[str(y_final[ind][0])] = 'gap'
                    self.menudict[(str(j[0]),str(y_final[ind][0]))] = 'gap'
                else:
                    x = x_prev_curr
                    self.prev_dict[str(j[0])] = 'abutting'
                    self.post_dict[str(y_final[ind][0])] = 'abutting'
                    self.menudict[(str(j[0]),str(y_final[ind][0]))] = 'abutting'
                y = ref_y - (0.5 + ind + 1)*ref_h #ceter of top box + (half and scalefactor) times height   
                self.label_dict[j[0]].place(x = x, y = y)
                self.canvas.update()
        col1, col2, col3 = [], [], []
        rels_df = pd.DataFrame()
        for i in self.menudict.keys():
            col1.append(i[0])
            col2.append(i[1])
            col3.append(self.menudict[i])
        rels_df['Younger group'] = col1
        rels_df['Older group'] = col2
        rels_df['Relationship'] = col3   
        cols = list(rels_df.columns)
        self.frmtreeborder = tk.LabelFrame(self.maincanvas, bg = 'white')
        self.frmtreeborder.columnconfigure(0, weight=1)
        self.frmtreeborder.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(self.frmtreeborder)
        self.frmtreeborder.place(relx = 0.67, rely = 0.25, relheight = 0.65, relwidth = 0.32)
        self.tree.grid(column=0,row=0,sticky='nsew',padx=6,pady=6)    
        self.tree["columns"] = cols
        for i in cols:
            self.tree.column(i, anchor="w", width = 100)
            self.tree.heading(i, text=i, anchor='w')
        
        for index, row in rels_df.iterrows():
            self.tree.insert("",0,text=index,values=list(row))
        self.tree['show'] = 'headings'         
        self.button_b = tk.Button(self.maincanvas, text='Render Chronological graph', command=lambda: self.full_chronograph_func(), bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6')
        self.button_b.place(relx=0.75, rely=0.91)
        self.button_a = tk.Button(self.maincanvas, text='Change relationships', command=lambda: self.back_func(), bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6')
        self.button_a.place(relx=0.55, rely=0.91)
    
    def back_func(self):
        self.button_b.destroy()
        self.instruc_label.destroy()
        self.button_a.destroy()
        self.maincanvas.update()
        self.button1 = tk.Button(self.maincanvas, text = "Confirm groups", command = lambda: self.get_coords(),  bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6') 
        self.button1.place(relx = 0.8, rely = 0.91)  
        self.instruc_label = tk.Label(self.maincanvas, text = "Instructions: \n Place the oldest group in the bottom left corner then for each subseqent group, place it directly above and move it to be overlapping, abutting or to have a gap.")
        self.instruc_label.config(bg='white', font=('helvetica', 12, 'bold'), wraplength=130)
        self.instruc_label.place(relx = 0.01, rely = 0.05, relwidth = 0.18, relheight = 0.85)
        
       
    def on_move(self, event):
        component=event.widget
        locx, locy = component.winfo_x(), component.winfo_y() #top left coords for where the object is
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height() #width of master canvas
        mx, my = component.winfo_width(), component.winfo_height() #width of boxes
        xpos=(locx+event.x)-(15)
        ypos=(locy+event.y)-int(my/2)
        if xpos>=0 and ypos>=0 and w-abs(xpos)>=0 and xpos <= (w - mx) and h-abs(ypos)>=0 and ypos<=(h-my):
           component.place(x=xpos,y=ypos)

    def full_chronograph_func(self):
        '''renders the chronological graph and forms the prev_phase and past_phase vectors'''
        self.prev_phase = ["start"]
        self.post_phase = []
        phase_list = self.step_1[2]
        if len(self.step_1[0][1][3]) != 0:
            self.graphcopy, self.phi_ref, self.null_phases = chrono_edge_add(self.graphcopy, self.step_1[0],
                                                                             self.step_1[1], self.menudict, self.phases,
                                                                             self.post_dict, self.prev_dict)
            self.post_phase.append(self.post_dict[self.phi_ref[0]])
            #adds the phase relationships to prev_phase and post_phase
            for i in range(1, len(self.phi_ref)-1):
                self.prev_phase.append(self.prev_dict[self.phi_ref[i]])
                self.post_phase.append(self.post_dict[self.phi_ref[i]])
            self.prev_phase.append(self.prev_dict[self.phi_ref[len(self.phi_ref)-1]])
        else:
            self.phi_ref = list(self.step_1[0][1][2])
        self.post_phase.append("end")
        del_phases = [i for i in self.phi_ref if i not in phase_list]
        ref_list = []
        for i in del_phases:
            ref = np.where(np.array(self.phi_ref) == i)[0][0]
            ref_list.append(ref)
        #deletes missing context references from phi_ref
        for index in sorted(ref_list, reverse=True):
            del self.phi_ref[index]
#change to new phase rels
        for i in ref_list:
            self.prev_phase[i] = 'gap'
            self.post_phase[i] = 'gap'
        self.graphcopy.graph['graph']={'splines':'ortho'}    
        atribs = nx.get_node_attributes(self.graphcopy, 'Group')
        nodes = self.graphcopy.nodes()
        edge_add = []
        edge_remove = []
        for i,j in enumerate(self.context_no_unordered):
            ####find paths in that phase
            
            phase = atribs[j]
            root = [i for i in nodes if "b_" + str(phase) in i][0]
            leaf = [i for i in nodes if "a_" + str(phase) in i][0]
            all_paths = []
            all_paths.extend(nx.all_simple_paths(self.graphcopy, source = root, target = leaf))

            if self.CONT_TYPE[i] == 'residual':
                for f in all_paths:
                    if j in f:
                        ind = np.where(np.array(f) == str(j))[0][0]
                        edge_add.append((f[ind - 1], f[ind+ 1]))
                for k in self.graphcopy.edges():
                    if k[0] == j:
                        edge_remove.append((k[0], k[1]))
            elif self.CONT_TYPE[i] == 'intrusive':
                for f in all_paths:
                    if j in f:
                        ind = np.where(np.array(f) == str(j))[0][0]
                        edge_add.append((f[ind -1], f[ind + 1]))
                for k in self.graphcopy.edges():
                    if k[1] == j:
                        edge_remove.append((k[0], k[1]))
        for a in edge_add:
            self.graphcopy.add_edge(a[0], a[1], arrowhead = 'none')
        for b in edge_remove:
            self.graphcopy.remove_edge(b[0], b[1])

        # networkx.drawing.nx_pydot.write_dot from networkx < 3.4 does not quote node attributes correctly if they contain characters such as :. Networkx 3.4 is only available for pythono >= 3.10, so a workaround is required for python 3.9 users.
        if packaging.version.parse(nx.__version__) < packaging.version.parse("3.4.0"):
            # Remove the contraction attribute from nodes.
            for i in nodes:
                self.graphcopy.nodes[i].pop("contraction", None)

        write_dot(self.graphcopy, 'fi_new_chrono')
        self.top.destroy()

class popupWindow8(object):
     def __init__(self, master, path):
         self.master = master
         self.path = path
         model_list_prev = [d for d in os.listdir(path) if os.path.isdir(path + '/' + d)]
         model_list = []
         for i in model_list_prev:
             mod_path = str(path) + "/" + str(i) + "/python_only/save.pickle"
             with open(mod_path, "rb") as f:
                 data = pickle.load(f)
                 load_check = data['load_check']
             if load_check == "loaded":
                model_list.append(i)


             
         self.top=tk.Toplevel(master)
         self.top.configure(bg ='white')
         self.top.title("Model calibration")
         self.top.geometry("1000x400")
         self.l=tk.Label(self.top,text="Which model/s would you like calibrate?", bg ='white', font='helvetica 12', fg = '#2f4858')
         self.l.place(relx = 0.3, rely = 0.1)
         self.e=tk.Listbox(self.top, font='helvetica 12', fg = '#2f4858', selectmode='multiple')
         self.e.place(relx = 0.3, rely = 0.2, relheight= 0.5, relwidth = 0.5)
  #       self.e.bind('<<ListboxSelect>>',tk.CurSelet)
         for items in model_list:
             self.e.insert('end',items)
         self.b=tk.Button(self.top,text='OK',command=self.cleanup,  bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6')
         self.b.place(relx = 0.3, rely = 0.7)
         self.b=tk.Button(self.top,text='Select all',command=self.selectall,  bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6')
         self.b.place(relx = 0.6, rely = 0.7)
     def selectall(self):
         self.e.select_set(0, 'end')
    
     def save_state_1(self, j):
        global mcmc_check, load_check, FILE_INPUT
        
        vars_list_1 = dir(self)
        var_list = [var for var in vars_list_1 if (('__' and 'grid' and 'get' and 'tkinter' and 'children') not in var) and (var[0] != '_')]          
        data = {}
        check_list = ["tkinter", "method", "__main__", 'PIL']
        for i in var_list:
            v = getattr(self, i)
            if not any(x in str(type(v)) for x in check_list):
               data[i] = v
        data['all_vars'] = list(data.keys())
        data['load_check'] = load_check
        data['mcmc_check'] = mcmc_check
        data["file_input"] = FILE_INPUT
        path = self.path + "/" +  str(j) + "/python_only/save.pickle"
        try:
            with open(path, "wb") as f:
                 pickle.dump(data, f)
            tk.messagebox.showinfo('Success', 'Your model has been saved')
        except Exception:
            tk.messagebox.showerror('Error', 'File not saved')             
     def load_cal_data(self, j):
        global mcmc_check, load_check, FILE_INPUT
        with open(self.path + "/" + str(j) + '/python_only/save.pickle', "rb") as f:
            data = pickle.load(f)
            vars_list = data['all_vars']
            for i in vars_list:
                setattr(self, i, data[i])
            FILE_INPUT = data['file_input']
            load_check = data['load_check']
            mcmc_check = data['mcmc_check']
        
     def cleanup(self):
         global mcmc_check
         values = [self.e.get(idx) for idx in self.e.curselection()]
         for i in values:
             self.load_cal_data(i)
             self.CONTEXT_NO, self.ACCEPT, self.PHI_ACCEPT, self.PHI_REF, self.A, self.P, self.ALL_SAMPS_CONT, self.ALL_SAMPS_PHI, self.resultsdict, self.all_results_dict = self.master.MCMC_func()
             mcmc_check = 'mcmc_loaded'
             self.save_state_1(i)
         self.top.destroy()
         

# @todo - not implemented yet, no tkinter code so didn't fit the pattern of other popup classes
class popupWindow9(object):
      def __init__(self, master, path):
          global mcmc_check
          self.master = master
          self.path = path
          model_list_labels = [(str(path) + '/graph_theory_tests_' + str(i), i, 'graph_theory_tests_' + str(i)) for i in self.master.graph.nodes()]
  #        model_list = []
          ref_wd = os.getcwd()
          base_cont_type =  self.master.CONT_TYPE
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
                  #remove_node_section   
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
            #change to new phase rels
                  self.graph_adjust(phase, phase_ref)
                  ######## sorting floating nodes
                  group_conts = [self.master.CONTEXT_NO[i] for i,j in enumerate(self.master.key_ref) if j == phase]
                  for m in group_conts:
                      if len(self.master.chrono_dag.out_edges(m)) == 0:
                         alph = [i for i in self.master.chrono_dag.nodes() if "a_" + phase in i]
                         self.master.chrono_dag.add_edge(m, alph[0], arrowhead = 'none')
                      if len(self.master.chrono_dag.in_edges(m)) == 0:
                          bet = [i for i in self.master.chrono_dag.nodes() if "b_" + phase in i]
                          self.master.chrono_dag.add_edge(bet[0], m, arrowhead = 'none')
    #############################    setting up the directorys
                  dirs4 = self.make_directories(i)
                  write_dot(self.master.chrono_dag, 'fi_new_chrono')
                  imgrender2(self.master.littlecanvas2.winfo_width(), self.master.littlecanvas2.winfo_height())  
                  imgrender(self.master.graph, self.master.littlecanvas.winfo_width(), self.master.littlecanvas.winfo_height())
                  self.master.ACCEPT = [[]]
                  while min([len(i) for i in self.master.ACCEPT]) < 20000:
                          self.master.CONTEXT_NO, self.master.ACCEPT, self.master.PHI_ACCEPT, self.master.PHI_REF, self.master.A, self.master.P, self.master.ALL_SAMPS_CONT, self.master.ALL_SAMPS_PHI, self.master.resultsdict, self.master.all_results_dict = self.master.MCMC_func()
                  mcmc_check = 'mcmc_loaded'
                  self.save_state_1(self.master, dirs4)

      def prob_overlap(self, ll1, ll2):
        ### hellenger distance
          dist_probs = np.array([(np.sqrt(ll2[1][i])-np.sqrt(j))**2 for i,j in enumerate(ll1[1])])
          h = 1 - 1/np.sqrt(2)*(np.sqrt(np.sum(dist_probs)))
          return h

        
      def node_importance(self, graph):
           G = graph.to_undirected() # setting up undirected graph          
           df_prob_overlap = pd.concat([pd.DataFrame([[str(i), str(j), self.prob_overlap(self.rc_llhds_dict[j], self.rc_llhds_dict[i])]], columns = ['node', 'neighbour', 'overlap_measure']) for i in G.nodes() for j in list(G.neighbors(i))])
          #katz
           df_prob_overlap.to_csv('overlap_df.csv')
           dd = nx.pagerank(G, alpha=0.85, personalization=None, max_iter=100, tol=1e-06, nstart=None, weight='weight', dangling=None)
           df = pd.DataFrame.from_dict(dd, orient = 'index')
           df.reset_index(inplace=True)
           df.columns = ['context', 'pagerank']
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
                  if self.master.prev_phase[phase_ref] == 'start':
                      phase_node = [i for i in self.master.chrono_dag.nodes() if "b_"+str(phase) in i]
                      self.master.chrono_dag.remove_node("a_" + str(phase))       
                      old_label = str(phase_node[0])
                      new_label = "a_"+ str(self.master.phi_ref[phase_ref + 1])
                      mapping = {old_label: new_label}
                      self.master.prev_phase.pop(phase_ref)
                      self.master.post_phase.pop(phase_ref)   
                      self.master.prev_phase[phase_ref] = 'start'
                  elif self.master.post_phase[phase_ref] == 'end':
                      phase_node = [i for i in self.master.chrono_dag.nodes() if "a_"+str(phase) in i]
                      self.master.chrono_dag.remove_node("b_" + str(phase))     
                      old_label = str(phase_node[0])
                      new_label = "b_"+ str(self.master.phi_ref[phase_ref -1])
                      mapping = {old_label: new_label}
                      self.master.prev_phase.pop(phase_ref)
                      self.master.post_phase.pop(phase_ref)   
                      self.master.post_phase[phase_ref] = 'end'
                  else:
                      phase_nodes = [i for i in self.master.chrono_dag.nodes() if phase in i]
                      self.master.chrono_dag.remove_edge(phase_nodes[0], phase_nodes[1])
                      self.master.chrono_dag = nx.contracted_nodes(self.master.chrono_dag, phase_nodes[0], phase_nodes[1]) 
                      new_label_1 = str(phase_nodes[0])
                      new_label = new_label_1.replace("a_"+str(phase), "a_"+ str(self.master.phi_ref[phase_ref + 1]))
                      mapping = {phase_nodes[0]: new_label}
                      self.master.prev_phase.pop(phase_ref)
                      self.master.post_phase.pop(phase_ref)   
                      self.master.prev_phase[phase_ref] = 'gap'
                      self.master.post_phase[phase_ref] = 'gap'
                  self.master.chrono_dag = nx.relabel_nodes(self.master.chrono_dag, mapping)
                  self.master.chrono_dag = phase_relabel(self.master.chrono_dag)
              self.master.chrono_dag.graph['graph']={'splines':'ortho'}    
              atribs = nx.get_node_attributes(self.master.chrono_dag, 'Group')
              nodes = self.master.chrono_dag.nodes()
              edge_add = []
              edge_remove = []
              for v,w in enumerate(self.master.CONTEXT_NO):
                    ####find paths in that phase
                    if self.master.CONT_TYPE[v] == 'residual':
                        phase = atribs[w]
                        root = [i for i in nodes if "b_" + str(phase) in i][0]
                        leaf = [i for i in nodes if "a_" + str(phase) in i][0]
                        all_paths = []
                        all_paths.extend(nx.all_simple_paths(self.master.chrono_dag, source = root, target = leaf))
                        for f in all_paths:
                            ind = np.where(np.array(f) == str(w))[0][0]
                            edge_add.append((f[ind - 1], f[ind+ 1]))
                        for k in self.master.chrono_dag.edges():
                            if k[0] == w:
                                edge_remove.append((k[0], k[1]))
                    elif self.master.CONT_TYPE[v] == 'intrusive':
                        for k in self.master.chrono_dag.edges():
                            if k[1] == w:
                                edge_remove.append((k[0], k[1]))
              for a in edge_add:
                    self.master.chrono_dag.add_edge(a[0], a[1], arrowhead = 'none')
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
          self.e.select_set(0, 'end')
    
      def save_state_1(self, master, j):
         global mcmc_check, load_check, FILE_INPUT
        
         vars_list_1 = dir(self.master)
         var_list = [var for var in vars_list_1 if (('__' and 'grid' and 'get' and 'tkinter' and 'children') not in var) and (var[0] != '_')]          
         data = {}
         check_list = ["tkinter", "method", "__main__", 'PIL']
         for i in var_list:
             v = getattr(master, i)
             if not any(x in str(type(v)) for x in check_list):
                data[i] = v
         data['all_vars'] = list(data.keys())
         data['load_check'] = load_check
         data['mcmc_check'] = mcmc_check
         data["file_input"] = FILE_INPUT
         path = j + "/save.pickle"
         if mcmc_check == 'mcmc_loaded': 
                results = data["all_results_dict"]
                df = pd.DataFrame()
                for i in results.keys():
                    df[i] = results[i][10000:]  
                results_path = os.getcwd() + "/mcmc_results/full_results_df"    
                df.to_csv(results_path)
                phasefile = data['phasefile']
                context_no = data['CONTEXT_NO']
                key_ref = [list(phasefile["Group"])[list(phasefile["context"]).index(i)] for i in context_no]
                df1 = pd.DataFrame(key_ref)   
                df1.to_csv('mcmc_results/key_ref.csv') 
                df2 = pd.DataFrame(context_no)
                df2.to_csv('mcmc_results/context_no.csv') 

         try:
             with open(path, "wb") as f:
                  pickle.dump(data, f)
         except Exception:
             tk.messagebox.showerror('Error', 'File not saved')        
             
      def load_cal_data(self, j):
         global mcmc_check, load_check, FILE_INPUT
         with open(self.path + "/" + str(j) + '/python_only/save.pickle', "rb") as f:
             data = pickle.load(f)
             vars_list = data['all_vars']
             for i in vars_list:
                 setattr(self, i, data[i])
             FILE_INPUT = data['file_input']
             load_check = data['load_check']
             mcmc_check = data['mcmc_check']

# @todo - not implemented yet, no tkinter code so didn't fit the pattern of other popup classes
class popupWindow10(object):
      def __init__(self, master, path):
          global mcmc_check
          self.master = master
          self.path = path
          # for i in range(20,140):
          #     katz_df_subset = katz_df_test.sort_values(by='pagerank', ascending = False).head(i)
        #   ref_wd = os.getcwd()
     #     con_list = list(katz_df_test['context'])
          base_cont_type =  self.master.CONT_TYPE
          base_key_ref = self.master.key_ref
          base_context_no = self.master.CONTEXT_NO
          base_graph = self.master.graph
          base_chrono_graph = self.master.chrono_dag
          base_phi_ref = self.master.phi_ref
          base_prev_phase = self.master.prev_phase
          base_post_phase = self.master.post_phase
          base_context_no_unordered = self.master.context_no_unordered
          
          
          for num in range(5,6):
          #for loop would start here
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
              #remove_node_section
              remove_conts = [i for i in self.master.CONTEXT_NO if i not in katz_df_test]
              print('remove contexts')
          
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
        #change to new phase rels
                  self.graph_adjust(phase, phase_ref)
                  ######## sorting floating nodes
                  group_conts = [self.master.CONTEXT_NO[i] for i,j in enumerate(self.master.key_ref) if j == phase]
                  for m in group_conts:
                      if len(self.master.chrono_dag.out_edges(m)) == 0:
                         alph = [i for i in self.master.chrono_dag.nodes() if "a_" + phase in i]
                         self.master.chrono_dag.add_edge(m, alph[0], arrowhead = 'none')
                      if len(self.master.chrono_dag.in_edges(m)) == 0:
                          bet = [i for i in self.master.chrono_dag.nodes() if "b_" + phase in i]
                          self.master.chrono_dag.add_edge(bet[0], m, arrowhead = 'none')
        #############################    setting up the directorys
              dirs4 = self.make_directories('testing' + str(num))
              write_dot(self.master.chrono_dag, 'fi_new_chrono')
              imgrender2(self.master.littlecanvas2.winfo_width(), self.master.littlecanvas2.winfo_height())  
              imgrender(self.master.graph, self.master.littlecanvas.winfo_width(), self.master.littlecanvas.winfo_height())
              self.master.ACCEPT = [[]]
              while min([len(i) for i in self.master.ACCEPT]) < 50000:
                       self.master.CONTEXT_NO, self.master.ACCEPT, self.master.PHI_ACCEPT, self.master.PHI_REF, self.master.A, self.master.P, self.master.ALL_SAMPS_CONT, self.master.ALL_SAMPS_PHI, self.master.resultsdict, self.master.all_results_dict = self.master.MCMC_func()
              mcmc_check = 'mcmc_loaded'
              self.save_state_1(self.master, dirs4)
              
      def katz_plus_overlap(self, path, refmodel, mode = 'strat'): 
          if mode == 'strat':
              katz_df_test = pd.read_csv(path + "/" + refmodel + "/katz_centr_strat.csv") # katz centrality worked out for the reference model
          elif mode == 'chrono':
              katz_df_test = pd.read_csv(path + "/" + refmodel + "/katz_centr_chrono.csv") 
          katz_df_test = katz_df_test[['context', 'pagerank']]
          katz_df_test['context'] = katz_df_test['context'].astype(str)
          katz_df_test = katz_df_test.loc[(not katz_df_test["context"].str.contains("a"))]
          katz_df_test = katz_df_test.loc[(not katz_df_test["context"].str.contains("b"))]
          katz_df_test = katz_df_test.transpose()
          katz_df = katz_df_test.rename(columns=katz_df_test.iloc[0]).drop(katz_df_test.index[0]).reset_index(drop=True)    
          ll_over_df = pd.read_csv(path + "/" + refmodel + "/overlap_df.csv")
          ll_over_df = pd.DataFrame(ll_over_df[['node', 'neighbour', 'overlap_measure']]) #overlap df for the reference model
          ll_over_df['neighbour'] = ll_over_df['neighbour'].astype(str)
          ll_over_df['node'] = ll_over_df['node'].astype(str)
          return katz_df, ll_over_df             
              
      def katz_w_weight(self, path):
         with open(path + "/reference_model/python_only/save.pickle", "rb") as f:
             data = pickle.load(f)   
         ref_graph = data['graph'] 
         katz_df, ll_over_df =  self.katz_plus_overlap(path, 'reference_model', mode = 'chrono')  
         ll_over_df['neighbour'] = ll_over_df['neighbour'].astype(str)
         ll_over_df['node'] = ll_over_df['node'].astype(str)
         for v, w in ref_graph.edges: 
             ref_graph.edges[v, w]["weight"] = float(ll_over_df.loc[(ll_over_df['node'] == v) & (ll_over_df['neighbour'] == w)]['overlap_measure'])
         weighted_katz = nx.pagerank(ref_graph.to_undirected())  
         return weighted_katz
              
              

      def top_nodes(self, num, phi_ref, context_no, key_ref, path):
          contexts = []
          weighted_katz = self.katz_w_weight(path)
          katz_vals = [weighted_katz[label] for i, label in enumerate(context_no)] 
          df = pd.DataFrame()
          df['context'] = context_no
          df['key_ref'] = key_ref
          df['katz_vals'] = katz_vals
          print('num')
          print(num)
          for i in phi_ref:
              df_subset = df.loc[df['key_ref'] == i]
              if len(df_subset) > num:
                  df_subset.sort_values(by = 'katz_vals', ascending=False)
                  conts = df_subset['context'][0:num]
                  [contexts.append(i) for i in conts]
              else:
                  conts = df_subset['context']
                  [contexts.append(i) for i in conts]
          return contexts
        
      def graph_adjust(self, phase, phase_ref):
              if phase not in self.master.key_ref:
                  self.master.phi_ref.pop(phase_ref)                                
                  if self.master.prev_phase[phase_ref] == 'start':
                      phase_node = [i for i in self.master.chrono_dag.nodes() if "b_"+str(phase) in i]
                      self.master.chrono_dag.remove_node("a_" + str(phase))       
                      old_label = str(phase_node[0])
                      new_label = "a_"+ str(self.master.phi_ref[phase_ref + 1])
                      mapping = {old_label: new_label}
                      self.master.prev_phase.pop(phase_ref)
                      self.master.post_phase.pop(phase_ref)   
                      self.master.prev_phase[phase_ref] = 'start'
                  elif self.master.post_phase[phase_ref] == 'end':
                      phase_node = [i for i in self.master.chrono_dag.nodes() if "a_"+str(phase) in i]
                      self.master.chrono_dag.remove_node("b_" + str(phase))     
                      old_label = str(phase_node[0])
                      new_label = "b_"+ str(self.master.phi_ref[phase_ref -1])
                      mapping = {old_label: new_label}
                      self.master.prev_phase.pop(phase_ref)
                      self.master.post_phase.pop(phase_ref)   
                      self.master.post_phase[phase_ref] = 'end'
                  else:
                      phase_nodes = [i for i in self.master.chrono_dag.nodes() if phase in i]
                      self.master.chrono_dag = nx.contracted_nodes(self.master.chrono_dag, phase_nodes[0], phase_nodes[1]) 
                      new_label_1 = str(phase_nodes[0])
                      new_label = new_label_1.replace("a_"+str(phase), "a_"+ str(self.master.phi_ref[phase_ref + 1]))
                      mapping = {phase_nodes[0]: new_label}
                      self.master.prev_phase.pop(phase_ref)
                      self.master.post_phase.pop(phase_ref)   
                      self.master.prev_phase[phase_ref] = 'gap'
                      self.master.post_phase[phase_ref] = 'gap'
                  self.master.chrono_dag = nx.relabel_nodes(self.master.chrono_dag, mapping)
                  self.master.chrono_dag = phase_relabel(self.master.chrono_dag)
              self.master.chrono_dag.graph['graph']={'splines':'ortho'}    
              atribs = nx.get_node_attributes(self.master.chrono_dag, 'Group')
              nodes = self.master.chrono_dag.nodes()
              edge_add = []
              edge_remove = []
              for v,w in enumerate(self.master.CONTEXT_NO):
                    ####find paths in that phase
                    if self.master.CONT_TYPE[v] == 'residual':
                        phase = atribs[w]
                        root = [i for i in nodes if "b_" + str(phase) in i][0]
                        leaf = [i for i in nodes if "a_" + str(phase) in i][0]
                        all_paths = []
                        all_paths.extend(nx.all_simple_paths(self.master.chrono_dag, source = root, target = leaf))
                        for f in all_paths:
                            ind = np.where(np.array(f) == str(w))[0][0]
                            edge_add.append((f[ind - 1], f[ind+ 1]))
                        for k in self.master.chrono_dag.edges():
                            if k[0] == w:
                                edge_remove.append((k[0], k[1]))
                    elif self.master.CONT_TYPE[v] == 'intrusive':
                        for k in self.master.chrono_graph.edges():
                            if k[1] == w:
                                edge_remove.append((k[0], k[1]))
              for a in edge_add:
                    self.master.chrono_graph.add_edge(a[0], a[1], arrowhead = 'none')
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
          self.e.select_set(0, 'end')
    
      def save_state_1(self, master, j):
         global mcmc_check, load_check, FILE_INPUT
        
         vars_list_1 = dir(self.master)
         var_list = [var for var in vars_list_1 if (('__' and 'grid' and 'get' and 'tkinter' and 'children') not in var) and (var[0] != '_')]          
         data = {}
         check_list = ["tkinter", "method", "__main__", 'PIL']
         for i in var_list:
             v = getattr(master, i)
             if not any(x in str(type(v)) for x in check_list):
                data[i] = v
         data['all_vars'] = list(data.keys())
         data['load_check'] = load_check
         data['mcmc_check'] = mcmc_check
         data["file_input"] = FILE_INPUT
         path = os.getcwd() + "/python_only/save.pickle"
         if mcmc_check == 'mcmc_loaded': 
                results = data["all_results_dict"]
                df = pd.DataFrame()
                for i in results.keys():
                    df[i] = results[i][10000:]  
                results_path = os.getcwd() + "/mcmc_results/full_results_df"    
                df.to_csv(results_path)
                phasefile = data['phasefile']
                context_no = data['CONTEXT_NO']
                key_ref = [list(phasefile["Group"])[list(phasefile["context"]).index(i)] for i in context_no]
                df1 = pd.DataFrame(key_ref)   
                df1.to_csv('mcmc_results/key_ref.csv') 
                df2 = pd.DataFrame(context_no)
                df2.to_csv('mcmc_results/context_no.csv') 

         try:
             with open(path, "wb") as f:
                  pickle.dump(data, f)
         except Exception:
             tk.messagebox.showerror('Error', 'File not saved')        
             
      def load_cal_data(self, j):
         global mcmc_check, load_check, FILE_INPUT
         with open(self.path + "/" + str(j) + '/python_only/save.pickle', "rb") as f:
             data = pickle.load(f)
             vars_list = data['all_vars']
             for i in vars_list:
                 setattr(self, i, data[i])
             FILE_INPUT = data['file_input']
             load_check = data['load_check']
             mcmc_check = data['mcmc_check']

class load_Window(object):
    # @note - this was triggered after a model was created. Not yet (fully) reimplemetned @todo
    def create_file(self, folder_dir, load):  
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
            tk.messagebox.showinfo('Tips:','model created successfully!')
            os.chdir(dirs)
        else:
            
            tk.messagebox.showerror('Tips','The folder name exists, please change it')
            self.cleanup()

class StartPage(tk.Frame):

    def __init__(self):
        self.h_1 = 0
        self.w_1 = 0
        
        self.transx = 0
        self.transy = 0
        self.meta1 = ""
        self.mode = ""
        self.node_del_tracker= []
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
        self.treeview_df = pd.DataFrame()
        self.file_menubar = ttk.Menubutton(self, text = 'File')

    def save_state_1(self):
        global mcmc_check, load_check, FILE_INPUT
        #converting metadata treeview to dataframe
        row_list = []
        columns = ('context', 'Reason for deleting')
        for child in self.tree2.get_children():
            row_list.append((self.tree2.item(child)['text'],self.tree2.item(child)['values']))
        self.treeview_df = pd.DataFrame(row_list, columns=columns)
        vars_list_1 = dir(self)
  #      self.node_importance(self.graph)
        var_list = [var for var in vars_list_1 if (('__' and 'grid' and 'get' and 'tkinter' and 'children') not in var) and (var[0] != '_')]          
        data = {}
        # Type names to not pickle when saving state. polychron is excluded to avoid classes which inherit from tk, this may be a bit too strong.
        check_list = ["tkinter", "method", "__main__", 'PIL', "polychron"]
        

        for i in var_list:
            v = getattr(self, i)
            if not any(x in str(type(v)) for x in check_list):
               data[i] = v
        data['all_vars'] = list(data.keys())
        data['load_check'] = load_check
        data['mcmc_check'] = mcmc_check
        data["file_input"] = FILE_INPUT
        if mcmc_check == 'mcmc_loaded': 
            results = data["all_results_dict"]
            df = pd.DataFrame()
            for i in results.keys():
                df[i] = results[i][10000:]  
            results_path = os.getcwd() + "/mcmc_results/full_results_df"    
            df.to_csv(results_path)
            phasefile = data['phasefile']
            context_no = data['CONTEXT_NO']
            key_ref = [list(phasefile["Group"])[list(phasefile["context"]).index(i)] for i in context_no]
            df1 = pd.DataFrame(key_ref)   
            df1.to_csv('mcmc_results/key_ref.csv') 
            df2 = pd.DataFrame(context_no)
            df2.to_csv('mcmc_results/context_no.csv') 
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
        with open('python_only/save.pickle', "rb") as f:
            data = pickle.load(f)
            vars_list = data['all_vars']
            for i in vars_list:
                setattr(self, i, data[i])
            FILE_INPUT = data['file_input']
            load_check = data['load_check']
            mcmc_check = data['mcmc_check']
        if self.graph is not None:
            self.littlecanvas.delete('all')
            self.rerender_stratdag()
            for i, j in enumerate(self.treeview_df['context']):
                 self.tree2.insert("", 'end', text=j, values=self.treeview_df['Reason for deleting'][i])

        if load_check == 'loaded':
            FILE_INPUT = None
            #manaually work this out as canvas hasn't rendered enough at this point to have a height and width in pixels
            height = 0.96*0.99*0.97*1000*0.96
            width = 0.99*0.37*2000*0.96  
            self.image2 = imgrender2(width, height)
            if self.image2 != 'No_image':
                self.littlecanvas2.delete('all')
                self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
                self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw",
                                                                         image=self.littlecanvas2.img)
    
                self.width2, self.height2 = self.image2.size
              #  self.imscale2 = 1.0  # scale for the canvaas image
                self.delta2 = 1.1  # zoom magnitude
                # Put image into container rectangle and use it to set proper coordinates to the image
                self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
                self.imscale2  = min(921/self.image2.size[0], 702/self.image2.size[1])
                self.littlecanvas.scale('all', 0, 0, self.delta2, self.delta2)  # rescale all canvas objects       
                self.show_image2()
                
                self.littlecanvas2.bind("<Configure>", self.resize2)


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

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        '''initilises page one'''
        tk.Frame.__init__(self, parent)
        self.controller = controller
        startpage = self.controller.get_page('StartPage')
        self.configure(background='#fcfdfd')
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg = '#FFE9D6')
        self.canvas.place(relx=0, rely=0.03, relwidth=1, relheight=0.97)
        self.button1 = tk.Button(self, text="Stratigraphy and supplementary data",  font='helvetica 12 bold', fg = '#2F4858',
                                  command=lambda: controller.show_frame("StartPage"), bd=0, highlightthickness=0, bg = '#AEC7D6')
        self.button1.place(relx=0.38, rely=0.0, relwidth=0.17, relheight=0.03)
        self.button1_a = tk.Button(self, text="Dating Results",  font='helvetica 12 bold', fg = '#8F4300',
                                   command=lambda: controller.show_frame("PageOne"), bd=0, highlightthickness=0, bg = '#FFE9D6')
        self.button1_a.place(relx=0.55, rely=0.0, relwidth=0.15, relheight=0.03)
        #define all variables that are used
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
        self.file_menubar = ttk.Menubutton(self, text = 'File',)
        # Adding File Menu and commands
        file = tk.Menu(self.file_menubar, tearoff = 0, bg = '#fcfdfd')#, font = ('helvetica',11))
        self.file_menubar["menu"] = file
        file.add_separator()
        file.add_command(label ='Save project progress', command = lambda: startpage.save_state_1(), font = ('helvetica 11 bold'))
        self.file_menubar.place(relx=0.0, rely=0, relwidth=0.1, relheight=0.03)
        self.view_menubar = ttk.Menubutton(self, text = 'View')
        # Adding File Menu and commands
        file1 = tk.Menu(self.view_menubar, tearoff = 0, bg = '#fcfdfd')#, font = ('helvetica',11))
        self.view_menubar["menu"] = file1
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)
        self.tool_menubar = ttk.Menubutton(self, text = 'Tools', )
        # Adding File Menu and commands
        file2 = tk.Menu(self.tool_menubar, tearoff = 0, bg = '#fcfdfd')#, font = ('helvetica',11))
        self.tool_menubar["menu"] = file2
        self.tool_menubar.place(relx=0.15, rely=0, relwidth=0.1, relheight=0.03)
        #forming and placing canvas and little canvas
        self.behindcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#CC5F00')
        self.behindcanvas.place(relx=0.6, rely=0.038, relwidth=0.39, relheight=0.96)
        #######################
        self.littlecanvas2_label = tk.Canvas(self.canvas, bd=0, bg='#CC5F00',
                                      selectborderwidth=0,  highlightthickness=0, insertwidth=0)
        self.littlecanvas2_label.place(relx=0.003, rely=0.011, relwidth=0.18, relheight=0.027)
        self.littlecanvas2_label_id = self.littlecanvas2_label.create_text(10, 5, anchor="nw", fill = 'white')
        self.littlecanvas2_label.itemconfig(self.littlecanvas2_label_id, text="Chronological graph", font='helvetica 12 bold' )
        #######################
        self.littlecanvas = tk.Canvas(self.behindcanvas, bd=0, bg='white',
                                      selectborderwidth=0,  highlightthickness=0, insertwidth=0)
        self.littlecanvas.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        ##########################################
        self.behindcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#CC5F00')
        self.behindcanvas2.place(relx=0.003, rely=0.038, relwidth=0.37, relheight=0.96)
        ##########################################
        self.littlecanvas_label = tk.Canvas(self.canvas, bd=0, bg='#CC5F00',
                                      selectborderwidth=0,  highlightthickness=0, insertwidth=0)
        self.littlecanvas_label.place(relx=0.6, rely=0.011, relwidth=0.18, relheight=0.027)
        self.littlecanvas_label_id = self.littlecanvas_label.create_text(10, 5, anchor="nw", fill = 'white')
        self.littlecanvas_label.itemconfig(self.littlecanvas_label_id, text='Posterior densities', font='helvetica 12 bold' )
        #########################################
        self.littlecanvas_a_label = tk.Canvas(self.canvas, bd=0, bg='#CC5F00',
                                      selectborderwidth=0,  highlightthickness=0, insertwidth=0)
        self.littlecanvas_a_label.place(relx=0.375, rely=0.518, relwidth=0.08, relheight=0.027)
        self.littlecanvas_a_label_id = self.littlecanvas_a_label.create_text(10, 5, anchor="nw", fill = 'white')
        self.littlecanvas_a_label.itemconfig(self.littlecanvas_a_label_id, text='Context list', font='helvetica 12 bold' )
        ############################################
        self.behindcanvas_a = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#CC5F00')
        self.behindcanvas_a.place(relx=0.375, rely=0.038, relwidth=0.223, relheight=0.45)
        ######################################
        self.littlecanvas_a = tk.Canvas(self.behindcanvas_a, bd=0, bg='white',
                                        selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas_a.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        #####################################################
        self.behindcanvas_3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#CC5F00')
        self.behindcanvas_3.place(relx=0.375, rely=0.545, relwidth=0.223, relheight=0.45)
        ########################################3
        self.littlecanvas2 = tk.Canvas(self.behindcanvas2, bd=0, bg='white',
                                       selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas2.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        #######################################################
        ################################
        self.littlecanvas3 = tk.Canvas(self.behindcanvas_3, bd=0, bg='white',
                                       selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas3.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.901)
        self.littlecanvas3_id = self.littlecanvas3.create_text(10, 10, anchor="nw",fill = '#0A3200')
        self.littlecanvas3.itemconfig(self.littlecanvas3_id, text="No contexts chosen for results. \n\nTo add a context to the results list right click on \nthe context you want then select 'add to list'",  font='helvetica 12 bold')
       
        ###############################################
        self.littlecanvas3_label = tk.Canvas(self.canvas, bd=0, bg='#CC5F00',
                                      selectborderwidth=0,  highlightthickness=0, insertwidth=0)
        self.littlecanvas3_label.place(relx=0.375, rely=0.011, relwidth=0.14, relheight=0.027)
        self.littlecanvas3_label_id = self.littlecanvas3_label.create_text(10, 5, anchor="nw", fill = 'white')
        self.littlecanvas3_label.itemconfig(self.littlecanvas3_label_id, text='Calendar date range estimates', font='helvetica 12 bold' )
        
        #################################
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


        #########deleted nodes##################
        self.button2 = ttk.Button(self.behindcanvas_3, text="Posterior densities",
                                  command=self.mcmc_output)
        self.button2.place(relx=0.008, rely=0.92, relwidth=0.402, relheight=0.07)
        self.button2a = ttk.Button(self.behindcanvas_3, text="HPD intervals",
                                   command=self.get_hpd_interval)
        self.button2a.place(relx=0.415, rely=0.92, relwidth=0.322, relheight=0.07)
        self.button3 = ttk.Button(self.behindcanvas_3, text="Clear list",
                                  command=self.clear_results_list)
        self.button3.place(relx=0.74, rely=0.92, relwidth=0.252, relheight=0.07)
        self.ResultList = [
            "Add to results list",
            "Get time elapsed",
            ]
        self.variable = tk.StringVar(self.littlecanvas)
        self.variable.set("Add to results list")
        self.testmenu2 = ttk.OptionMenu(self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder)


    def clear_results_list(self):
        '''deletes nodes from results lists'''
        self.results_list = []
        self.littlecanvas3.delete(self.results_text)
        self.canvas_plt.get_tk_widget().pack_forget()
        for item in self.tree_phases.get_children():
            self.tree_phases.delete(item)

    def node_finder(self, currentevent):
        '''finds nodes in the chronodag on results page'''
        self.testmenu2.place_forget()
        startpage = self.controller.get_page('StartPage')
        self.chronograph = startpage.chrono_dag
        x = str(self.chrono_nodes(currentevent))

        if self.variable.get() == 'Add to results list':
            self.littlecanvas3.delete(self.results_text)
            #ref = np.where(np.array(startpage.CONTEXT_NO) == x)[0][0]
            if x != 'no node':
                self.results_list.append(x)

        if len(self.phase_len_nodes) == 1:
            if self.variable.get() == "Get time elapsed between "+ str(self.phase_len_nodes[0]) + ' and another context':
                self.phase_len_nodes = np.append(self.phase_len_nodes, x)
                if self.canvas_plt is not None:
                    self.canvas_plt.get_tk_widget().pack_forget()
        #        font = {'size': 11}
                # using rc function
                
                self.fig = Figure()
           #     self.fig.rc('font', **font)
                LENGTHS = phase_length_finder(self.phase_len_nodes[0], self.phase_len_nodes[1], startpage.all_results_dict)
                plot1 = self.fig.add_subplot(111)
                plot1.hist(LENGTHS, bins='auto', color='#0504aa', rwidth = 1, density=True)
              #  plot1.xlabel('Time elapsed in calibrated years (cal BP)')
              #  plot1.ylabel('Probability density')
                plot1.spines['right'].set_visible(False)
                plot1.spines['top'].set_visible(False)
               # plot1.set_ylim([0, 0.05])
               # plot1.set_xlim([0, 400])
                plot1.title.set_text('Time elapsed between ' + str(self.phase_len_nodes[0]) + ' and '+ str(self.phase_len_nodes[1]))
                interval = list(mcmc.HPD_interval(np.array(LENGTHS[1000:])))
                columns = ('context_1', 'context_2', 'hpd_interval')
         #       self.fig.set_tight_layout(True)
                self.canvas_plt = FigureCanvasTkAgg(self.fig,
                                                    master=self.littlecanvas)
                self.canvas_plt.get_tk_widget().place(relx = 0, rely = 0, relwidth = 1)
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
                self.tree_phases.place(relx = 0, rely = 0, relwidth = 1)
                # add a scrollbar
                scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
                self.tree_phases.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky='nsew')
            self.ResultList.remove("Get time elapsed between "+ str(self.phase_len_nodes[0]) + ' and another context')
            self.testmenu2 = ttk.OptionMenu(self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder)
            self.phase_len_nodes = []

        if self.variable.get() == "Get time elapsed":
            if len(self.phase_len_nodes) == 1:
                self.ResultList.remove("Get time elapsed between "+ str(self.phase_len_nodes[0]) + ' and another context')
                self.testmenu2 = ttk.OptionMenu(self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder)
                self.phase_len_nodes = []
            self.phase_len_nodes = np.append(self.phase_len_nodes, x)
            self.ResultList.append("Get time elapsed between "+ str(self.phase_len_nodes[0]) + ' and another context')
            self.testmenu2 = ttk.OptionMenu(self.littlecanvas2, self.variable, self.ResultList[0], *self.ResultList, command=self.node_finder)
        self.littlecanvas3.delete(self.results_text)
        self.littlecanvas3.delete(self.littlecanvas3_id) 
        self.cont_canvas_list = ''
        for i in set(self.results_list):
            self.cont_canvas_list = self.cont_canvas_list + str(i) + '\n'
        self.results_text = self.littlecanvas3.create_text(5, 10, anchor="nw", text=self.cont_canvas_list, fill = '#0A3200', font = ('Helvetica 12 bold'))
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
        self.testmenu2.place(x=self.cursorx2, y=self.cursory2, relwidth= 0.2)
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
        '''loads posterior density plots into the graph'''
        global mcmc_check
        startpage = self.controller.get_page('StartPage')
        if mcmc_check == 'mcmc_loaded':
            if self.canvas_plt is not None:
                self.canvas_plt.get_tk_widget().pack_forget()
                self.toolbar.destroy()
            fig = Figure(figsize=(8, min(30, len(self.results_list)*3)),
                             dpi=100)
            for i, j in enumerate(self.results_list):
                if len(self.results_list) < 10:
                    n = len(self.results_list)
                else:
                    n = 10
                plt.rcParams['text.usetex']
                
                plot_index = int(str(n) + str(1) + str(i+1))
                plot1 = fig.add_subplot(plot_index)
                plot1.hist(startpage.resultsdict[j], bins='auto', color='#0504aa',
                           alpha=0.7, rwidth=1, density=True)
                plot1.spines['right'].set_visible(False)
                plot1.spines['top'].set_visible(False)
                fig.gca().invert_xaxis()
                plot1.set_ylim([0, 0.02])
                nodes = list(nx.topological_sort(startpage.chrono_dag))
                uplim = nodes[0]
                lowlim = nodes[-1]
                min_plot = min(startpage.resultsdict[uplim])
                max_plot = max(startpage.resultsdict[lowlim])
                plot1.set_xlim(min_plot, max_plot)
                node = str(j)
                if ('a' in node) or ('b' in node):
                    if 'a' in node:
                        node = node.replace('a_', r'\alpha_{')
                    if 'b' in node:
                        node = node.replace('b_', r'\beta_{')
                    if '=' in node:
                        node = node.replace('=', '} = ')
                    plot1.title.set_text(r"Group boundary " +  r"$" + node + "}$")
                else: 
                    plot1.title.set_text(r"Context " +  r"$" + node + "}$")

            fig.set_tight_layout(True)
            self.canvas_plt = FigureCanvasTkAgg(fig, master=self.littlecanvas)
            self.canvas_plt.draw()
    # creating the Matplotlib toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas_plt,
                                                self.littlecanvas)#
            self.toolbar.update()#
            self.canvas_plt.get_tk_widget().pack()

    def get_hpd_interval(self):
        '''loads hpd intervals into the results page'''
        global mcmc_check
        if len(self.results_list) != 0:
            startpage = self.controller.get_page('StartPage')
            USER_INP = simpledialog.askstring(title="HPD interval percentage",
                                              prompt="Please input HPD interval percentage. Note, 95% is used as standard \n \n Percentage:")
    
            self.lim = np.float64(USER_INP)/100
            if mcmc_check == 'mcmc_loaded':
                hpd_str = ""
                columns = ('context', 'hpd_interval')
                self.tree_phases = ttk.Treeview(self.littlecanvas_a, columns=columns, show='headings')
                self.tree_phases.heading('context', text='Context')
                self.tree_phases.heading('hpd_interval', text=str(USER_INP) + '% HPD interval')
                intervals = []
                for i, j  in enumerate(list(set(self.results_list))):
                    node = str(j)
                    interval = list(mcmc.HPD_interval(np.array(startpage.resultsdict[j][1000:]), lim=self.lim))
                # define headings
                    hpd_str = ""
                    refs = [k for k in range(len(interval)) if k %2]
                    for i in refs:
                        hpd_str = hpd_str + str(np.abs(interval[i-1])) + " - " + str(np.abs(interval[i])) + " Cal BP "
                    # add data to the treeview
                    intervals.append((node, hpd_str))
                for contact in intervals:
                    self.tree_phases.insert('', tk.END, values=contact)
                self.tree_phases.place(relx = 0, rely = 0, relwidth = 0.99)
                # add a scrollbar
                scrollbar = ttk.Scrollbar(self.littlecanvas_a, orient=tk.VERTICAL, command=self.tree_phases.yview)
                self.tree_phases.configure(yscroll=scrollbar.set)
                scrollbar.grid(row=0, column=1, sticky='nsew')
                self.littlecanvas_a.create_text(150, 80, text=hpd_str, fill = '#0A3200')

    def chronograph_render_post(self):
        if load_check == 'loaded':
            self.image2 = imgrender2(self.littlecanvas2.winfo_width(), self.littlecanvas2.winfo_height())
        #    scale_factor = min(self.littlecanvas2.winfo_width()/self.image_ws.size[0], self.littlecanvas2.winfo_height()/self.image_ws.size[1])                       
        #    self.image2 = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
           
            self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
            self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw",
                                                                     image=self.littlecanvas2.img)

            self.width2, self.height2 = self.image2.size
         #   self.imscale2 = 1.0  # scale for the canvaas image
            self.delta2 = 1.1  # zoom magnitude
                # Put image into container rectangle and use it to set proper coordinates to the image
            self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
            self.imscale2  = min(921/self.image2.size[0], 702/self.image2.size[1])
            self.littlecanvas2.scale('all', 0, 0, self.delta2, self.delta2)  # rescale all canvas objects       
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
        if int(bbox2[3]) == 1:
             bbox2 = [0, 0, 0.96*0.99*0.97*1000, 0.99*0.37*2000*0.96]
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
        """ returns the node that corresponds to the mouse cooridinates"""
        global node_df
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
        '''scales the nodes on chronodag'''
        x_scal = self.cursorx2 + self.transx2
        y_scal = self.cursory2 + self.transy2
        node = self.nodecheck(x_scal, y_scal)
        return node
