import tkinter as tk
from tkinter import ttk

from .PopupView import PopupView


class MCMCProgressView(PopupView):
    """View for displaying MCMC calibratrion progress

    Formely within `StartPage::load_mcmc`, triggered by tools > calibrate model
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        self.geometry("700x200")
        self.title("MCMC in progress")
        self.attributes("-topmost", "true")

        self.backcanvas = tk.Canvas(self, bg="#AEC7D6")
        self.backcanvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.title_label = tk.Label(
            self.backcanvas, text="MCMC in progress", font=("helvetica 14 bold"), fg="#2F4858", bg="#AEC7D6"
        )
        self.title_label.place(relx=0.35, rely=0.26)
        self.output_label = tk.Label(self.backcanvas, font=("helvetica 14 bold"), fg="#2F4858", bg="#AEC7D6")
        self.output_label.place(relx=0.4, rely=0.4)
        self.progress_bar = ttk.Progressbar(self.backcanvas, orient=tk.HORIZONTAL, length=400, mode="indeterminate")
        self.progress_bar.place(relx=0.2, rely=0.56)

    def update_progress(self, percent: int) -> None:
        """Update the progress bar and text label with current progress

        Parameters:
            percent (int): MCMC calibration progress as an integer percentage in the inclusive range [0, 100]
        """
        self.output_label["text"] = f"{percent}% complete"
        self.progress_bar["value"] = percent
