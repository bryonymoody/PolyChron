import tkinter as tk
from tkinter import ttk


class ModelView(ttk.Frame):
    """Main view for displaying information about the model.
    I.e. the "Stratigraphy and supplementary data" tab

    Formely part of `StartPage`

    @todo - consider splitting each canvas to it's own separate classes?
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root
