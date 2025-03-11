import tkinter as tk
from tkinter import ttk

from .popupWindow3 import popupWindow3


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
