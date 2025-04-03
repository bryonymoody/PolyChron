import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional


class ProjectSelectView(ttk.Frame):
    """Passive view for project loading/selection"""

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root

        # Declare 2 canvas, splitting the UI into 2 columns
        # @todo - self.top? i.e. a special top window? Maybe shoudl just be passed in as a diff root?
        # @todo - should this be moved somewhere else, which views which use these then extend to avoid duplication?
        self.maincanvas = tk.Canvas(self.root, bg="white")
        self.maincanvas.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.canvas = tk.Canvas(self.root, bg="#AEC7D6")
        self.canvas.place(relx=0, rely=0, relheight=1, relwidth=0.2)

        self.list_label = tk.Label(
            self.maincanvas, text="Select project", bg="white", font=("helvetica 14 bold"), fg="#2F4858"
        )
        self.list_label.place(relx=0.36, rely=0.1)

        self.mylist_var = tk.StringVar()  # @todo value = myList)
        self.MyListBox = tk.Listbox(
            self.maincanvas,
            listvariable=self.mylist_var,
            bg="#eff3f6",
            font=("Helvetica 11 bold"),
            fg="#2F4858",
            selectmode="browse",
        )
        scrollbar = ttk.Scrollbar(self.maincanvas, orient="vertical", command=self.MyListBox.yview)
        self.MyListBox["yscrollcommand"] = scrollbar.set
        self.MyListBox.place(relx=0.36, rely=0.17, relheight=0.4, relwidth=0.28)
        # self.MyListBox.bind('<<ListboxSelect>>', self.items_selected) # @todo

        self.load_button = tk.Button(
            self.maincanvas, text="Load project", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.load_button.place(relx=0.8, rely=0.9, relwidth=0.19)
        # self.top.bind('<Return>', (lambda event: self.load_model(proj_dir))) # @todo
        self.back_button = tk.Button(
            self.maincanvas, text="Back", bg="#eff3f6", font=("Helvetica 12 bold"), fg="#2F4858"
        )
        self.back_button.place(relx=0.21, rely=0.01)

    def bind_load_button(self, callback: Callable[[], Optional[Any]]) -> None:
        if callback is not None:
            self.load_button.config(command=callback)

    def bind_back_button(self, callback: Callable[[], Optional[Any]]) -> None:
        if callback is not None:
            self.back_button.config(command=callback)
