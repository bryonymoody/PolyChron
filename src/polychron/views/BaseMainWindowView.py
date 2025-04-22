import tkinter as tk


class BaseMainWindowView(tk.Frame):
    """Base class for Views which will be contained within the main window

    @todo - base this on tkk.Frame for better theming, but needs changes to extending classes

    @todo - should this contain a Frame rahter than extend one? I.e. prevent tkinter leaking out of the view

    @todo - make this more complex
    """

    def __init__(self, parent: tk.Frame):
        """Call the base class (Frame) constructor"""
        # Call the tk.Frame's constructor providing the parent/master element
        super().__init__(parent)

        self.parent = parent
        """A reference to the parent frame"""
