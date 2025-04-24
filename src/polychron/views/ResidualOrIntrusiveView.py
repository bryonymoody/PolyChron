import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, List, Optional

from .BasePopupView import BasePopupView


class ResidualOrIntrusiveView(BasePopupView):
    """View for users to provide input on whether contexts are residual or inclusive during chronological graph rendering

    Formely part of `PageTwo`

    """

    def __init__(self, parent: tk.Frame, start_visible=False):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent, start_visible)

        # @todo cleaner popup separation?
        self.configure(bg="#AEC7D6")
        self.geometry("2000x1000")  # @todo - differnt geometry?
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.graphcanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.graphcanvas.place(relx=0.02, rely=0.05, relwidth=0.35, relheight=0.9)
        # @todo - this label suggests blue boxes, but green is used.
        self.label = tk.Message(
            self,
            text="Using this page: \n\n Please click on the buttons below to set into residual or intrusive mode. Then double right click on any context to set as residual/intrusive. \n\n Note that orange boxes denote intrusive contexts and blue boxes denote residual contexts. \n\n If you have clicked on a context by mistake, double right click to remove any label attributed to the context.",
        )
        self.label.place(relx=0.4, rely=0.05)
        self.resid_title_label = ttk.Label(self.canvas, text="Residual Contexts")
        self.resid_title_label.place(relx=0.4, rely=0.4)
        self.graphcanvas.update()
        self.residcanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.residcanvas.place(relx=0.4, rely=0.42, relwidth=0.35, relheight=0.08)
        self.resid_label = ttk.Label(self.residcanvas)
        self.resid_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.resid_scroll_bar = ttk.Scrollbar(self.residcanvas)
        self.resid_scroll_bar.pack(side=tk.RIGHT)
        self.intrucanvas = tk.Canvas(
            self.canvas, bd=0, bg="white", selectborderwidth=0, highlightthickness=0, insertwidth=0
        )
        self.intrucanvas.place(relx=0.4, rely=0.54, relwidth=0.35, relheight=0.08)
        self.intru_label = ttk.Label(self.intrucanvas)
        self.intru_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.intru_scroll_bar = ttk.Scrollbar(self.intrucanvas)
        self.intru_scroll_bar.pack(side=tk.RIGHT)
        self.intru_title_label = ttk.Label(self.canvas, text="Intrusive Contexts")
        self.intru_title_label.place(relx=0.4, rely=0.52)

        self.proceed_button = ttk.Button(self, text="Proceed")
        self.proceed_button.place(relx=0.48, rely=0.65, relwidth=0.09, relheight=0.03)

        self.residual_mode_button = tk.Button(self, text="Residual mode")
        self.residual_mode_button.place(relx=0.44, rely=0.35, relwidth=0.09, relheight=0.03)
        self.intrusive_mode_button = tk.Button(self, text="Intrusive mode")
        self.intrusive_mode_button.place(relx=0.54, rely=0.35, relwidth=0.09, relheight=0.03)

        # self.parent.wait_window(self) # @todo

        # @todo - move these to tests
        # self.set_resid_label_text(["foo", "bar"])
        # self.set_intru_label_text(["foo", "bar", "baz"])
        # self.set_residual_mode_button_background("orange")
        # self.set_intrusive_mode_button_background("lightgreen")

    def set_resid_label_text(self, resid_list: List[str]):
        """Update the intrusive list

        @todo - check this behaves as intended, it might make a copy?
        """
        self.resid_label["text"] = str(resid_list).replace("'", "")[1:-1]

    def set_intru_label_text(self, intru_list: List[str]):
        """Update the intrusive list

        @todo - check this behaves as intended, it might make a copy?
        """
        self.intru_label["text"] = str(intru_list).replace("'", "")[1:-1]

    def bind_proceed_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the proceed_button is pressed"""
        if callback is not None:
            self.proceed_button.config(command=callback)

    def bind_residual_mode_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the residual_mode_button is pressed"""
        if callback is not None:
            self.residual_mode_button.config(command=callback)

    def bind_intrusive_mode_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the intrusive_mode_button is pressed"""
        if callback is not None:
            self.intrusive_mode_button.config(command=callback)

    def set_residual_mode_button_background(self, color: str):
        self.residual_mode_button.config(background=str(color))

    def set_intrusive_mode_button_background(self, color: str):
        self.intrusive_mode_button.config(background=str(color))

    def bind_graphcanvas_events(
        self,
        callback_wheel: Callable[[], Optional[Any]],
        callback_node_click: Callable[[], Optional[Any]],
        callback_move_from: Callable[[], Optional[Any]],
        callback_move_to: Callable[[], Optional[Any]],
    ) -> None:
        """Bind mouse callback events for interacting with the graph canvas

        @todo - split this method?

        @todo better callback names
        """
        self.graphcanvas.bind("<MouseWheel>", callback_wheel)
        self.graphcanvas.bind("<Button-4>", callback_wheel)  # only with Linux, wheel scroll down
        self.graphcanvas.bind("<Button-5>", callback_wheel)
        self.graphcanvas.bind("<Double-Button-3>", callback_node_click)
        self.graphcanvas.bind("<Button-1>", callback_move_from)
        self.graphcanvas.bind("<B1-Motion>", callback_move_to)
