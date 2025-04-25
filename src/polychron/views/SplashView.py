import importlib.resources
import io
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional

from PIL import Image, ImageTk

from .BaseFrameView import BaseFrameView


class SplashView(BaseFrameView):
    """View for the splash screen main window view.

    This is displayed in the main window before a project is opened, and just allows users to re-open the new/load project popup in case they close it without loading anything.

    This is implemented as a passive view, i.e. UI elements have no callbacks at constrution, and they must be explcitly bound afterwards
    """

    def __init__(self, parent: tk.Frame):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        self.configure(background="white")

        # Use a canvas to add a background colour below the menu bar
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, bg="white")
        self.canvas.place(relx=0, rely=0.03, relwidth=1, relheight=0.97)

        # Adding File Menu and commands
        # @todo - (partially) abstract this away to avoid duplication
        self.file_menubar = ttk.Menubutton(self, text="File")
        file = tk.Menu(self.file_menubar, tearoff=0, bg="white", font=("helvetica 12 bold"))
        self.file_menubar["menu"] = file
        file.add_separator()
        file.add_command(label="Select Project", font="helvetica 12 bold")
        self.file_menubar.place(relx=0.00, rely=0, relwidth=0.1, relheight=0.03)

        # Add an empty (and disabled) view menubar for consistency with other tabs
        self.view_menubar = ttk.Menubutton(self, text="View", state=tk.DISABLED)
        self.view_menubar.place(relx=0.07, rely=0, relwidth=0.1, relheight=0.03)

        # Add an empty (and disabled) tools menubar for consistency with other tabs
        self.tool_menubar = ttk.Menubutton(self, text="Tools", state=tk.DISABLED)
        self.tool_menubar.place(relx=0.15, rely=0, relwidth=0.1, relheight=0.03)

        # Load the image from the package resources, and add it to the current frame
        package_name = __name__.split(".")[0]
        image1 = None
        with importlib.resources.files(package_name).joinpath("resources/logo.png").open("rb") as f:
            image1 = Image.open(io.BytesIO(f.read()))
        # Convert the image which has been read from disk into an ImageTK, as a class memebr to avoid it going out of scope
        self.logo_image = ImageTk.PhotoImage(image1)

        # Because the frame & parent frame have not yet been packed in the parent, the width and height have not yet been computed correctly for self or self.frame.
        # Instead, use the parent's width / height, and scale the window height as the canvas is 97% tall
        self.update()  # required for window height to be correct.
        canvas_center_x = self.parent.winfo_width() / 2
        canvas_center_y = (0.97 * self.parent.winfo_height()) / 2
        self.canvas_img_id = self.canvas.create_image(
            canvas_center_x, canvas_center_y, image=self.logo_image, anchor=tk.CENTER
        )
        # When the window is resized, ensure the image is still centered within the window
        self.canvas.bind("<Configure>", lambda event: self.recenter_image(event))

    def recenter_image(self, event) -> None:
        """Callback for when the window is resized to re-center the image

        @todo - resize the image too when the remainign window size is too small.
        """
        canvas_center_x = self.parent.winfo_width() / 2
        canvas_center_y = (0.97 * self.parent.winfo_height()) / 2
        self.canvas.coords(self.canvas_img_id, canvas_center_x, canvas_center_y)

    def bind_menu_callbacks(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the back_button is pressed

        @todo - standardise this with how other menu callbacks are set in ModelView/DatingResultsVeiw. Probably a Dict[str, Callable] usign the menu label? Or just have a member dict of function pointers and directly bind to that for each command on creation.
        """
        if callback is not None:
            file_menu = self.nametowidget(self.file_menubar.cget("menu"))
            file_menu.entryconfig("Select Project", command=callback)
