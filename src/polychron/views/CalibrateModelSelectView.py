import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional


class CalibrateModelSelectView(ttk.Frame):
    """View for selecting which models to calibrate, when multiple models are to be calibrated at once

    Formerly `popupWindow8`, used from menu option "Calibrate multiple projects from project"
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root

        # @todo cleaner popup separation?
        self.top=tk.Toplevel(root)
        self.top.configure(bg ='white')
        self.top.title("Model calibration")
        self.top.geometry("1000x400")
        self.top.attributes('-topmost', 'true')  # @todo maybe remove. # Forces the top level to always be on top. 

        # @todo - implement loading / data population in the presenter / model
        # self.path = path
        # model_list_prev = [d for d in os.listdir(path) if os.path.isdir(path + '/' + d)]
        # model_list = []
        # for i in model_list_prev:
        #     mod_path = str(path) + "/" + str(i) + "/python_only/save.pickle"
        #     with open(mod_path, "rb") as f:
        #         data = pickle.load(f)
        #         load_check = data['load_check']
        #     if load_check == "loaded":
        #         model_list.append(i)

        self.label=tk.Label(self.top,text="Which model/s would you like calibrate?", bg ='white', font='helvetica 12', fg = '#2f4858')
        self.label.place(relx = 0.3, rely = 0.1)
        self.list_box=tk.Listbox(self.top, font='helvetica 12', fg = '#2f4858', selectmode='multiple')
        self.list_box.place(relx = 0.3, rely = 0.2, relheight= 0.5, relwidth = 0.5)
        # self.list_box.bind('<<ListboxSelect>>',tk.CurSelet)
        # @todo provide method to populate list with data
        # for items in model_list:
        #     self.list_box.insert('end',items)
        self.ok_button=tk.Button(self.top,text='OK', bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6')
        self.ok_button.place(relx = 0.3, rely = 0.7)
        self.select_all_button=tk.Button(self.top,text='Select all',  bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6')
        self.select_all_button.place(relx = 0.6, rely = 0.7)

    def bind_load_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the load_button is pressed"""
        if callback is not None:
            self.load_button.config(command=callback)

    def bind_select_all_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the select_all_button is pressed"""
        if callback is not None:
            self.select_all_button.config(command=callback)
