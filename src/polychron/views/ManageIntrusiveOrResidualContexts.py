import tkinter as tk
from typing import Any, Callable, Optional

from .BasePopupView import BasePopupView


class ManageIntrusiveOrResidualContexts(BasePopupView):
    """View for managing intrusive and residual contexts

    Formerly `popupWindow4`. This is a popup window triggered after ResidualOrIntrusive input
    """

    def __init__(self, parent: tk.Tk, start_visible=False):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent, start_visible)

        # @todo cleaner popup separation?
        self.configure(bg="#AEC7D6")
        self.geometry("1000x400")
        self.title("Managing intrusive and residual contexts")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        # self.node_del_tracker = node_track
        # self.controller = controller
        # self.resid_list = resid_list
        # self.intru_list = intru_list
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
        # self.test(resid_list, intru_list)
        # controller.wait_window(self)

    def bind_back_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the back_button is pressed"""
        if callback is not None:
            self.back_button.config(command=callback)

    def bind_proceed_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the proceed_button is pressed"""
        if callback is not None:
            self.proceed_button.config(command=callback)
