import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional


class DatafilePreviewView(ttk.Frame):
    """View for previewing the data in a loaded dataframe (i.e. csv). 

    Formerly `popupWindow7`, called by numerous `open_fileX` methods in StartPage
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root

        # @todo cleaner popup separation?
        self.top=tk.Toplevel(root)
        # self.top.configure(bg ='white') # @todo popupwindow7 doesn't have a background.
        # self.top.geometry("1000x400") # @todo popupwindow7 doesn't have a fixed geometry defined
        self.top.title("Data preview")
        self.top.attributes('-topmost', 'true')  # @todo maybe remove. # Forces the top level to always be on top. 

        self.canvas = tk.Canvas(self.top, bg = 'white')
        self.canvas.pack()
        self.l=tk.Label(self.canvas, text="Data Preview")
        self.l.pack()
        # cols = list(df.columns) # @todo
        
        tree = ttk.Treeview(self.canvas)
        tree.pack()
        # tree["columns"] = cols
        # for i in cols:
        #     tree.column(i, anchor="w")
        #     tree.heading(i, text=i, anchor='w')
        
        # for index, row in df.iterrows():
        #     tree.insert("",0,text=index,values=list(row))
        tree['show'] = 'headings'
        self.load_button=tk.Button(self.top,text='Load data', bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6')
        self.load_button.pack()
        self.cancel_button=tk.Button(self.top,text='Cancel', bg = '#2F4858', font = ('Helvetica 12 bold'),  fg = '#eff3f6')
        self.cancel_button.pack()
    
    # def cleanup1(self):
    #     self.value= 'load'
    #     self.top.destroy()
    # def cleanup2(self):
    #     self.value='cancel'
    #     self.top.destroy()

    def bind_load_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the load_button is pressed"""
        if callback is not None:
            self.load_button.config(command=callback)

    def bind_cancel_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the cancel_button is pressed"""
        if callback is not None:
            self.cancel_button.config(command=callback)
