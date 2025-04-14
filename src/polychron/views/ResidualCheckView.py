import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional


class ResidualCheckView(ttk.Frame):
    """View for residual vs inclusive contexts

    Formerly `popupWindow3`

    @todo - implement

    @todo - make this a popup rather than child of root?
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root

        raise Exception("@todo - implement ResidualCheckView/popupWindow3")