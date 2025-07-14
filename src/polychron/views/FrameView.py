from __future__ import annotations

import tkinter as tk
from tkinter import messagebox as messagebox
from tkinter.filedialog import askopenfile
from typing import IO, Any, Dict, Literal

from ..GUIThemeManager import GUIThemeManager


class FrameView(tk.Frame):
    """Base class for Views which are frames rather than windows"""

    def __init__(self, parent: tk.Frame, theme_manager: GUIThemeManager) -> None:
        """Call the base class (Frame) constructor"""
        # Call the tk.Frame's constructor providing the parent/master element
        super().__init__(parent)

        self.parent = parent
        """A reference to the parent frame"""

        self.theme_manager = theme_manager
        """A reference to the style provider, to access common fonts, colours and theming elements"""

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

    def messagebox_askquestion(
        self,
        title: str | None = None,
        message: str | None = None,
        *args: tuple[Any, ...],
        icon: Literal["error", "info", "question", "warning"] = "question",
        **options: dict[str, Any],
    ) -> str:
        """Ask the user a (yes/no by default) question, with automatic parent setting:

        Parameters:
            title: The message box title
            message: The error message
            args*: Other positional arugments forwarded to the underlyin tkinter call
            icon: The icon to display in the dialog
            **options: other arguments forwarded to `tkinter.messagebox.askquestion`, excluding `parent`

        Returns:
            The selected value from the question box
        """
        # Prevent parents being passed as a kwarg
        options.pop("parent", None)
        # Launch the tkinter messagebox
        return messagebox.askquestion(title, message, *args, icon=icon, parent=self.parent, **options)

    def messagebox_askokcancel(
        self,
        title: str | None = None,
        message: str | None = None,
        *args: tuple[Any, ...],
        icon: Literal["error", "info", "question", "warning"] = "question",
        **options: dict[str, Any],
    ) -> str | None:
        """Ask the user an ok/cancel question, with automatic parent setting:

        Parameters:
            title: The message box title
            message: The error message
            args*: Other positional arugments forwarded to the underlyin tkinter call
            icon: The icon to display in the dialog
            **options: other arguments forwarded to `tkinter.messagebox.askokcancel`, excluding `parent`

        Returns:
            True if OK was selected
        """
        # Prevent parents being passed as a kwarg
        options.pop("parent", None)
        # Launch the tkinter messagebox
        return messagebox.askokcancel(title, message, *args, icon=icon, parent=self.parent, **options)

    def messagebox_askyesno(
        self,
        title: str | None = None,
        message: str | None = None,
        *args: tuple[Any, ...],
        icon: Literal["error", "info", "question", "warning"] = "question",
        **options: dict[str, Any],
    ) -> bool:
        """Ask the user a yes/no question, with automatic parent setting:

        Parameters:
            title: The message box title
            message: The error message
            args*: Other positional arugments forwarded to the underlyin tkinter call
            icon: The icon to display in the dialog
            **options: other arguments forwarded to `tkinter.messagebox.askyesno`, excluding `parent`

        Returns:
            True if yes was selected
        """
        # Prevent parents being passed as a kwarg
        options.pop("parent", None)
        # Launch the tkinter messagebox
        return messagebox.askyesno(title, message, *args, icon=icon, parent=self.parent, **options)

    def messagebox_askyesnocancel(
        self,
        title: str | None = None,
        message: str | None = None,
        *args: tuple[Any, ...],
        icon: Literal["error", "info", "question", "warning"] = "question",
        **options: dict[str, Any],
    ) -> bool | None:
        """Ask the user a yes/no/cancel question, with automatic parent setting:

        Parameters:
            title: The message box title
            message: The error message
            args*: Other positional arugments forwarded to the underlyin tkinter call
            icon: The icon to display in the dialog
            **options: other arguments forwarded to `tkinter.messagebox.askyesnocancel`, excluding `parent`

        Returns:
            True if yes, False if No, None if cancelled
        """
        # Prevent parents being passed as a kwarg
        options.pop("parent", None)
        # Launch the tkinter messagebox
        return messagebox.askyesnocancel(title, message, *args, icon=icon, parent=self.parent, **options)

    def askopenfile(self, mode: str = "r", *args: tuple[Any, ...], **options: dict[str, Any]) -> IO | None:
        """Opens a tkinter file dialogue with the specified mode, forwarding arguments and keyword arugments to the underlying tkinter.filedialog.askopenfile call.

        This abstracts tkinter out of Presenters, simplifying unit testing of non-GUI code.

        Parameters:
            mode: The mode of the file to open
            *args: other positional args, forwarded to askopenfile
            **options: keyword arguments which are forwarded to askopenfile. parent will be overridden to be relative to the FrameView

        Returns:
            The opened file (or None)
        """
        # Prevent parents being passed as a kwarg
        options.pop("parent", None)
        # Launch the tkinter filedialog
        return askopenfile(mode, *args, parent=self.parent, **options)
