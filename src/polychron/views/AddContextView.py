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

        self.configure(bg="#AEC7D6")
        self.geometry("1000x400")
        self.attributes("-topmost", "true")

        # Label
        self.label = ttk.Label(self, text="Context Number")
        self.label.pack()

        # User input
        self.entry = ttk.Entry(self)
        self.entry.pack()

        # OK Button
        self.ok_button = ttk.Button(self, text="Ok")
        self.ok_button.pack()

    def bind_ok_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)

    def get_input(self) -> str:
        """Get the string provided by the user

        Returns:
            User provided string
        """
        return self.entry.get()
