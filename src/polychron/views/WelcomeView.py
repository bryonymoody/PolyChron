import importlib.resources
import io
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from typing import Any, Callable, Optional
from .BaseMainWindowView import BaseMainWindowView


class WelcomeView(BaseMainWindowView):
    """View for the welcome screen when polychron is first opened.

    This is implemented as a passive view, i.e. UI elements have no callbacks at constrution, and they must be explcitly bound afterwards
    """

    def __init__(self, parent: tk.Frame):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(parent)
        self.parent = parent

        # Declare 2 canvas, splitting the UI into 2 columns
        # @todo - self.top? i.e. a special top window? Maybe shoudl just be passed in as a diff root?
        # @todo - should this be moved somewhere else, which views which use these then extend to avoid duplication?
        self.maincanvas = tk.Canvas(self, bg="white")
        self.maincanvas.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.canvas = tk.Canvas(self, bg="#AEC7D6")
        self.canvas.place(relx=0, rely=0, relheight=1, relwidth=0.2)

        # Load the image from the package resources, and add it to the current frame
        package_name = __name__.split(".")[0]
        image1 = None
        with importlib.resources.files(package_name).joinpath("resources/logo.png").open("rb") as f:
            image1 = Image.open(io.BytesIO(f.read()))
        # Convert the image which has been read from disk into an ImageTK, as a class memebr to avoid it going out of scope
        self.logo_image = ImageTk.PhotoImage(image1.resize((360, 70)))
        # Add the logo to a tk label within the main canvas
        self.logo_label = tk.Label(self.maincanvas, image=self.logo_image)
        self.logo_label.place(relx=0.2, rely=0.2, relheight=0.2, relwidth=0.4)

        # Add some greeting text to the main canvas
        self.greeting = tk.Label(
            self.maincanvas,
            text="Welcome to PolyChron, how would you like to proceed?",
            bg="white",
            font=("helvetica 12 bold"),
            fg="#2F4858",
            anchor="w",
        )

        # Add the back button with no command set
        self.back_button = tk.Button(
            self.maincanvas, text="Load existing project", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.back_button.place(relx=0.8, rely=0.9)
        # Add the create button with no command set
        self.create_button = tk.Button(
            self.maincanvas, text="Create new project", bg="#eff3f6", font=("Helvetica 12 bold"), fg="#2F4858"
        )
        self.create_button.place(relx=0.62, rely=0.9)

    def bind_back_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the back_button is pressed"""
        if callback is not None:
            self.back_button.config(command=callback)

    def bind_create_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the create_button is pressed"""
        if callback is not None:
            self.create_button.config(command=callback)
