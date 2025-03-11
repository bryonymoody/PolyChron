#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 17:43:25 2021

@author: bryony
"""
import argparse
import copy
import csv
import os
import pickle
import sys
import tkinter as tk
import tkinter.font as tkFont
from importlib.metadata import version  # requires python >= 3.8
from tkinter import simpledialog, ttk
from tkinter.filedialog import askopenfile
from tkinter.messagebox import askquestion

import matplotlib as plt
import networkx as nx
import numpy as np
import pandas as pd
import pydot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from ttkthemes import ThemedStyle

import polychron.automated_mcmc_ordering_coupling_copy as mcmc

from . import globals
from .popupWindow import popupWindow
from .popupWindow2 import popupWindow2
from .popupWindow3 import popupWindow3
from .popupWindow4 import popupWindow4
from .popupWindow5 import popupWindow5
from .popupWindow6 import popupWindow6
from .popupWindow7 import popupWindow7
from .popupWindow8 import popupWindow8
from .popupWindow9 import popupWindow9
from .popupWindow10 import popupWindow10
from .util import (
    StdoutRedirector,
    clear_all,
    imagefunc,
    imgrender,
    imgrender2,
    imgrender_phase,
    node_coords_fromjson,
    node_del_fixed,
    phase_labels,
    phase_length_finder,
)

# @todo - these should be removed?
# Ensure the directory exists (this is a little aggressive)
globals.POLYCHRON_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
# Change into the projects dir
os.chdir(globals.POLYCHRON_PROJECTS_DIR)

#mainframe is the parent class that holds all the other classes
class MainFrame(tk.Tk):
    def __init__(self, *args, **kwargs):
        """initilaises the main frame for tkinter app"""
        tk.Tk.__init__(self, *args, **kwargs)
        os.chdir(globals.POLYCHRON_PROJECTS_DIR)
        load_Window(self)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        style = ThemedStyle(self)
        style.set_theme("arc")
        # f = tkFont.Font(family='helvetica', size=10, weight='bold')
        # s = ttk.Style()
        # s.configure('.', font=f)
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=12, weight = 'bold')
        style = ttk.Style(self)
        style.configure('TEntry', font=('Helvetica', 12, 'bold'))
        style.configure('TButton', font=('Helvetica', 12, 'bold'))
        style.configure('TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('TOptionMenu', font=('Helvetica', 12, 'bold'))
        style.configure('TTreeView', font=('Helvetica', 12, 'bold'))
        self.option_add("*Font", default_font)
        self.geometry("2000x1000")
        self.title(f"PolyChron {version('polychron')}")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        frame.config()

    def get_page(self, page_class):
        '''Shows the desired frame'''
        return self.frames[page_class]
        


            
class load_Window(object):
    def __init__(self,master):
        root_x = master.winfo_rootx()
        root_y = master.winfo_rooty()
        self.master = master
    # add offset
        win_x = root_x + 500
        win_y = root_y + 200
        self.top=tk.Toplevel(master)
        self.top.attributes("-topmost", True)
        self.top.title("PolyChron loading page")
    # set toplevel in new position
        self.top.geometry(f'1000x400+{win_x}+{win_y}') 
        self.folderPath = tk.StringVar()
        self.maincanvas = tk.Canvas(self.top, bg = 'white')
        self.maincanvas.place(relx=0, rely=0, relheight = 1, relwidth = 1)       
        self.canvas = tk.Canvas(self.top, bg = '#AEC7D6') 
        self.canvas.place(relx =0, rely= 0, relheight = 1, relwidth = 0.2) 
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
        [x.destroy() for x in [self.greeting, self.b, self.c, self.back, self.back1, self.l, self.MyListBox, self.text_1, self.user_input] if x is not None]
        self.maincanvas.update() 
        image1 = Image.open(globals.SCRIPT_DIR / "logo.png")
        logo = ImageTk.PhotoImage(image1.resize((360, 70)))
 #       self.imagetk2 = ImageTk.PhotoImage(image2.resize((int(x_2 - x_1), int(y_2 - y_1))))
        self.label1 = tk.Label(self.maincanvas, image=logo, bg = 'white')
        self.label1.image = logo        
        # Position image
        self.label1.place(relx = 0.2, rely = 0.2,  relheight = 0.2, relwidth = 0.4)
        self.greeting = tk.Label(self.maincanvas, text="Welcome to PolyChron, how would you like to proceed?", bg = 'white', font = ('helvetica 12 bold'), fg = '#2F4858', anchor = 'w' )
        self.greeting.place(relx = 0.22, rely = 0.45)
        self.b=tk.Button(self.maincanvas, text='Load existing project', command=lambda: self.load_proj(), bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6') 
        self.b.place(relx = 0.8, rely = 0.9)
        self.c=tk.Button(self.maincanvas, text='Create new project', command=lambda: self.new_proj(), bg = '#eff3f6', font = ('Helvetica 12 bold'),  fg = '#2F4858')
        self.c.place(relx = 0.62, rely = 0.9)

    # def getFolderPath(self):
    #     self.top.attributes("-topmost", False)
    #     folder_selected = tk.filedialog.askdirectory()        
    #     self.folderPath.set(folder_selected)
    #     os.chdir(self.folderPath.get())
  
        
    def load_proj(self):
        os.chdir(globals.POLYCHRON_PROJECTS_DIR)
        [x.destroy() for x in [self.label1, self.greeting, self.b, self.c, self.back, self.l, self.back1, self.MyListBox, self.text_1, self.user_input] if x is not None]
        self.maincanvas.update()

        self.l=tk.Label(self.maincanvas, text="Select project", bg = 'white', font = ('helvetica 14 bold'), fg = '#2F4858' )
        self.l.place(relx = 0.36, rely = 0.1)
        myList = [d for d in os.listdir(globals.POLYCHRON_PROJECTS_DIR) if os.path.isdir(d)]
        myList = [d for d in myList if (d != '__pycache__') and (d != 'Data')]
        mylist_var = tk.StringVar(value = myList)
        self.MyListBox = tk.Listbox(self.maincanvas, listvariable = mylist_var, bg = '#eff3f6', font = ('Helvetica 11 bold'),  fg = '#2F4858', selectmode = 'browse')  
        scrollbar = ttk.Scrollbar(
            self.maincanvas,
            orient='vertical',
            command=self.MyListBox.yview)
        self.MyListBox['yscrollcommand'] = scrollbar.set
        self.MyListBox.place(relx = 0.36, rely = 0.17, relheight=0.4, relwidth = 0.28)
        self.MyListBox.bind('<<ListboxSelect>>', self.items_selected)
        self.b=tk.Button(self.maincanvas,text='Load project', command=lambda: self.load_model(globals.proj_dir),  bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6') 
        self.b.place(relx = 0.8, rely = 0.9, relwidth = 0.19)
        self.top.bind('<Return>', (lambda event: self.load_model(globals.proj_dir)))
        self.back=tk.Button(self.maincanvas,text='Back', command=lambda: self.initscreen(),  bg = '#eff3f6', font = ('Helvetica 12 bold'),  fg = '#2F4858')
        self.back.place(relx = 0.21, rely = 0.01)
         
    
    def load_model(self, direc):
        [x.destroy() for x in [self.greeting, self.label1, self.b, self.c, self.back, self.back1, self.l, self.MyListBox] if x is not None] 
        if self.selected_langs is None:
            path = direc
        else:    
            path = os.getcwd() + "/" + self.selected_langs 
        os.chdir(path)
        self.maincanvas.update()

        self.l=tk.Label(self.maincanvas, text="Model list", bg = 'white', font = ('helvetica 14 bold'), fg = '#2F4858' )
        self.l.place(relx = 0.36, rely = 0.1)
       # myList_all = os.listdir(globals.POLYCHRON_PROJECTS_DIR)
        myList = [d for d in os.listdir(path) if os.path.isdir(d)]
        self.model_list = tk.StringVar(value = myList)
        self.MyListBox = tk.Listbox(self.maincanvas, listvariable = self.model_list, bg = '#eff3f6', font = ('Helvetica 11 bold'),  fg = '#2F4858', selectmode = 'browse')  
        scrollbar = ttk.Scrollbar(
            self.maincanvas,
            orient='vertical',
            command=self.MyListBox.yview)
        self.MyListBox['yscrollcommand'] = scrollbar.set
        self.MyListBox.place(relx = 0.36, rely = 0.17, relheight=0.4, relwidth = 0.28)
        self.MyListBox.bind('<<ListboxSelect>>', self.items_selected)
        self.b=tk.Button(self.maincanvas,text='Load selected model', command=lambda: self.cleanup2(),  bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6') 
        self.top.bind('<Return>', (lambda event: self.cleanup2()))
        self.b.place(relx = 0.8, rely = 0.9, relwidth = 0.195)
        self.back=tk.Button(self.maincanvas,text='Back', command=lambda: self.initscreen(), bg = '#eff3f6', font = ('Helvetica 12 bold'),  fg = '#2F4858')
        self.back.place(relx = 0.21, rely = 0.01)
        self.back1=tk.Button(self.maincanvas,text='Create new model', command=lambda: self.new_model(path),  bg = '#eff3f6', font = ('Helvetica 12 bold'),  fg = '#2F4858')
        self.back1.place(relx = 0.62, rely = 0.9, relwidth = 0.17)
        globals.proj_dir = path

    def items_selected(self, event):
        """ handle item selected event    """
        # get selected indices
        selected_indices = self.MyListBox.curselection()
        # get selected items
        self.selected_langs = ",".join([self.MyListBox.get(i) for i in selected_indices])

  
        
    def create_file(self, folder_dir, load):  
        dirs = os.path.join(globals.POLYCHRON_PROJECTS_DIR, folder_dir, self.model.get())
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
            globals.proj_dir = os.path.join(globals.POLYCHRON_PROJECTS_DIR, folder_dir)
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

    def new_proj(self):
        [x.destroy() for x in [self.greeting, self.label1, self.b, self.back1, self.c, self.back, self.l, self.MyListBox, self.text_1, self.user_input] if x is not None]
        self.maincanvas.update()
        self.folder = tk.StringVar() # Receiving user's folder_name selection
        self.text_1 = tk.Label(self.maincanvas, text = "Input project name:" ,bg = 'white', font = ('helvetica 14 bold'), fg = '#2F4858' )
        self.text_1.place(relx=0.4, rely= 0.2)
        self.user_input = tk.Entry(self.maincanvas, textvariable = self.folder)
        self.user_input.place(relx=0.35, rely=0.4, relwidth = 0.3, relheight = 0.08)
        self.b = tk.Button(self.maincanvas, text = "Submit ", command = lambda: self.new_model(self.folder.get()), bg = '#ec9949', font = ('Helvetica 12 bold'),  fg = '#2F4858')
        self.top.bind('<Return>', (lambda event: self.new_model(self.folder.get())))
        self.b.place(relx = 0.66, rely = 0.4)
        self.back=tk.Button(self.maincanvas,text='Back', command=lambda: self.initscreen(), bg = '#dcdcdc', font = ('helvetica 12 bold'), fg = '#2F4858' )
        self.back.place(relx = 0.21, rely = 0.01)
        
    def new_model(self, folder_dir, load = True):
        [x.destroy() for x in [self.greeting, self.label1, self.b, self.c, self.back, self.back1, self.l, self.MyListBox, self.text_1, self.user_input] if x is not None]
        self.maincanvas.update()
        self.model = tk.StringVar() # Receiving user's folder_name selection
        self.text_1 = tk.Label(self.maincanvas, text = "Input model name:" ,bg = 'white', font = ('helvetica 14 bold'), fg = '#2F4858' )
        self.text_1.place(relx=0.4, rely= 0.2)
        self.user_input = tk.Entry(self.maincanvas, textvariable = self.model)
        self.user_input.place(relx=0.35, rely=0.4, relwidth = 0.3, relheight = 0.08)
        self.b = tk.Button(self.maincanvas, text = "Submit ", command = lambda: self.create_file(folder_dir, load), bg = '#ec9949', font = ('Helvetica 12 bold'),  fg = '#2F4858')
        self.b.place(relx = 0.66, rely = 0.4)
        self.top.bind('<Return>', (lambda event:  self.create_file(folder_dir, load)))
        self.back=tk.Button(self.maincanvas,text='Back', command=lambda: self.new_proj(), bg = '#dcdcdc', font = ('helvetica 12 bold'), fg = '#2F4858' )
        self.back.place(relx = 0.21, rely = 0.01)    
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
    """ Main frame for tkinter app"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(background= 'white')
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg = '#AEC7D6')
        self.canvas.place(relx=0, rely=0.03, relwidth=1, relheight=0.97)
        self.button1 = tk.Button(self, text="Stratigraphy and supplementary data", font='helvetica 12 bold', fg = '#2F4858',
                                  command=lambda: controller.show_frame("StartPage"), bd=0, highlightthickness=0, bg = '#AEC7D6')
        self.button1.place(relx=0.38, rely=0.0, relwidth=0.17, relheight=0.03)
        self.button1_a = tk.Button(self, text="Dating Results",  font='helvetica 12 bold', fg = '#8F4300',
                                   command=lambda: controller.show_frame("PageOne"), bd=0, highlightthickness=0, bg = '#FFE9D6')
        self.button1_a.place(relx=0.55, rely=0.0, relwidth=0.15, relheight=0.03)
        #define all variables that are used
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
        self.strat_check = False
        self.phase_check = False
        self.phase_rel_check = False
        self.date_check = False
        # Adding File Menu and commands
        file = tk.Menu(self.file_menubar, tearoff = 0, bg = 'white', font = ("helvetica 12 bold"))
        self.file_menubar["menu"] = file
        file.add_separator()
        globals.FILE_INPUT = None
        file.add_command(label ='Load stratigraphic diagram file (.dot)', command=lambda: self.open_file1(), font="helvetica 12 bold")
        file.add_command(label ='Load stratigraphic relationship file (.csv)', command=lambda: self.open_file2(),font="helvetica 12 bold")
        file.add_command(label ='Load scientific dating file (.csv)', command=lambda: self.open_file3(), font="helvetica 12 bold")
        file.add_command(label ='Load context grouping file (.csv)', command=lambda: self.open_file4(), font="helvetica 12 bold")
        file.add_command(label ='Load group relationship file (.csv)', command=lambda: self.open_file5(), font="helvetica 12 bold")
        file.add_command(label ='Load context equalities file (.csv)', command=lambda: self.open_file6(), font="helvetica 12 bold")
        file.add_command(label ='Load new project', command = lambda: load_Window(MAIN_FRAME) , font="helvetica 12 bold")
        file.add_command(label ='Load existing model', command = lambda: load_Window.load_model(load_Window(MAIN_FRAME), globals.proj_dir), font="helvetica 12 bold")
        file.add_command(label ='Save changes as current model', command = lambda: self.save_state_1(), font="helvetica 12 bold")
        file.add_command(label ='Save changes as new model', command = lambda: self.refresh_4_new_model(controller, globals.proj_dir, load = False), font="helvetica 12 bold")
        file.add_separator()
        file.add_command(label ='Exit', command = lambda: self.destroy1)
        self.file_menubar.place(relx=0.00, rely=0, relwidth=0.1, relheight=0.03)
        self.view_menubar = ttk.Menubutton(self, text = 'View')
        # Adding File Menu and commands
        file1 = tk.Menu(self.view_menubar, tearoff = 0, bg = 'white', font = ('helvetica',11))
        self.view_menubar["menu"] = file1
        file1.add_command(label ='Display Stratigraphic diagram in phases', command=lambda: self.phasing(), font='helvetica 11')
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)
        
        self.tool_menubar = ttk.Menubutton(self, text = 'Tools')
        # Adding File Menu and commands
        file2 = tk.Menu(self.tool_menubar, tearoff = 0, bg = 'white', font = ('helvetica',11))
        self.tool_menubar["menu"] = file2
        #file2.add_separator()
        file2.add_command(label = 'Render chronological graph', command=lambda: self.chronograph_render_wrap(), font='helvetica 12 bold')
        file2.add_command(label = 'Calibrate model', command=lambda: self.load_mcmc(), font='helvetica 12 bold')
        file2.add_command(label = 'Calibrate multiple projects from project', command=lambda: popupWindow8(self, globals.proj_dir), font='helvetica 12 bold')
        file2.add_command(label = 'Calibrate node delete variations (alpha)', command=lambda: popupWindow9(self, globals.proj_dir), font='helvetica 12 bold')
        file2.add_command(label = 'Calibrate important variations (alpha)', command=lambda: popupWindow10(self, globals.proj_dir), font='helvetica 12 bold')
            
        # file2.add_separator()
        self.tool_menubar.place(relx=0.14, rely=0, relwidth=0.1, relheight=0.03)
        #############################
        self.behindcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.behindcanvas.place(relx=0.003, rely=0.038, relwidth=0.37, relheight=0.96)
        ############################
        self.behindcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.behindcanvas2.place(relx=0.38, rely=0.038, relwidth=0.37, relheight=0.96)
        ######################
        self.labelcanvas = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.labelcanvas.place(relx=0.003, rely=0.011, relwidth=0.18, relheight=0.027)
        self.labelcanvas1_id = self.labelcanvas.create_text(10, 3, anchor="nw", fill =  'white')
        self.labelcanvas.itemconfig(self.labelcanvas1_id, text="Stratigraphic graph", font='helvetica 12 bold')
        #########################
        self.littlecanvas = tk.Canvas(self.behindcanvas, bd=0, bg='white', selectborderwidth=0,  highlightthickness=0, insertwidth=0)
        self.littlecanvas_id = self.littlecanvas.create_text(10, 10, anchor="nw",fill =  '#2f4845')
        self.littlecanvas.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)        
        self.littlecanvas.itemconfig(self.littlecanvas_id, text="No stratigraphic graph loaded. \n \n \nTo load, go to File > Load stratigraphic diagram",  font='helvetica 12 bold')
        self.littlecanvas.update()
        ##############################
        
        #################
        self.littlecanvas2 = tk.Canvas(self.behindcanvas2, bd=0, bg='white', selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.littlecanvas2_id = self.littlecanvas2.create_text(10, 10, anchor="nw", fill = '#2f4845')
        self.littlecanvas2.itemconfig(self.littlecanvas2_id, text="No chronological graph loaded. \n \n \nYou must load a stratigraphic graph first. \nTo load, go to File > Load stratigraphic diagram \nTo load your chronological graph, go to Tools > Render chronological graph",  font='helvetica 12 bold')
        self.littlecanvas2.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
        ##########################
        self.labelcanvas2 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.labelcanvas2.place(relx=0.38, rely=0.011, relwidth=0.18, relheight=0.027)
        self.labelcanvas2_id = self.labelcanvas2.create_text(10, 3, anchor="nw", fill =  'white')
        self.labelcanvas2.itemconfig(self.labelcanvas2_id, text="Chronological graph", font='helvetica 12 bold')
        ###################
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
        self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes)
