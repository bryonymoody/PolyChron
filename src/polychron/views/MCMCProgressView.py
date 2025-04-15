import tkinter as tk
from tkinter import ttk


class MCMCProgressView(ttk.Frame):
    """View for displaying MCMC calibratrion progress

    Formely within `StartPage::load_mcmc`, triggered by tools > calibrate model
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root

        # @todo cleaner popup separation?
        self.top = tk.Toplevel(root)
        self.backcanvas = tk.Canvas(self.top, bg="#AEC7D6")
        self.backcanvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.top.geometry("%dx%d%+d%+d" % (700, 200, 600, 400))
        self.top.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        self.title_label = tk.Label(
            self.backcanvas, text="MCMC in progress", font=("helvetica 14 bold"), fg="#2F4858", bg="#AEC7D6"
        )
        self.title_label.place(relx=0.35, rely=0.26)
        self.output_label = tk.Label(self.backcanvas, font=("helvetica 14 bold"), fg="#2F4858", bg="#AEC7D6")
        self.output_label.place(relx=0.4, rely=0.4)
        self.progress_bar = ttk.Progressbar(self.backcanvas, orient=tk.HORIZONTAL, length=400, mode="indeterminate")
        self.progress_bar.place(relx=0.2, rely=0.56)

    def update_progress(self, percent: int):
        # @todo - assert integer is between 0 and 100 inclusive
        # @todo - should this be split into 2 methods which just sets a passed in string and integer separately from the appropriate presenter, to make this view more passive (i.e. move as much testing as possible out of the view?
        self.output_label["text"] = f"{percent}% complete"
        self.progress_bar["value"] = percent
