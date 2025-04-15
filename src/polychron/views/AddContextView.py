import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional


class AddContextView(ttk.Frame):
    """View for adding an additional context to the current model

    Takes a single context label as user input to add to the model

    Formerly `popupWindow`
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root

        # @todo cleaner popup separation?
        self.top = tk.Toplevel(root)
        self.top.configure(bg="#AEC7D6")
        self.top.geometry("1000x400")
        self.top.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        # pop up window to allow us to enter a context that we want to change the meta data for
        self.label = ttk.Label(self.top, text="Context Number")
        self.label.pack()
        self.entry = ttk.Entry(self.top)  # allows us to keep t6rack of the number we've entered
        self.entry.pack()
        self.ok_button = ttk.Button(self.top, text="Ok")  # gets ridof the popup
        self.ok_button.pack()
        self.value = tk.StringVar(self.top)

    # @todo
    # def cleanup(self):
    #     '''destroys popupWindow'''
    #     self.value = self.e.get()
    #     self.top.destroy()

    def bind_ok_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)
