import tkinter as tk
from typing import Any, Callable, List, Optional

from .BasePopupView import BasePopupView


class CalibrateModelSelectView(BasePopupView):
    """View for selecting which models to calibrate, when multiple models are to be calibrated at once

    Formerly `popupWindow8`, used from menu option "Calibrate multiple projects from project"
    """

    def __init__(self, parent: tk.Frame):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # @todo cleaner popup separation?
        self.configure(bg="white")
        self.title("Model calibration")
        self.geometry("1000x400")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        # Add instruction text
        self.label = tk.Label(
            self, text="Which model/s would you like calibrate?", bg="white", font="helvetica 12", fg="#2f4858"
        )
        self.label.place(relx=0.3, rely=0.1)

        # Add an (emtpy) list for selections to be made from.
        self.list_box = tk.Listbox(self, font="helvetica 12", fg="#2f4858", selectmode="multiple")
        self.list_box.place(relx=0.3, rely=0.2, relheight=0.5, relwidth=0.5)

        # Add an OK button
        self.ok_button = tk.Button(self, text="OK", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.ok_button.place(relx=0.3, rely=0.7)

        # Add a button for selecting all possible models
        self.select_all_button = tk.Button(
            self, text="Select all", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.select_all_button.place(relx=0.6, rely=0.7)

    def bind_ok_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)

    def bind_select_all_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the select_all_button is pressed"""
        if callback is not None:
            self.select_all_button.config(command=callback)

    def update_model_list(self, model_list: List[str]) -> None:
        """Update the list box with the names of models from the current project which are ready for calibration."""
        for model_name in model_list:
            self.list_box.insert("end", model_name)

    def select_all_models(self) -> None:
        """select all models within the UI"""
        self.list_box.select_set(0, "end")

    def get_selected_models(self) -> List[str]:
        """Get a list of selected model names from the listbox"""
        return [self.list_box.get(i) for i in self.list_box.curselection()]
