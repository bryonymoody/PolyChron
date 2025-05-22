import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional

from .PopupView import PopupView


class AddContextView(PopupView):
    """View for adding an additional context to the current model

    Takes a single context label as user input to add to the model

    Formerly `popupWindow`
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # @todo cleaner popup separation?
        self.configure(bg="#AEC7D6")
        self.geometry("1000x400")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        # Label
        self.label = ttk.Label(self, text="Context Number")
        self.label.pack()

        # User input
        self.entry = ttk.Entry(self)
        self.entry.pack()

        # Button
        self.ok_button = ttk.Button(self, text="Ok")  # gets ridof the popup
        self.ok_button.pack()

        # @todo - cancel button?

    def bind_ok_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)

    def get_input(self) -> str:
        return self.entry.get()
