from __future__ import annotations

import tkinter as tk
from typing import Any, Callable, Dict


class PopupView(tk.Toplevel):
    """Base class for Views exist within their own popup window"""

    def __init__(self, parent: tk.Toplevel) -> None:
        """Call the base class (Toplevel) constructor"""
        # Call the tk.Toplevel's constructor providing the parent/master element
        super().__init__(parent)

        self.parent = parent
        """A reference to the parent frame"""

        # Ensure the popup window is displayed on top of the parent window
        self.transient(self.parent)
        # Prevent the user from interacting with the parent window while the popup is open
        self.grab_set()

    def register_keybinds(self, bindings: Dict[str, Callable[[], Any]]) -> None:
        """Register window-wide key bindings"""
        for sequence, callback in bindings.items():
            self.bind(sequence, callback)

    def register_protocols(self, bindings: Dict[str, Callable[[], Any]]) -> None:
        """Register protocols with the window

        i.e. what happens when the window is closed using the OS decorations"""
        for name, callback in bindings.items():
            self.protocol(name, callback)

    def centered_geometry(self, width: int, height: int) -> None:
        """Set the popup view's geometry, centred within the parent window

        Parameters:
            width: the width of the popup view
            height: the height of the popup view
        """
        # Set the popup window width and height
        self.geometry(f"{width}x{height}")
        # Get the parent window's dimensions
        parent_width, parent_height = self.parent.winfo_width(), self.parent.winfo_height()
        # Get the parent window's position
        parent_x, parent_y = self.parent.winfo_rootx(), self.parent.winfo_rooty()
        # If the parent width and height were available (not both 1)
        if parent_width != 1 or parent_height != 1:
            # Compute the horizontal and vertical offset for the popup window
            offset_x = parent_x + (parent_width - width) // 2
            offset_y = parent_y + (parent_height - height) // 2
            # Set the popup window offset
            self.geometry(f"+{offset_x}+{offset_y}")
