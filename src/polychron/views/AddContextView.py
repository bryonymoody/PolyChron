from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

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
        self.centered_geometry(1000, 400)

        # Label
        self.label = ttk.Label(self, text="Context Number")
        self.label.pack()

        # User input
        self.entry = ttk.Entry(self)
        self.entry.pack()

        # OK Button
        self.ok_button = ttk.Button(self, text="Ok")
        self.ok_button.pack()

        # Cancel Button
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_button.pack()

    def bind_ok_button(self, callback: Callable[[], Any | None]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)

    def bind_cancel_button(self, callback: Callable[[], Any | None]) -> None:
        """Bind the callback for when the cancel_button is pressed"""
        if callback is not None:
            self.cancel_button.config(command=callback)

    def get_input(self) -> str:
        """Get the string provided by the user

        Returns:
            User provided string
        """
        return self.entry.get()
