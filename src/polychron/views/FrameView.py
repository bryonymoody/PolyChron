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