#meta data table
        self.labelcanvas3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.labelcanvas3.place(relx=0.755, rely=0.695, relwidth=0.17, relheight=0.029)
        self.behindcanvas3 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.behindcanvas3.place(relx=0.755, rely=0.719, relwidth=0.23, relheight=0.278)
        self.metatext_id = self.labelcanvas3.create_text(10, 5, anchor="nw", fill = 'white')
        self.labelcanvas3.itemconfig(self.metatext_id, text="Supplementary data",  font='helvetica 12 bold')
        self.tree1 = ttk.Treeview(self.canvas)
        self.tree1["columns"] = ["Data"]
        self.tree1.place(relx=0.758, rely=0.725)
        self.tree1.column("Data", anchor="w")
        self.tree1.heading("Data", text="Data")
#deleted contexts table
        self.labelcanvas4 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.labelcanvas4.place(relx=0.755, rely=0.04, relwidth=0.17, relheight=0.029)
        self.behindcanvas4 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.behindcanvas4.place(relx=0.755, rely=0.069, relwidth=0.23, relheight=0.278)
        self.delcontext_id = self.labelcanvas4.create_text(10, 5, anchor="nw", fill = 'white')
        self.labelcanvas4.itemconfig(self.delcontext_id, text="Deleted Contexts",  font='helvetica 12 bold')
        self.tree2 = ttk.Treeview(self.canvas)
        
        self.tree2.heading('#0', text="Context")
        self.tree2["columns"] = ["Meta"]
        self.tree2.place(relx=0.758, rely=0.0729)
        self.tree2.column("Meta", anchor="w")
        self.tree2.heading("Meta", text="Reason for deleting")

