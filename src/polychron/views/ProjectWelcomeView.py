from __future__ import annotations

import importlib.resources
import io
import tkinter as tk
from typing import Any, Callable

import ttkbootstrap as ttk
from PIL import Image, ImageTk

from ..GUIThemeManager import GUIThemeManager
from .FrameView import FrameView


class ProjectWelcomeView(FrameView):
    """View for the welcome screen when polychron is first opened.

    This is implemented as a passive view, i.e. UI elements have no callbacks at constrution, and they must be explcitly bound afterwards
    """

    def __init__(self, parent: tk.Frame, theme_manager: GUIThemeManager) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent, theme_manager)

        # Set this element's background to white
        self.config(background="white")

        # Load the image from the package resources, and add it to the current frame
        package_name = __name__.split(".")[0]
        image1 = None
        with importlib.resources.files(package_name).joinpath("resources/logo.png").open("rb") as f:
            image1 = Image.open(io.BytesIO(f.read()))
        # Convert the image which has been read from disk into an ImageTK, as a class memebr to avoid it going out of scope
        self.logo_image = ImageTk.PhotoImage(image1.resize((360, 70)))
        # Add the logo to a tk label within the main canvas
        self.logo_label = ttk.Label(self, image=self.logo_image)  # , background="white")
        self.logo_label.place(relx=0.2, rely=0.2, relheight=0.2, relwidth=0.4)

        # Add some greeting text to the main canvas
        self.greeting = ttk.Label(
            self,
            text="Welcome to PolyChron, how would you like to proceed?",
            # bg="white",
            # fg=GUIThemeManager.colour("slate_grey"),
            anchor="w",
        )
        self.greeting.place(relx=0.22, rely=0.45)

        # Add the back button with no command set
        self.load_button = ttk.Button(
            self,
            text="Load existing project",
            # bg=GUIThemeManager.colour("slate_grey"),
            # fg=GUIThemeManager.colour("offwhite2"),
        )
        self.load_button.place(relx=0.8, rely=0.9)
        self.load_button.bind("<Return>", lambda event: self.load_button.invoke())

        # Add the create button with no command set
        self.create_button = ttk.Button(
            self,
            text="Create new project",
            # bg=GUIThemeManager.colour("offwhite2"),
            # fg=GUIThemeManager.colour("slate_grey"),
        )
        self.create_button.place(relx=0.62, rely=0.9)
        self.create_button.bind("<Return>", lambda event: self.create_button.invoke())

    def bind_load_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the load_button is pressed"""
        if callback is not None:
            self.load_button.config(command=callback)

    def bind_create_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the create_button is pressed"""
        if callback is not None:
            self.create_button.config(command=callback)
