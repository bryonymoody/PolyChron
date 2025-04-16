import tkinter as tk
from tkinter import ttk

from .BasePopupView import BasePopupView


class GetSupplementaryDataView(BasePopupView):
    """View for getting supplementary data about a context.

    Not yet implemented, as implementation is marked as BROKEN in 0.1
    """

    def __init__(self, parent: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)
        self.parent = parent

        raise Exception("GetSupplementaryDataView is not fully implemented. popupWindow2 was previously unused.")

        self.title("Adding new supplementary data")
        self.configure(bg="#AEC7D6")
        self.geometry("1000x400")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        # this popup window lets us change the metadata after popupwindow has gone
        # self.graph = graph
        self.canvas2 = tk.Canvas(self)
        self.canvas2.place(relx=0, rely=0, relwidth=1, relheight=1)
        # making node add section
        # defining variables to keep track of what is being updated in the meta data
        self.variable_a = tk.StringVar(self)
        self.variable_b = tk.StringVar(self)
        self.variable_c = tk.StringVar(self)
        self.variable_d = tk.StringVar(self)
        self.label4 = ttk.Label(self.canvas2)
        self.entry4 = ttk.Entry(self.canvas2)
        self.label5 = ttk.Label(self.canvas2)
        self.entry5 = ttk.Entry(self.canvas2)
        self.label6 = ttk.Label(self.canvas2)
        self.entry6 = ttk.Entry(self.canvas2)
        # entry box for adding metadata
        self.entry3 = ttk.Entry(self.canvas2)
        #  self.button3 = ttk.Button(self, text='Add Metadata to node', command=self.testcom())#need to add command
        self.label3 = ttk.Label(self.canvas2, text="Node")
        self.canvas2.create_window(40, 60, window=self.entry3, width=50)
        self.canvas2.create_window(40, 35, window=self.label3)
        # needs way more detail adding to this
        self.dict = {
            "Find Type": ["Find1", "Find2", "Find3"],
            "Determination": ["None", "Input date"],
            "Group": ["None", "Input Group"],
        }
        # defining variables to keep track of what is being updated in the meta data
        self.variable_a = tk.StringVar(self)
        self.variable_b = tk.StringVar(self)
        self.variable_c = tk.StringVar(self)
        self.variable_d = tk.StringVar(self)
        self.optionmenu_a = ttk.OptionMenu(self, self.variable_a, list(self.dict.keys())[0], *self.dict.keys())
        self.optionmenu_b = ttk.OptionMenu(self, self.variable_b, "None", "None")
        self.optionmenu_a.place(relx=0.3, rely=0.15)
        self.optionmenu_b.place(relx=0.6, rely=0.15)
        # self.variable_a.trace('w', self.update_options)
        # self.variable_b.trace('w', self.testdate_input)
        # self.variable_c.trace('w', self.update_options)
        # self.variable_d.trace('w', self.update_options)
        self.variable_a.set("Determination")
        #    self.button3.place(relx=0.1, rely=0.7)
