import tkinter as tk
from tkinter import ttk

class GetSupplementaryDataView(ttk.Frame):
    """View for getting supplementary data about a context.
    
    Not yet implemented, as implementation is marked as BROKEN in 0.1
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root

        raise Exception("GetSupplementaryDataView is not fully implemented. popupWindow2 was previously unused.")

        # @todo cleaner popup separation?
        self.top = tk.Toplevel(root)
        self.top.title("Adding new supplementary data")
        self.top.configure(bg ='#AEC7D6')
        self.top.geometry("1000x400")
        self.top.attributes('-topmost', 'true')  # @todo maybe remove. # Forces the top level to always be on top. 

        # this popup window lets us change the metadata after popupwindow has gone
        # self.graph = graph
        self.canvas2 = tk.Canvas(self.top)
        self.canvas2.place(relx=0, rely=0, relwidth=1, relheight=1)
        # making node add section
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
        # entry box for adding metadata
        self.entry3 = ttk.Entry(self.canvas2)
        #  self.button3 = ttk.Button(self.top, text='Add Metadata to node', command=self.testcom())#need to add command
        self.label3 = ttk.Label(self.canvas2, text='Node')
        self.canvas2.create_window(40, 60, window=self.entry3, width=50)
        self.canvas2.create_window(40, 35, window=self.label3)
        #needs way more detail adding to this
        self.dict = {'Find Type': ['Find1', 'Find2', 'Find3'],
                     'Determination': ['None', 'Input date'],
                     'Group': ['None', 'Input Group']}
        # defining variables to keep track of what is being updated in the meta data
        self.variable_a = tk.StringVar(self.top)
        self.variable_b = tk.StringVar(self.top)
        self.variable_c = tk.StringVar(self.top)
        self.variable_d = tk.StringVar(self.top)
        self.optionmenu_a = ttk.OptionMenu(self.top, self.variable_a, list(self.dict.keys())[0], *self.dict.keys())
        self.optionmenu_b = ttk.OptionMenu(self.top, self.variable_b, 'None', 'None')
        self.optionmenu_a.place(relx=0.3, rely=0.15)
        self.optionmenu_b.place(relx=0.6, rely=0.15)
        # self.variable_a.trace('w', self.update_options)
        # self.variable_b.trace('w', self.testdate_input)
        # self.variable_c.trace('w', self.update_options)
        # self.variable_d.trace('w', self.update_options)
        self.variable_a.set('Determination')
        #    self.button3.place(relx=0.1, rely=0.7)