#deleted edges table
        self.labelcanvas5 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.labelcanvas5.place(relx=0.755, rely=0.371, relwidth=0.17, relheight=0.029)
        self.behindcanvas5 = tk.Canvas(self.canvas, bd=0, highlightthickness=0, bg = '#33658a')
        self.behindcanvas5.place(relx=0.755, rely=0.399, relwidth=0.23, relheight=0.278)
        self.deledge_id = self.labelcanvas5.create_text(10, 5, anchor="nw", fill = 'white')
        self.labelcanvas5.itemconfig(self.deledge_id, text="Deleted Stratigraphic Relationships",  font='helvetica 12 bold')
        self.tree3 = ttk.Treeview(self.canvas)
        self.tree3.heading('#0', text="Stratigraphic relationship")
        self.tree3["columns"] = ["Meta"]
        self.tree3.place(relx=0.758, rely=0.405)
        self.tree3.heading("Meta", text="Reason for deleting")
        f = dir(self)
        self.f_1 = [var for var in f if ('__' or 'grid' or 'get') not in var]
        self.littlecanvas.update()
        try: 
            self.restore_state()
        except FileNotFoundError:
            self.save_state_1()
        self.databutton = tk.Button(self, text="Data loaded  ↙", font='helvetica 12 bold', fg = 'white',
                                  command=lambda: self.display_data_func(), bd=0, highlightthickness=0, bg = '#33658a')
        self.databutton.place(relx=0.303, rely=0.04, relwidth=0.07, relheight=0.028)
        self.datacanvas = tk.Canvas(self.behindcanvas, bd=0, highlightthickness = 0, bg = '#33658a')
        self.datacanvas.place(relx=0.55, rely=0.0, relwidth=0.45, relheight=0.2)
        self.datalittlecanvas = tk.Canvas(self.datacanvas, bd=8, bg = 'white', highlightbackground= '#33658a', highlightthickness = 5)
        self.datalittlecanvas.place(relx=0.015, rely=0.015, relwidth=0.97, relheight=0.97)
        self.display_data_var = 'hidden'
        self.check_list_gen()
        tk.Misc.lift(self.littlecanvas)
    
    
    def refresh_4_new_model(self, controller, proj_dir, load):
        extra_top = load_Window.new_model(load_Window(MAIN_FRAME), proj_dir, load)
        self.wait_window(extra_top)
 #       self.save_state_1()
        
    def display_data_func(self):
        if self.display_data_var == 'hidden':
            tk.Misc.lift(self.datacanvas)
            self.databutton['text'] = "Data loaded ↗"
            self.display_data_var = 'onshow'
        else: 
            if self.display_data_var == 'onshow':
                tk.Misc.lift(self.littlecanvas)
                self.databutton['text'] = "Data loaded  ↙"
                self.display_data_var = 'hidden'
    
    def check_list_gen(self):
        if self.strat_check:
            strat = '‣ Stratigraphic relationships'
            col1 = 'green'
        else:
            strat ='‣ Stratigraphic relationships'
            col1 = 'black'
        if self.date_check:
            date = '‣ Radiocarbon dates'
            col2 = 'green'
        else:
            date = '‣ Radiocarbon dates'
            col2 = 'black'
        if self.phase_check:
            phase = '‣ Groups for contexts'
            col3 = 'green'
        else:
            phase = '‣ Groups for contexts'  
            col3 = 'black'                 
        if self.phase_rel_check:
            rels = '‣ Relationships between groups'
            col4 = 'green'
        else:    
            rels = '‣ Relationships between groups'
            col4 = 'black'
        self.datalittlecanvas.delete('all')
        self.datalittlecanvas.create_text(10, 20, anchor = 'nw', text=strat + "\n\n" , font=('Helvetica 12 bold'), fill = col1)
        self.datalittlecanvas.pack()
        self.datalittlecanvas.create_text(10, 50, anchor = 'nw', text=date + "\n\n" , font=('Helvetica 12 bold'), fill = col2)
        self.datalittlecanvas.pack()
        self.datalittlecanvas.create_text(10, 80, anchor = 'nw', text=phase + "\n\n" , font=('Helvetica 12 bold'), fill = col3)
        self.datalittlecanvas.pack()
        self.datalittlecanvas.create_text(10, 110, anchor = 'nw', text=rels, font=('Helvetica 12 bold'), fill = col4)
        self.datalittlecanvas.pack()

            
    def destroy1(self):
        '''destroys self.testmenu'''
        self.menubar.place_forget()
    def resid_check(self):
        '''Loads a text box to check if the user thinks any samples are residual'''
        MsgBox = tk.messagebox.askquestion('Residual and Intrusive Contexts', 'Do you suspect any of your samples are residual or intrusive?', icon='warning')
        if MsgBox == 'yes':
            
            pagetwo = PageTwo(self, self.controller)
            self.popup3 = pagetwo.popup4

        else:
            self.popup3 = popupWindow3(self, self.graph, self.littlecanvas2, self.phase_rels)

        def destroy(self):
            '''destroys self.testmenu'''
            self.testmenu.place_forget()
    #    # This is the function that removes the selected item when the label is clicked.
        def delete(self, *args):
            '''uses destroy then sets self.variable'''
            self.destroy()
            self.testmenu.place_forget()
            self.variable.set("Node Action")
    def save_state_1(self):
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
        data['load_check'] = globals.load_check
        data['mcmc_check'] = globals.mcmc_check
        data["file_input"] = globals.FILE_INPUT
        if globals.mcmc_check == 'mcmc_loaded': 
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
        with open('python_only/save.pickle', "rb") as f:
            data = pickle.load(f)
            vars_list = data['all_vars']
            for i in vars_list:
                setattr(self, i, data[i])
            globals.FILE_INPUT = data['file_input']
            globals.load_check = data['load_check']
            globals.mcmc_check = data['mcmc_check']
        if self.graph is not None:
            self.littlecanvas.delete('all')
            self.rerender_stratdag()
            for i, j in enumerate(self.treeview_df['context']):
                 self.tree2.insert("", 'end', text=j, values=self.treeview_df['Reason for deleting'][i])

        if globals.load_check == 'loaded':
            globals.FILE_INPUT = None
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
        self.testmenuWidth = len(max(self.OptionList, key=len))
        self.testmenu.config(width=self.testmenuWidth)
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
    def file_popup(self, file):
        self.nodedel=popupWindow7(self.canvas, file)
        self.canvas["state"] = "disabled" 
        self.master.wait_window(self.nodedel.top)
        self.canvas["state"] = "normal"
        return self.nodedel.value

    def open_file1(self):
        '''opens dot file'''
        file = askopenfile(mode='r', filetypes=[('Python Files', '*.dot')])
        globals.FILE_INPUT = file.name
        self.graph = nx.DiGraph(imagefunc(file.name), graph_attr={'splines':'ortho'})
        if globals.phase_true == 1:
            self.image = imgrender_phase(self.graph)
        else:
            self.image = imgrender(self.graph)
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw",
                                                               image=self.littlecanvas.img)

        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvaas image
      #  self.imscale  = min(921/self.image.size[0], 702/self.image.size[1])
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.bind("<Configure>", self.resize)
        self.littlecanvas.scale('all', 0, 0, self.delta, self.delta)  # rescale all canvas objects       
        self.show_image()
        self.littlecanvas.bind("<Configure>", self.resize)
        self.delnodes = []
        self.delnodes_meta = []
        self.canvas.delete('all')
        self.littlecanvas.bind("<Button-3>", self.preClick)

    def rerender_stratdag(self):
        '''rerenders stratdag after reloading previous project'''
        height = 0.96*0.99*0.97*1000
        width = 0.99*0.37*2000*0.96  
        if globals.phase_true == 1:
            self.image = imgrender_phase(self.graph)
        else:
            self.image = imgrender(self.graph, width, height)
        
        
             
 #       self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw",
                                                               image=self.littlecanvas.img)

        self.width, self.height = self.image.size
     #   self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.imscale  = min(width/self.image.size[0], height/self.image.size[1])

        self.delnodes = []
        self.delnodes_meta = []
        self.littlecanvas.bind("<Button-3>", self.preClick)
        self.littlecanvas.update()
        self.littlecanvas.scale('all', 0, 0, self.delta, self.delta)  # rescale all canvas objects       
        self.show_image()

    def chronograph_render_wrap(self):
        '''wraps chronograph render so we can assign a variable when runing the func using a button'''
        if (self.phase_rels is None) or (self.phasefile is None) or (self.datefile is None):
            tk.messagebox.showinfo("Error", "You haven't loaded in all the data required for a chronological graph")
        if globals.load_check == "loaded":
            answer = askquestion('Warning!', 'Chronological DAG already loaded, are you sure you want to write over it? You can copy this model in the file menu if you want to consider multiple models')
            if answer == 'yes':
            
                self.refresh_4_new_model(self.controller, globals.proj_dir, load = False)
                globals.load_check = 'not_loaded'
                self.littlecanvas2.delete('all')
                self.chrono_dag = self.chronograph_render()
                startpage = self.controller.get_page('StartPage')
                startpage.CONT_TYPE = self.popup3.CONT_TYPE
                startpage.prev_phase = self.popup3.prev_phase
                startpage.post_phase = self.popup3.post_phase
                startpage.phi_ref = self.popup3.phi_ref
                startpage.context_no_unordered = self.popup3.context_no_unordered
                startpage.graphcopy = self.popup3.graphcopy
                startpage.node_del_tracker = self.popup3.node_del_tracker

        else: 
            self.littlecanvas2.delete('all')
            self.chrono_dag = self.chronograph_render()
            startpage = self.controller.get_page('StartPage')
            startpage.CONT_TYPE = self.popup3.CONT_TYPE
            startpage.prev_phase = self.popup3.prev_phase
            startpage.post_phase = self.popup3.post_phase
            startpage.phi_ref = self.popup3.phi_ref
            startpage.context_no_unordered = self.popup3.context_no_unordered
            startpage.graphcopy = self.popup3.graphcopy
            startpage.node_del_tracker = self.popup3.node_del_tracker
    def open_file2(self):
        '''opens plain text strat file'''
        file = askopenfile(mode='r', filetypes=[('Python Files', '*.csv')])
        if file is not None:
            try:
                globals.FILE_INPUT = None
                self.littlecanvas.delete('all')
                self.stratfile = pd.read_csv(file, dtype=str)
                load_it = self.file_popup(self.stratfile)
                if load_it == 'load':
                    self.strat_check = True
                    G = nx.DiGraph(graph_attr={'splines':'ortho'})
                    set1 = set(self.stratfile.iloc[:, 0])
                    set2 = set(self.stratfile.iloc[:, 1])
                    set2.update(set1)
                    node_set = {x for x in set2 if x==x}
                    for i in set(node_set):
                        G.add_node(i, shape="box", fontname="helvetica", fontsize="30.0", penwidth="1.0", color='black')
                        G.nodes()[i].update({"Determination": [None, None]})
                        G.nodes()[i].update({"Group": None})
                    edges = []
                    for i in range(len(self.stratfile)):
                        a = tuple(self.stratfile.iloc[i, :])
                        if not pd.isna(a[1]):
                            edges.append(a)
                    G.add_edges_from(edges, arrowhead="none")
                    self.graph = G
                    if globals.phase_true == 1:
                        self.image = imgrender_phase(self.graph)
                    else:
                        self.image = imgrender(self.graph, self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
                        
                   #     scale_factor = min(self.littlecanvas.winfo_width()/self.image_ws.size[0], self.littlecanvas.winfo_height()/self.image_ws.size[1])                       
                   #     self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
                        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
                        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw",
                                                                               image=self.littlecanvas.img)                       
                        self.width, self.height = self.image.size
                   #     self.imscale = 1.0#, self.littlecanvas.winfo_height()/self.image.size[1])# scale for the canvaas image
                        self.delta = 1.1 # zoom magnitude
                        # Put image into container rectangle and use it to set proper coordinates to the image
                        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
                        self.bind("<Configure>", self.resize)
                        self.littlecanvas.bind("<Configure>", self.resize)
                        self.delnodes = []
                        self.delnodes_meta = []
                        self.littlecanvas.bind("<Button-3>", self.preClick)
                        self.imscale  = min(921/self.image.size[0], 702/self.image.size[1])
                        self.littlecanvas.scale('all', 0, 0, self.delta, self.delta)  # rescale all canvas objects       
                        self.show_image()
                    tk.messagebox.showinfo("Success", "Stratigraphic data loaded")
                    self.check_list_gen()
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")
                
    def open_file3(self):
        '''opens scientific dating file'''
        file = askopenfile(mode='r', filetypes=[('Python Files', '*.csv')])
        if file is not None:
            try:
                self.datefile = pd.read_csv(file)
                self.datefile = self.datefile.applymap(str)
                load_it = self.file_popup(self.datefile)
                if load_it == 'load':
                    for i, j in enumerate(self.datefile["context"]):
                        self.graph.nodes()[str(j)].update({"Determination":[self.datefile["date"][i], self.datefile["error"][i]]})
                    self.context_no_unordered = list(self.graph.nodes())
                self.date_check = True
                self.check_list_gen()
                tk.messagebox.showinfo("Success", "Scientific dating data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_file4(self):
        '''opens phase file'''
        file = askopenfile(mode='r', filetypes=[('Pythotransxn Files', '*.csv')])
        if file is not None:
            try:
                self.phasefile = pd.read_csv(file)
                self.phasefile = self.phasefile.applymap(str)
                load_it = self.file_popup(self.phasefile)
                if load_it == 'load':
                    for i, j in enumerate(self.phasefile["context"]):
                        self.graph.nodes()[str(j)].update({"Group":self.phasefile["Group"][i]})
                self.phase_check = True
                self.check_list_gen()
                tk.messagebox.showinfo("Success", "Grouping data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")

    def open_file5(self):
        '''opens phase relationship files'''
        file = askopenfile(mode='r', filetypes=[('Python Files', '*.csv')])
        if file is not None:
            try:
                phase_rel_df = pd.read_csv(file)
                self.phase_rels = [(str(phase_rel_df['above'][i]), str(phase_rel_df['below'][i])) for i in range(len(phase_rel_df))]
                self.file_popup(pd.DataFrame(self.phase_rels, columns = ['Younger group', 'Older group']))
                self.phase_rel_check = True
                self.check_list_gen()
                tk.messagebox.showinfo("Success", "Group relationships data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")
                
    def open_file6(self):
        '''opens files determining equal contexts (in time)'''
        file = askopenfile(mode='r', filetypes=[('Python Files', '*.csv')])
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
                if globals.phase_true == 1:
                    imgrender_phase(self.graph)
                else:
                    imgrender(self.graph, self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
                self.image = Image.open('testdag.png')
             #   scale_factor = min(self.littlecanvas.winfo_width()/self.image_ws.size[0], self.littlecanvas.winfo_height()/self.image_ws.size[1])                       
             #   self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
                self.width, self.height = self.image.size
                self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
                self.show_image()
                tk.messagebox.showinfo("Success", "Equal contexts data loaded")
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")
    def cleanup(self):
        '''destroys mcmc loading page when done'''
        self.top.destroy()
    def load_mcmc(self):
        '''loads mcmc loading page'''
        self.top = tk.Toplevel(self.littlecanvas)
        self.backcanvas = tk.Canvas(self.top, bg = '#AEC7D6')
        self.backcanvas.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
        self.top.geometry("%dx%d%+d%+d" % (700, 200, 600, 400))
        self.l = tk.Label(self.backcanvas, text="MCMC in progress", font = ('helvetica 14 bold'), fg = '#2F4858', bg = '#AEC7D6')
        self.l.place(relx = 0.35, rely = 0.26)
        outputPanel = tk.Label(self.backcanvas, font = ('helvetica 14 bold'), fg = '#2F4858', bg = '#AEC7D6')
        outputPanel.place(relx = 0.4, rely = 0.4)  
        pb1 = ttk.Progressbar(self.backcanvas, orient=tk.HORIZONTAL, length=400, mode='indeterminate')
        pb1.place(relx = 0.2, rely = 0.56)
        old_stdout = sys.stdout
        sys.stdout = StdoutRedirector(outputPanel, pb1)
        self.ACCEPT = [[]]
        while min([len(i) for i in self.ACCEPT]) < 50000:
            self.CONTEXT_NO, self.ACCEPT, self.PHI_ACCEPT, self.PHI_REF, self.A, self.P, self.ALL_SAMPS_CONT, self.ALL_SAMPS_PHI, self.resultsdict, self.all_results_dict = self.MCMC_func()
        globals.mcmc_check = 'mcmc_loaded'
        sys.stdout = old_stdout
        self.controller.show_frame('PageOne')
        f = dir(self)
        self.f_2 = [var for var in f if ('__' or 'grid' or 'get') not in var]
        self.newvars = [var for var in self.f_2 if var not in self.f_1]
        self.cleanup()

    def addedge(self, edgevec):
        '''adds an edge relationship (edgevec) to graph and rerenders the graph'''
        x_1 = edgevec[0]
        x_2 = edgevec[1]
        self.graph.add_edge(x_1, x_2, arrowhead='none')
        self.graph_check = nx.transitive_reduction(self.graph)
        if self.graph.edges() != self.graph_check.edges():
            self.graph.remove_edge(x_1, x_2)
            tk.messagebox.showerror("Redundant relationship", "That stratigraphic relationship is already implied by other relationships in the graph")
        if globals.phase_true == 1:
            imgrender_phase(self.graph)
        else:
            imgrender(self.graph, self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
        self.image = Image.open('testdag.png')
        self.show_image()

    def chronograph_render(self):
        '''initiates residual checking function then renders the graph when thats done'''
        if globals.load_check != 'loaded':
            globals.load_check = 'loaded'
            self.resid_check()
            self.image2 = imgrender2(self.littlecanvas2.winfo_width(), self.littlecanvas2.winfo_height())
            if self.image2 != 'No_image':
                try:
                    self.littlecanvas2.delete('all')
                    self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
                    self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw",
                                                                             image=self.littlecanvas2.img)
        
                    self.width2, self.height2 = self.image2.size
                    #self.imscale2 = 1.0  # scale for the canvaas image
                    self.delta2 = 1.1  # zoom magnitude
                    # Put image into container rectangle and use it to set proper coordinates to the image
                    self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
                    self.imscale2  = min(921/self.image2.size[0], 702/self.image2.size[1])
                    self.littlecanvas2.scale('all', 0, 0, self.delta2, self.delta2)  # rescale all canvas objects       
                    self.show_image2()
                    self.littlecanvas2.bind("<Configure>", self.resize2)
                except (RuntimeError, TypeError, NameError):
                    globals.load_check = 'not_loaded'
        return self.popup3.graphcopy


    def stratfunc(self, node):
        '''obtains strat relationships for node'''
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
        '''gathers all the inputs for the mcmc module and then runs it and returns resuslts dictionaries'''
        context_no = [x for x in list(self.context_no_unordered) if x not in self.node_del_tracker]
        TOPO = list(nx.topological_sort(self.chrono_dag))
        self.TOPO_SORT = [x for x in TOPO if (x not in self.node_del_tracker) and (x in context_no)]
        self.TOPO_SORT.reverse()
        context_no = self.TOPO_SORT
        self.key_ref = [list(self.phasefile["Group"])[list(self.phasefile["context"]).index(i)] for i in context_no]
        self.CONT_TYPE = [self.CONT_TYPE[list(self.context_no_unordered).index(i)] for i in self.TOPO_SORT]
        strat_vec = []
        resids = [j for i,j in enumerate(context_no) if self.CONT_TYPE[i] == 'residual']
        intrus = [j for i,j in enumerate(context_no) if self.CONT_TYPE[i] == 'intrusive']
        for i,j in enumerate(context_no): 
            if self.CONT_TYPE[i] == 'residual':
                low = []
                up = list(self.graph.predecessors(j))
            elif self.CONT_TYPE[i] == 'intrusive':
                low = list(self.graph.successors(j))
                up = []
            else:
                up = [k for k in self.graph.predecessors(j) if k not in resids]
                low = [k for k in self.graph.successors(j) if k not in intrus]
            strat_vec.append([up, low])
        #strat_vec = [[list(self.graph.predecessors(i)), list(self.graph.successors(i))] for i in context_no]
        self.RCD_EST = [int(list(self.datefile["date"])[list(self.datefile["context"]).index(i)]) for i in context_no]
        self.RCD_ERR = [int(list(self.datefile["error"])[list(self.datefile["context"]).index(i)]) for i in context_no]
        rcd_est = self.RCD_EST
        rcd_err = self.RCD_ERR
        self.prev_phase, self.post_phase = self.prev_phase, self.post_phase
        input_1 = [strat_vec, rcd_est, rcd_err, self.key_ref, context_no, self.phi_ref, self.prev_phase, self.post_phase, self.TOPO_SORT, self.CONT_TYPE]
        f = open('input_file', 'w')
        writer = csv.writer(f)
      #  for i in input_1:
        writer.writerow(input_1)
        f.close()
        CONTEXT_NO, ACCEPT, PHI_ACCEPT, PHI_REF, A, P, ALL_SAMPS_CONT, ALL_SAMPS_PHI = mcmc.run_MCMC(globals.CALIBRATION, strat_vec, rcd_est, rcd_err, self.key_ref, context_no, self.phi_ref, self.prev_phase, self.post_phase, self.TOPO_SORT, self.CONT_TYPE)
        phase_nodes, resultsdict, all_results_dict = phase_labels(PHI_REF, self.post_phase, PHI_ACCEPT, ALL_SAMPS_PHI)
        for i, j in enumerate(CONTEXT_NO):
            resultsdict[j] = ACCEPT[i]
        for k, l in enumerate(CONTEXT_NO):
            all_results_dict[l] = ALL_SAMPS_CONT[k]
        
        return CONTEXT_NO, ACCEPT, PHI_ACCEPT, PHI_REF, A, P, ALL_SAMPS_CONT, ALL_SAMPS_PHI, resultsdict, all_results_dict

    def nodecheck(self, x_current, y_current):
        """ returns the node that corresponds to the mouse cooridinates"""     
        node_inside = "no node"
        if globals.phase_true == 1:
            (graph,) = pydot.graph_from_dot_file('fi_new.txt')
            node_df_con = node_coords_fromjson(graph)
        else:
            node_df_con = node_coords_fromjson(self.graph)
        globals.node_df = node_df_con[0]
        
        xmax, ymax = node_df_con[1]
        #forms a dataframe from the dicitonary of coords
        x, y = self.image.size
        cavx = x*self.imscale
        cany = y*self.imscale
        xscale = (x_current)*(xmax)/cavx
        yscale = (cany-y_current)*(ymax)/cany
        for n_ind in range(globals.node_df.shape[0]):
            if ((globals.node_df.iloc[n_ind].x_lower < xscale < globals.node_df.iloc[n_ind].x_upper) and
                    (globals.node_df.iloc[n_ind].y_lower < yscale < globals.node_df.iloc[n_ind].y_upper)):
                node_inside = globals.node_df.iloc[n_ind].name
                self.graph[node_inside]
        return node_inside


    def edge_render(self):
        """renders string for deleted edges"""
        self.edges_del = self.edge_nodes
        ednodes = str(self.edges_del[0]) + ' above '+ str(self.edges_del[1])
        self.temp = str(self.temp).replace('[', '')
        self.temp = str(self.temp).replace(']', '')
        self.temp = self.temp + str(ednodes.replace("'", ""))
        
        
    def node_del_popup(self):
        self.nodedel=popupWindow5(self.canvas)
        self.canvas["state"] = "disabled" 
        self.master.wait_window(self.nodedel.top)
        self.canvas["state"] = "normal"
        return self.nodedel.value
    def edge_del_popup(self):
        self.nodedel=popupWindow6(self.canvas)
        self.canvas["state"] = "disabled" 
        self.master.wait_window(self.nodedel.top)
        self.canvas["state"] = "normal"
        return self.nodedel.value
        
    def nodes(self, currentevent):
        """performs action using the node and redraws the graph"""
        self.testmenu.place_forget()
        #deleting a single context
        if self.variable.get() == "Delete context":
            if self.node != "no node":
                if globals.load_check == 'loaded':
                    globals.load_check = 'not_loaded'
                    answer = askquestion('Warning!', 'Chronological DAG already loaded, do you want to save this as a new model first? \n\n Click Yes to save as new model and No to overwrite existing model')
                    if answer == 'yes':
                        self.refresh_4_new_model(self.controller, globals.proj_dir, load = False)
                    self.littlecanvas2.delete('all')       
             #   self.graph.remove_node(self.node)
                self.graph = node_del_fixed(self.graph, self.node)
                self.nodedel_meta = self.node_del_popup()
                self.delnodes = np.append(self.delnodes, self.node)
                self.delnodes_meta.append(self.nodedel_meta)
                self.tree2.insert("", 'end', text=self.node, values=[self.nodedel_meta])
        #presents popup list to label new context
        if self.variable.get() == "Add new contexts":
            if globals.load_check == 'loaded':
                answer = askquestion('Warning!', 'Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model')
                if answer == 'yes':
                    self.refresh_4_new_model(self.controller, globals.proj_dir, load = False)
                self.littlecanvas2.delete('all')
                globals.load_check = 'not_loaded'
            self.w = popupWindow(self)
            self.wait_window(self.w.top)
            self.node = self.w.value
            self.graph.add_node(self.node, shape="box", fontsize="30.0",
                                fontname="helvetica", penwidth="1.0")
       #checks if any nodes are in edge node to see if we want to add/delete a context
        if len(self.edge_nodes) == 1:
            #first case deletes strat relationships
            if self.variable.get() == "Delete stratigraphic relationship with "+ str(self.edge_nodes[0]):
                self.edge_nodes = np.append(self.edge_nodes, self.node)
                self.reason = self.edge_del_popup()
                if globals.load_check == 'loaded':
                    answer = askquestion('Warning!', 'Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model')
                    if answer == 'yes':
                        self.refresh_4_new_model(self.controller, globals.proj_dir, load = False)
                    self.littlecanvas2.delete('all')
                    globals.load_check = 'not_loaded'
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
                        tk.messagebox.showinfo('Error', 'An edge doesnt exist between those nodes')

                self.OptionList.remove("Delete stratigraphic relationship with "+ str(self.edge_nodes[0]))
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0],*self.OptionList, command=self.nodes)
                self.edge_nodes = []
            #second case is adding a strat relationship
            elif self.variable.get() == ("Place "+ str(self.edge_nodes[0]) + " Above"):
                    if globals.load_check == 'loaded':
                     answer = askquestion('Warning!', 'Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model')
                     if answer == 'yes':
                         self.refresh_4_new_model(self.controller, globals.proj_dir, load = False)
                    self.littlecanvas2.delete('all')
                    globals.load_check = 'not_loaded'
                    self.edge_nodes = np.append(self.edge_nodes, self.node)
                    self.addedge(self.edge_nodes)
                    self.OptionList.remove("Place "+ str(self.edge_nodes[0]) + " Above")
                    self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes)
                    self.edge_nodes = []
        #sets up the menu to delete the strat relationship once user picks next node
        if self.variable.get() == "Delete stratigraphic relationship":
            if len(self.edge_nodes) == 1:
                self.OptionList.remove("Delete stratigraphic relationship with "+ str(self.edge_nodes[0]))
                self.edge_nodes = []
            self.edge_nodes = np.append(self.edge_nodes, self.node)
            self.OptionList.append("Delete stratigraphic relationship with "+ str(self.edge_nodes[0]))
            self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes)
        #equates too contexts
        if len(self.comb_nodes) == 1:
            if self.variable.get() == "Equate context with "+ str(self.comb_nodes[0]):
                if globals.load_check == 'loaded':
                    answer = askquestion('Warning!', 'Chronological DAG already loaded, do you want to save this as a new model first? \n Click YES to save as new model and NO to overwrite existing model')
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
                    if e.__class__.__name__ == 'NetworkXError':
                        tk.messagebox.showinfo('Error!', 'This creates a cycle so you cannot equate these contexts')
                self.OptionList.remove("Equate context with "+ str(self.comb_nodes[0]))
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes)
                self.comb_nodes = []
        #sets up menu to equate context for when user picks next node
        if self.variable.get() == "Equate context with another":
            if len(self.comb_nodes) == 1:
                self.OptionList.remove("Equate context with "+ str(self.comb_nodes[0]))
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes)
                self.comb_nodes = []
            self.comb_nodes = np.append(self.comb_nodes, self.node)
            self.OptionList.append("Equate context with "+ str(self.comb_nodes[0]))
            self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes)
        
        if self.variable.get() == "Supplementary menu":
            self.w = popupWindow2(self, self.graph, self.canvas)
        if self.variable.get() == "Get supplementary data for this context":
            self.stratinfo = self.stratfunc(self.node)
            self.metadict2= {}
            self.metadict = self.graph.nodes()[str(self.node)]
            self.metadict2['Contexts above'] = [self.stratinfo[0]]
            self.metadict2['Contexts below'] = [self.stratinfo[1]]
            self.meta1 = pd.DataFrame.from_dict(self.metadict, orient = 'index')
            self.meta2 = pd.DataFrame.from_dict(self.metadict2, orient = 'index')
            self.meta = pd.concat([self.meta1, self.meta2])
            self.meta = self.meta.loc["Determination":"Contexts below"]
            self.meta.columns = ["Data"]
            if self.meta.loc["Determination"][0] != "None":
                self.meta.loc["Determination"][0] = str(self.meta.loc["Determination"][0][0]) + " +- " + str(self.meta.loc["Determination"][0][1]) + " Carbon BP"
            self.canvas.itemconfig(self.metatext_id, text="Supplementary of node " + str(self.node),  font='helvetica 12 bold')
            cols = list(self.meta.columns)
       #     self.tree1 = ttk.Treeview(self.canvas)
            clear_all(self.tree1)
            self.tree1["columns"] = cols
            self.tree1.place(relx=0.758, rely=0.725, relwidth = 0.225)
            self.tree1.column("Data", anchor="w")
            self.tree1.heading("Data", text="Data", anchor='w')
            for index, row in self.meta.iterrows():
                self.tree1.insert("", 0, text=index, values=list(row))
            self.tree1.update()
        #sets up menu to add strat relationships for when user picks next node
        if self.variable.get() == "Place above other context":
            if len(self.edge_nodes) == 1:
                self.OptionList.remove("Place "+ str(self.edge_nodes[0]) + " Above")
                self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes)
                self.edge_nodes = []
            self.edge_nodes = np.append(self.edge_nodes, self.node)
            self.OptionList.append("Place "+ str(self.edge_nodes[0]) + " Above")
            self.testmenu = ttk.OptionMenu(self.littlecanvas, self.variable, self.OptionList[0], *self.OptionList, command=self.nodes)
        if self.variable.get() == "Get stratigraphic information":
            self.stratfunc(self.node) 
        if globals.phase_true == 1:
            imgrender_phase(self.graph)
        else:
            imgrender(self.graph, self.littlecanvas.winfo_width(), self.littlecanvas.winfo_height())
        self.image = Image.open('testdag.png')
        self.width, self.height = self.image.size
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.show_image()
        self.variable.set("Node Action")
        self.littlecanvas.unbind('<Button-1>')
        self.littlecanvas.bind('<Button-1>', self.move_from)
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
        self.littlecanvas.scale('all', 0, 0, scale, scale)  # rescale all canvas objects
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
        if int(bbox2[3]) == 1:
             bbox2 = [0, 0, 0.96*0.99*0.97*1000, 0.99*0.37*2000*0.96]
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
            self.littlecanvas2.imagetk2 = self.imagetk2


    def phasing(self):
        """runs image render function with phases on seperate levels"""
        globals.phase_true = 1
        self.image = imgrender_phase(self.graph)
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw",
                                                               image=self.littlecanvas.img)
        self.width, self.height = self.image.size
      #  self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.imscale  = min(921/self.image.size[0], 702/self.image.size[1])
        self.littlecanvas.scale('all', 0, 0, self.delta, self.delta)  # rescale all canvas objects       
        self.show_image()
        self.bind("<Configure>", self.resize)
        self.littlecanvas.bind("<Configure>", self.resize)
        self.delnodes = []
        self.delnodes_meta = []
        self.canvas.delete('all')
        self.littlecanvas.bind("<Button-3>", self.preClick)
        self.show_image()


    def resize(self, event):
        """resizes image on canvas"""
        img = Image.open('testdag.png')#.resize((event.width, event.height), Image.ANTIALIAS)
        self.littlecanvas.img = ImageTk.PhotoImage(img)
        self.w_1 = event.width
        self.h_1 = event.height
        self.littlecanvas.itemconfig(self.littlecanvas_img, image=self.littlecanvas.img)

        
    def resize2(self, event):
        """resizes image on canvas"""
        img = Image.open('testdag_chrono.png')#.resize((event.width, event.height), Image.ANTIALIAS)
        self.littlecanvas2.img = ImageTk.PhotoImage(img)
        self.w_1 = event.width
        self.h_1 = event.height
        self.littlecanvas2.itemconfig(self.littlecanvas2_img, image=self.littlecanvas2.img)



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
        startpage = self.controller.get_page('StartPage')
        if globals.mcmc_check == 'mcmc_loaded':
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
        if len(self.results_list) != 0:
            startpage = self.controller.get_page('StartPage')
            USER_INP = simpledialog.askstring(title="HPD interval percentage",
                                              prompt="Please input HPD interval percentage. Note, 95% is used as standard \n \n Percentage:")
    
            self.lim = np.float64(USER_INP)/100
            if globals.mcmc_check == 'mcmc_loaded':
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
        if globals.load_check == 'loaded':
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
        node_inside = "no node"
        node_df_con = node_coords_fromjson(self.chronograph)
        globals.node_df = node_df_con[0]
        xmax, ymax = node_df_con[1]
        #forms a dataframe from the dicitonary of coords
        x, y = self.image2.size
        cavx = x*self.imscale2
        cany = y*self.imscale2
        xscale = (x_current)*(xmax)/cavx
        yscale = (cany-y_current)*(ymax)/cany
        outline = nx.get_node_attributes(self.chronograph, 'color')
        for n_ind in range(globals.node_df.shape[0]):
            if ((globals.node_df.iloc[n_ind].x_lower < xscale < globals.node_df.iloc[n_ind].x_upper) and
                    (globals.node_df.iloc[n_ind].y_lower < yscale < globals.node_df.iloc[n_ind].y_upper)):
                node_inside = globals.node_df.iloc[n_ind].name
                outline[node_inside] = 'red'
                nx.set_node_attributes(self.chronograph, outline, 'color')
        return node_inside

    def chrono_nodes(self, current):
        '''scales the nodes on chronodag'''
        x_scal = self.cursorx2 + self.transx2
        y_scal = self.cursory2 + self.transy2
        node = self.nodecheck(x_scal, y_scal)
        return node

