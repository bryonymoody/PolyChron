import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional


class ManageIntrusiveOrResidualContexts(ttk.Frame):
    """View for managing intrusive and residual contexts

    Formerly `popupWindow4`. This is a popup window triggered after ResidualOrIntrusive input
    """

    def __init__(self, root: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the root tk constructor
        super().__init__(root)
        self.root = root

        # @todo cleaner popup separation?
        self.top = tk.Toplevel(root)
        self.top.configure(bg="#AEC7D6")
        self.top.geometry("1000x400")
        self.top.title("Managing intrusive and residual contexts")
        self.top.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        # self.node_del_tracker = node_track
        # self.controller = controller
        # self.resid_list = resid_list
        # self.intru_list = intru_list
        self.back_button = tk.Button(self.top, text="Go back", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.back_button.grid(column=30, row=4)
        self.proceed_button = tk.Button(
            self.top,
            text="Proceed to render chronological graph",
            bg="#2F4858",
            font=("Helvetica 12 bold"),
            fg="#eff3f6",
        )
        self.proceed_button.grid(column=30, row=6)
        # self.test(resid_list, intru_list)
        # controller.wait_window(self.top)

    def bind_back_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the back_button is pressed"""
        if callback is not None:
            self.back_button.config(command=callback)

    def bind_proceed_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the proceed_button is pressed"""
        if callback is not None:
            self.proceed_button.config(command=callback)
