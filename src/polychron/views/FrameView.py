import tkinter as tk


class FrameView(tk.Frame):
    """Base class for Views which are frames rather than windows"""

    def __init__(self, parent: tk.Frame) -> None:
        """Call the base class (Frame) constructor"""
        # Call the tk.Frame's constructor providing the parent/master element
        super().__init__(parent)

        self.parent = parent
        """A reference to the parent frame"""
