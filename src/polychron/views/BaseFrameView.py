import tkinter as tk


class BaseFrameView(tk.Frame):
    """Base class for Views which are frames rather than windows

    @todo - base this on tkk.Frame for better theming, but needs changes to extending classes

    @todo - should this contain a Frame rahter than extend one? I.e. prevent tkinter leaking out of the view

    @todo - check waht the type hint for Parent should be. Parent could be a top level, or a tk.Tk or antother frame? Update in child classes. `Misc | None` seems to be used by tk.Frame(master: ) https://github.com/python/typeshed/blob/bc19a28c0dd4876788bd9a5a0deedc20211cd9af/stdlib/tkinter/__init__.pyi#L978
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Call the base class (Frame) constructor"""
        # Call the tk.Frame's constructor providing the parent/master element
        super().__init__(parent)

        self.parent = parent
        """A reference to the parent frame"""
