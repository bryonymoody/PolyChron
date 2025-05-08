import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional

from .BasePopupView import BasePopupView


class DatafilePreviewView(BasePopupView):
    """View for previewing the data in a loaded dataframe (i.e. csv).

    Formerly `popupWindow7`, called by numerous `open_fileX` methods in StartPage
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # self.configure(bg ='white') # @todo popupwindow7 doesn't have a background.
        # self.geometry("1000x400") # @todo popupwindow7 doesn't have a fixed geometry defined
        self.title("Data preview")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

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

    def bind_load_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the load_button is pressed"""
        if callback is not None:
            self.load_button.config(command=callback)

    def bind_cancel_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the cancel_button is pressed"""
        if callback is not None:
            self.cancel_button.config(command=callback)
