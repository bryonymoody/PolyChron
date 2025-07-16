from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, List, Tuple

from .PopupView import PopupView


class DatafilePreviewView(PopupView):
    """View for previewing the data in a loaded dataframe (i.e. csv).

    Formerly `popupWindow7`, called by numerous `open_fileX` methods in StartPage
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        self.title("Data preview")
        self.attributes("-topmost", "true")

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack()
        self.l = tk.Label(self.canvas, text="Data Preview")
        self.l.pack()

        self.tree = ttk.Treeview(self.canvas)
        self.tree.pack()
        self.tree["show"] = "headings"
        self.load_button = tk.Button(self, text="Load data", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.load_button.pack()
        self.cancel_button = tk.Button(self, text="Cancel", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.cancel_button.pack()

    def bind_load_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the load_button is pressed"""
        if callback is not None:
            self.load_button.config(command=callback)

    def bind_cancel_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the cancel_button is pressed"""
        if callback is not None:
            self.cancel_button.config(command=callback)

    def set_tree_data(self, cols: List[str], rows: List[Tuple[str, List[str]]]) -> None:
        """Update the data shown in the preview table/tree

        Parameters:
            cols: A list of column titles
            rows: A list of row entries, where each row is a tuple of the the row index and the row data as a list of strings
        """

        # Clear old data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Set new data
        self.tree["columns"] = cols
        for i in cols:
            self.tree.column(i, anchor="w")
            self.tree.heading(i, text=i, anchor="w")
        for index, row in rows:
            self.tree.insert("", "end", text=index, values=row)
