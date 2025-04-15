import tkinter as tk
from tkinter import ttk


class DatingResultsView(ttk.Frame):
    """View for displaying post-calibration "Dating Results" for a model.

    I.e. the "Dating Results" tab

    Formely part of `PageOne`

    @todo - consider splitting each canvas to it's own separate classes?
    @todo - Split the navbar into it's own class, to reduce duplication with ModelView)
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root
