from __future__ import annotations

import tkinter as tk
from tkinter import messagebox as messagebox
from typing import Any, Dict


class FrameView(tk.Frame):
    """Base class for Views which are frames rather than windows"""

    def __init__(self, parent: tk.Frame) -> None:
        """Call the base class (Frame) constructor"""
        # Call the tk.Frame's constructor providing the parent/master element
        super().__init__(parent)

        self.parent = parent
        """A reference to the parent frame"""

        self.__grid_initialised: bool = False
        """Flag indicating if place_in_container has been called"""

    def place_in_container(self) -> None:
        """Initial placement of the FrameView inside the containing element using grid, before immediately hiding"""
        # Place in the parent grid
        self.grid(row=0, column=0, sticky="nsew")
        # Immediately hide the frame, but remembering placement
        self.grid_remove()
        self.__grid_initialised = True

    def visible_in_container(self) -> None:
        """Make the frame visible within the parent container (if it has one)"""
        # If the frame has been placed via grid already, ensure it is on top of the grid and has focus
        if self.__grid_initialised:
            # Re-place in the grid using saved placement
            self.grid()
            # Give it focus for any keybind events
            self.focus_set()

    def not_visible_in_container(self) -> None:
        """Make this FrameView not the "current" frame within a frame view with containers, via grid_remove"""
        if self.__grid_initialised:
            # Remove from the grid, but remembering placement within the container
            self.grid_remove()

    def messagebox_info(self, title: str | None = None, message: str | None = None, **options: Dict[str, Any]) -> None:
        """Show an info message box with the provided type and message, and automatic parent setting:

        Parameters:
            title: The message box title
            message: The info message
            **options: other arguments forwarded to `tkinter.messagebox.showinfo`, excluding `parent`"""
        # Prevent parents being passed as a kwarg
        options.pop("parent", None)
        # Launch the tkinter messagebox
        messagebox.showinfo(title=title, message=message, parent=self.parent, **options)

    def messagebox_warning(
        self, title: str | None = None, message: str | None = None, **options: Dict[str, Any]
    ) -> None:
        """Show an warning message box with the provided type and message, and automatic parent setting:

        Parameters:
            title: The message box title
            message: The warning message
            **options: other arguments forwarded to `tkinter.messagebox.showwarning`, excluding `parent`"""
        # Prevent parents being passed as a kwarg
        options.pop("parent", None)
        # Launch the tkinter messagebox
        messagebox.showwarning(title=title, message=message, parent=self.parent, **options)

    def messagebox_error(self, title: str | None = None, message: str | None = None, **options: Dict[str, Any]) -> None:
        """Show an error message box with the provided type and message, and automatic parent setting:

        Parameters:
            title: The message box title
            message: The error message
            **options: other arguments forwarded to `tkinter.messagebox.showerror`, excluding `parent`"""
        # Prevent parents being passed as a kwarg
        options.pop("parent", None)
        # Launch the tkinter messagebox
        messagebox.showerror(title=title, message=message, parent=self.parent, **options)
