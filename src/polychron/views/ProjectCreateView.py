from __future__ import annotations

import tkinter as tk
from typing import Any, Callable

from ..GUIThemeManager import GUIThemeManager
from .FrameView import FrameView


class ProjectCreateView(FrameView):
    """Passive view for project creation"""

    def __init__(self, parent: tk.Frame, theme_manager: GUIThemeManager) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent, theme_manager)

        # Set this element's background to white
        self.config(background="white")

        # Add a text label
        self.text_1 = tk.Label(
            self,
            text="Input project name:",
            bg="white",
            font=self.theme_manager.font(14, "bold"),
            fg=GUIThemeManager.colour("slate_grey"),
        )
        self.text_1.place(relx=0.4, rely=0.2)

        # Add an text input element
        self.user_input = tk.Entry(self)
        self.user_input.place(relx=0.35, rely=0.4, relwidth=0.3, relheight=0.08)

        # Add a submit button
        self.submit_button = tk.Button(
            self, text="Submit ", bg=GUIThemeManager.colour("submit_orange"), fg=GUIThemeManager.colour("slate_grey")
        )
        self.submit_button.place(relx=0.66, rely=0.4)
        self.submit_button.bind("<Return>", lambda event: self.submit_button.invoke())

        # Add a back button
        self.back_button = tk.Button(
            self, text="Back", bg=GUIThemeManager.colour("back_white"), fg=GUIThemeManager.colour("slate_grey")
        )
        self.back_button.place(relx=0.21, rely=0.01)
        self.back_button.bind("<Return>", lambda event: self.back_button.invoke())

    def bind_submit_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the submit_button is pressed, or when the enter button is pressed."""
        if callback is not None:
            self.submit_button.config(command=callback)
            self.user_input.bind("<Return>", (lambda event: callback()))

    def bind_back_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the back_button is pressed"""
        if callback is not None:
            self.back_button.config(command=callback)

    def get_name(self) -> str:
        """Get the user-provided name of the project"""
        return self.user_input.get()
