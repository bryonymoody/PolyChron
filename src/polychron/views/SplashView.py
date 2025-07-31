from __future__ import annotations

import importlib.resources
import io
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, List, Tuple

from PIL import Image, ImageTk

from .FrameView import FrameView


class SplashView(FrameView):
    """View for the splash screen main window view.

    This is displayed in the main window before a project is opened, and just allows users to re-open the new/load project popup in case they close it without loading anything.

    This is implemented as a passive view, i.e. UI elements have no callbacks at constrution, and they must be explcitly bound afterwards
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        self.configure(background="white")

        # Use a canvas to add a background colour below the menu bar
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg="white")
        self.canvas.place(relx=0, rely=0.03, relwidth=1, relheight=0.97)

        # Add the file menu button
        self.file_menubar = ttk.Menubutton(self, text="File", state=tk.DISABLED)
        self.file_menubar["menu"] = tk.Menu(self.file_menubar, tearoff=0, bg="#fcfdfd", font=("helvetica", 11))
        self.file_menubar.place(relx=0.0, rely=0, relwidth=0.1, relheight=0.03)

        # Adding View menu button
        self.view_menubar = ttk.Menubutton(self, text="View", state=tk.DISABLED)
        self.view_menubar["menu"] = tk.Menu(self.view_menubar, tearoff=0, bg="#fcfdfd", font=("helvetica", 11))
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)

        # Adding Tools menu button
        self.tool_menubar = ttk.Menubutton(self, text="Tools", state=tk.DISABLED)
        self.tool_menubar["menu"] = tk.Menu(self.tool_menubar, tearoff=0, bg="#fcfdfd", font=("helvetica", 11))
        self.tool_menubar.place(relx=0.15, rely=0, relwidth=0.1, relheight=0.03)

        # Load the image from the package resources, and add it to the current frame
        package_name = __name__.split(".")[0]
        self.original_logo_image = None
        with importlib.resources.files(package_name).joinpath("resources/logo.png").open("rb") as f:
            self.original_logo_image = Image.open(io.BytesIO(f.read()))
        # Create a copy of the image which will be resized if needed
        self.logo_image = self.original_logo_image.copy()

        # Convert the image which has been read from disk into an ImageTK, as a class member to avoid it going out of scope
        self.logo_image_tk = ImageTk.PhotoImage(self.original_logo_image)

        # Because the frame & parent frame have not yet been packed in the parent, the width and height have not yet been computed correctly for self or self.frame.
        # Instead, use the parent's width / height, and scale the window height as the canvas is 97% tall
        self.update()  # required for window height to be correct.
        canvas_center_x = self.parent.winfo_width() / 2
        canvas_center_y = (0.97 * self.parent.winfo_height()) / 2
        self.canvas_img_id = self.canvas.create_image(
            canvas_center_x, canvas_center_y, image=self.logo_image_tk, anchor=tk.CENTER
        )
        # When the window is resized, ensure the image is still centered within the window
        self.canvas.bind("<Configure>", lambda event: self.recentre_image(event))

    def recentre_image(self, event) -> None:
        """Callback for when the window is resized to re-size and re-center the image"""

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width == 0 or canvas_height == 0:
            return

        # Calculate if the image needs to be scaled or not, if the canvas is smaller than the source image
        original_width, original_height = self.original_logo_image.size
        width_sf = canvas_width / original_width
        height_sf = canvas_width / original_height
        scale_factor = min(1.0, width_sf, height_sf)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        # If the size doesn't match, change it.
        if new_width != self.logo_image.width or new_height != self.logo_image.height:
            self.logo_image = self.original_logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_image_tk = ImageTk.PhotoImage(self.logo_image)
            self.canvas.itemconfig(self.canvas_img_id, image=self.logo_image_tk)

        # Place in the new centre
        canvas_center_x = canvas_width / 2
        canvas_center_y = canvas_height / 2
        self.canvas.coords(self.canvas_img_id, canvas_center_x, canvas_center_y)

    def build_file_menu(self, items: List[Tuple[str, Callable[[], Any]] | None]) -> None:
        """Builds the 'file' menu element with labels and callback functions.

        Parameters:
            items: A List of menu entries to add, which may be None to identify a separator, or a tuple containing a label anf callback fucntion.
        """
        # Get a handle to the Menu belonging to the MenuButton
        menubar: ttk.Menubutton = self.file_menubar
        menu: tk.Menu = self.nametowidget(menubar.cget("menu"))
        # Clear existing items
        menu.delete(0, "end")
        # Iterate the items to add to the menu
        for item in items:
            if item is not None:
                # If the item is not None, it should be a Tuple contianing a string label and a callback function
                label, callback = item
                menu.add_command(font="helvetica 12 bold", label=label, command=callback)
            else:
                # Add a separator if the item is None
                menu.add_separator()
        # Mark the menubutton as not disabled
        if len(items) > 0:
            menubar.configure(state=tk.NORMAL)