class PageTwo(object):
    def __init__(self, master, controller):
        '''initilaising page two'''
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
        startpage = self.controller.get_page('StartPage')
        self.graphcanvas = tk.Canvas(self.canvas, bd=0, bg='white',
                                     selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.graphcanvas.place(relx=0.02, rely=0.05, relwidth=0.35, relheight=0.9)
        label = tk.Message(self.top, text='Using this page: \n\n Please click on the buttons below to set into residual or intrusive mode. Then double right click on any context to set as residual/intrusive. \n\n Note that orange boxes denote intrusive contexts and blue boxes denote residual contexts. \n\n If you have clicked on a context by mistake, double right click to remove any label attributed to the context.')
        label.place(relx=0.4, rely=0.05)
        label2 = ttk.Label(self.canvas, text='Residual Contexts')
        label2.place(relx=0.4, rely=0.4)
        self.graphcanvas.update()
        self.residcanvas = tk.Canvas(self.canvas, bd=0, bg='white',
                                     selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.residcanvas.place(relx=0.4, rely=0.42, relwidth=0.35, relheight=0.08)
        self.intrucanvas = tk.Canvas(self.canvas, bd=0, bg='white',
                                     selectborderwidth=0, highlightthickness=0, insertwidth=0)
        self.intrucanvas.place(relx=0.4, rely=0.54, relwidth=0.35, relheight=0.08)

        self.resid_label = ttk.Label(self.residcanvas, text=self.resid_list)
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        scroll_bar1 = ttk.Scrollbar(self.residcanvas)
        scroll_bar1.pack(side=tk.RIGHT)
        self.intru_label = ttk.Label(self.intrucanvas, text=self.intru_list)
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        scroll_bar2 = ttk.Scrollbar(self.intrucanvas)
        scroll_bar2.pack(side=tk.RIGHT)
        label3 = ttk.Label(self.canvas, text='Intrusive Contexts')
        label3.place(relx=0.4, rely=0.52)
        if startpage.graph is not None:
            self.graphcopy = self.load_graph()
            self.imscale2  = min(921/self.image.size[0], 702/self.image.size[1])
            self.graphcanvas.scale('all', 0, 0, self.delta2, self.delta2)  # rescale all canvas objects       
            self.show_image2()
        self.graphcanvas.update()
        button = ttk.Button(self.top, text="Proceed",
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
        '''wraps popup4 so we can get the variables from self.popup4'''
        self.popup4 = popupWindow4(self, controller, self.resid_list, self.intru_list, self.node_del_tracker, self.graphcopy)
        self.top.destroy()
                
    def mode_set(self, var_set):
        '''sets the mode to residual or intrusive and highlights the colour of the  button'''
        self.modevariable = var_set
        if var_set == 'resid':
            button1 = tk.Button(self.top, text="Residual mode",
                                 command=lambda: self.mode_set('resid'), background='orange')
            button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
            button3 = tk.Button(self.top, text="Intrusive mode",
                                 command=lambda: self.mode_set('intru'))
            button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)
        if var_set == 'intru':
            button1 = tk.Button(self.top, text="Residual mode",
                                 command=lambda: self.mode_set('resid'))
            button1.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
            button3 = tk.Button(self.top, text="Intrusive mode",
                                 command=lambda: self.mode_set('intru'), background='lightgreen')
            button3.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)

    def tkraise(self, aboveThis=None):
        '''runs loads graph'''
        self.load_graph()
        super().tkraise(aboveThis)

    def load_graph(self):
        '''loads graph on results page'''
        #loads start page so we get get variables from that class
        startpage = self.controller.get_page('StartPage')
        self.graphcopy = copy.deepcopy(startpage.graph)
        datadict = nx.get_node_attributes(self.graphcopy, 'Determination')
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
        if globals.phase_true == 1:
            self.image = imgrender_phase(self.graphcopy)
        else:
            self.image = imgrender(self.graphcopy, self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height())
    #    scale_factor = min(self.graphcanvas.winfo_width()/self.image_ws.size[0], self.graphcanvas.winfo_height()/self.image_ws.size[1])                       
   #     self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
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
        self.graphcanvas.scale('all', 0, 0, scale2, scale2)  # rescale all canvas objects
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
        """ returns the node that corresponds to the mouse cooridinates"""
        startpage = self.controller.get_page('StartPage')
        #updates canvas to get the right coordinates
        startpage.update_idletasks()

        node_inside = "no node"
        if self.graphcopy is not None:
            #gets node coordinates from the graph
            node_df_con = node_coords_fromjson(self.graphcopy)
            #forms a dataframe from the dicitonary of coords
            globals.node_df = node_df_con[0]
            xmax, ymax = node_df_con[1]
            #scales the coordinates using the canvas and image size
            x, y = self.image.size
            cavx = x*self.imscale2
            cany = y*self.imscale2
            xscale = (x_current)*(xmax)/cavx
            yscale = (cany-y_current)*(ymax)/cany
            #gets current node colours
            outline = nx.get_node_attributes(self.graphcopy, 'color')
            for n_ind in range(globals.node_df.shape[0]):
                if ((globals.node_df.iloc[n_ind].x_lower < xscale < globals.node_df.iloc[n_ind].x_upper) and
                        (globals.node_df.iloc[n_ind].y_lower < yscale < globals.node_df.iloc[n_ind].y_upper)):
                    node_inside = globals.node_df.iloc[n_ind].name
                    nx.set_node_attributes(self.graphcopy, outline, 'color')
        return node_inside

    def resid_node_click(self, event):
        '''Gets node that you're clicking on and sets it as the right colour depending on if it's residual or intrusive'''
        startpage = self.controller.get_page('StartPage')
        startpage.update_idletasks()
        self.cursorx2 = int(self.graphcanvas.winfo_pointerx() - self.graphcanvas.winfo_rootx())
        self.cursory2 = int(self.graphcanvas.winfo_pointery() - self.graphcanvas.winfo_rooty())
        x_scal = self.cursorx2 + self.transx2
        y_scal = self.cursory2 + self.transy2
        node = self.nodecheck(x_scal, y_scal)
        outline = nx.get_node_attributes(self.graphcopy, 'color')
        #changes colour of the node outline to represent: intrustive (green), residual (orange) or none (black)
        if (node in self.resid_list) and (self.modevariable != 'intru'):
            self.resid_list.remove(node)
            outline[node] = 'black'
        elif (node in self.resid_list) and (self.modevariable == 'intru'):
            self.resid_list.remove(node)
            outline[node] = 'green'
            self.intru_list.append(node)
        elif (node in self.intru_list) and (self.modevariable != 'resid'):
            self.intru_list.remove(node)
            outline[node] = 'black'
        elif (node in self.intru_list) and (self.modevariable == 'resid'):
            self.intru_list.remove(node)
            self.resid_list.append(node)
            outline[node] = 'orange'
        elif (self.modevariable == 'resid') and (node not in self.resid_list):
            self.resid_list.append(node)
            outline[node] = 'orange'
        elif self.modevariable == 'intru'and (node not in self.intru_list):
            self.intru_list.append(node)
            outline[node] = 'green'
        self.resid_label = ttk.Label(self.residcanvas, text=str(self.resid_list).replace("'", "")[1:-1])
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.intru_label = ttk.Label(self.intrucanvas, text=str(self.intru_list).replace("'", "")[1:-1])
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        #adds scrollbars to the canvas
        scroll_bar1 = ttk.Scrollbar(self.residcanvas)
        scroll_bar1.pack(side=tk.RIGHT)
        scroll_bar2 = ttk.Scrollbar(self.intrucanvas)
        scroll_bar2.pack(side=tk.RIGHT)
        #updates the node outline colour
        nx.set_node_attributes(self.graphcopy, outline, 'color')
        if globals.phase_true == 1:
            imgrender_phase(self.graphcopy)
        else:
            imgrender(self.graphcopy, self.graphcanvas.winfo_width(), self.graphcanvas.winfo_height())
        #rerends the image of the strat DAG with right colours
        self.image = Image.open('fi_new.png')
        self.width2, self.height2 = self.image.size
        self.container = self.graphcanvas.create_rectangle(0, 0, self.width2, self.height2, width=0)
        self.show_image2()
        return node

# Global scoping of MAIN_FRAME is currently required for state saving behaviour, prior to refactoring.
MAIN_FRAME = MainFrame()

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
    print(f"PolyChron {version('polychron')}")

def main():
    """Main method as the entry point for launching the GUI
    """
    args = parse_cli()
    if args.version:
        print_version()
    else:
        MAIN_FRAME.mainloop() 
