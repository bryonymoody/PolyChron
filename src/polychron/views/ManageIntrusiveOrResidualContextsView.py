import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

from .BasePopupView import BasePopupView


class ManageIntrusiveOrResidualContextsView(BasePopupView):
    """View for managing intrusive and residual contexts

    Formerly `popupWindow4`. This is a popup window triggered after ResidualOrIntrusive input
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        self.__intru_dropdown_labels = {}
        """Dict of tkinter label widgets for intrusive nodes"""

        self.__intru_dropdowns = {}
        """Dict of dropdown tkinter widgets for intrusive nodes"""

        self.__resid_dropdown_labels = {}
        """Dict of tkinter label widgets for residual nodes"""

        self.__resid_dropdowns = {}
        """Dict of dropdown tkinter widgets for residual nodes"""

        # @todo cleaner popup separation?
        self.configure(bg="#AEC7D6")
        self.geometry("1000x400")
        self.title("Managing intrusive and residual contexts")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        self.back_button = tk.Button(self, text="Go back", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.back_button.grid(column=30, row=4)
        self.proceed_button = tk.Button(
            self,
            text="Proceed to render chronological graph",
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.proceed_button.grid(column=30, row=6)

    def bind_back_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the back_button is pressed"""
        if callback is not None:
            self.back_button.config(command=callback)

    def bind_proceed_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the proceed_button is pressed"""
        if callback is not None:
            self.proceed_button.config(command=callback)

    def create_dropdowns(self, resid_list: List[str], intru_list: List[str]) -> None:
        """Sets up drop down menus for defining what to do with residual or intrusive contexts

        Formerly popupWindow4.test
        """

        # Reset class the lists of ttk elements
        # @todo - Explicitly delete drop down elements if any exist already?
        self.__resid_dropdown_labels = {}
        self.__resid_dropdowns = {}
        self.__intru_dropdown_labels = {}
        self.__intru_dropdowns = {}

        # Create a label and combobox for each residual node provided
        for idx, node in enumerate(resid_list):
            # Add a label
            self.__resid_dropdown_labels[node] = ttk.Label(self, text=str(node))
            self.__resid_dropdown_labels[node].grid(column=0, row=idx, padx=30, pady=25)
            # Adding combobox drop down list
            self.__resid_dropdowns[node] = ttk.Combobox(self, width=27, state="readonly")
            self.__resid_dropdowns[node]["values"] = ("Exclude from modelling", "Treat as TPQ")
            self.__resid_dropdowns[node]["background"] = "#ff0000"
            self.__resid_dropdowns[node].grid(column=1, row=idx)

        # Create a label and combobox for each intrusive node provided
        for idx, node in enumerate(intru_list):
            self.__intru_dropdown_labels[node] = ttk.Label(self, text=str(node))
            self.__intru_dropdown_labels[node].grid(column=21, row=idx, padx=30, pady=25)
            # Adding combobox drop down list
            self.__intru_dropdowns[node] = ttk.Combobox(self, width=27, state="readonly")
            self.__intru_dropdowns[node]["values"] = ("Exclude from modelling", "Treat as TAQ")
            self.__intru_dropdowns[node].current(0)
            self.__intru_dropdowns[node].grid(column=22, row=idx)

    def get_resid_dropdown_selections(self) -> Dict[str, str]:
        """Get the selected values for each residual dropdown in a dictionary"""
        return {node: combobox.get() for node, combobox in self.__resid_dropdowns.items()}

    def get_intru_dropdown_selections(self) -> Dict[str, str]:
        """Get the selected values for each intrusive dropdown in a dictionary"""
        return {node: combobox.get() for node, combobox in self.__intru_dropdowns.items()}
