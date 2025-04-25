import tkinter as tk
from typing import Any, Callable, Optional

from .BasePopupView import BasePopupView


class RemoveStratigraphicRelationshipView(BasePopupView):
    """View for providing the reason wehn removing a specific stratigraphic relationship

    Formerly `popupWindow6`

    @todo - Add the specific relationship details to the text label?
    @todo - Add the option to not remove the relationship, i.e. cancel / go back?
    """

    def __init__(self, parent: tk.Frame, start_visible=False):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent, start_visible)

        # @todo cleaner popup separation?
        self.configure(bg="white")
        self.geometry("1000x400")
        self.title("Removal of stratigraphic relationship")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        self.label = tk.Label(
            self,
            text="Why are you deleting the stratigraphic relationship between these contexts?",
            bg="white",
            font="helvetica 12",
            fg="#2f4858",
        )
        self.label.place(relx=0.3, rely=0.1)
        self.text = tk.Text(self, font="helvetica 12", fg="#2f4858")
        self.text.place(relx=0.3, rely=0.2, relheight=0.5, relwidth=0.5)
        self.ok_button = tk.Button(self, text="OK", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.ok_button.place(relx=0.3, rely=0.7)

    def bind_ok_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)
