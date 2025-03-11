import copy
import tkinter as tk
from tkinter import ttk

import networkx as nx
import numpy as np
import packaging
import pandas as pd
from networkx.drawing.nx_pydot import write_dot

from .util import chrono_edge_add, chrono_edge_remov, node_del_fixed


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
            if phasedict[i] is None:
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

        # networkx.drawing.nx_pydot.write_dot from networkx < 3.4 does not quote node attributes correctly if they contain characters such as :. Networkx 3.4 is only available for pythono >= 3.10, so a workaround is required for python 3.9 users.
        if packaging.version.parse(nx.__version__) < packaging.version.parse("3.4.0"):
            # Remove the contraction attribute from nodes.
            for i in nodes:
                self.graphcopy.nodes[i].pop("contraction", None)

        write_dot(self.graphcopy, "fi_new_chrono")
        self.top.destroy()
