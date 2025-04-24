import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional

from .BaseFrameView import BaseFrameView


class ProjectSelectView(BaseFrameView):
    """Passive view for project loading/selection"""

    def __init__(self, parent: tk.Frame):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)
        self.parent = parent

        # Set this element's background to white @todo use a theme?
        self.config(background="white")

        self.list_label = tk.Label(self, text="Select project", bg="white", font=("helvetica 14 bold"), fg="#2F4858")
        self.list_label.place(relx=0.36, rely=0.1)

        self.mylist_var = tk.StringVar()  # @todo value = myList)
        self.MyListBox = tk.Listbox(
            self,
            listvariable=self.mylist_var,
            bg="#eff3f6",
            font=("Helvetica 11 bold"),
            fg="#2F4858",
            selectmode="browse",
        )
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.MyListBox.yview)
        self.MyListBox["yscrollcommand"] = scrollbar.set
        self.MyListBox.place(relx=0.36, rely=0.17, relheight=0.4, relwidth=0.28)
        # self.MyListBox.bind('<<ListboxSelect>>', self.items_selected) # @todo

        self.load_button = tk.Button(self, text="Load project", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.load_button.place(relx=0.8, rely=0.9, relwidth=0.19)
        # self.top.bind('<Return>', (lambda event: self.load_model(proj_dir))) # @todo
        self.back_button = tk.Button(self, text="Back", bg="#eff3f6", font=("Helvetica 12 bold"), fg="#2F4858")
        self.back_button.place(relx=0.21, rely=0.01)

    def bind_load_button(self, callback: Callable[[], Optional[Any]]) -> None:
        if callback is not None:
            self.load_button.config(command=callback)

    def bind_back_button(self, callback: Callable[[], Optional[Any]]) -> None:
        if callback is not None:
            self.back_button.config(command=callback)
