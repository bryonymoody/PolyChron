import tkinter as tk
from typing import Any, Callable, Optional

from .BasePopupView import BasePopupView


class RemoveStratigraphicRelationshipView(BasePopupView):
    """View for providing the reason wehn removing a specific stratigraphic relationship

    Formerly `popupWindow6`

    @todo - Add the specific relationship details to the text label?
    @todo - Add the option to not remove the relationship, i.e. cancel / go back?
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # @todo cleaner popup separation?
        self.configure(bg="white")
        self.geometry("1000x400")
        self.title("Removal of stratigraphic relationship")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        # Add a label, without the text value set by update_label to avoid duplication
        self.label = tk.Label(
            self,
            bg="white",
            font="helvetica 12",
            fg="#2f4858",
        )
        self.update_label()
        self.label.place(relx=0.3, rely=0.1)

        # Place a text entry box
        self.text = tk.Text(self, font="helvetica 12", fg="#2f4858")
        self.text.place(relx=0.3, rely=0.2, relheight=0.5, relwidth=0.5)

        # Place an OK button
        self.ok_button = tk.Button(self, text="OK", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.ok_button.place(relx=0.3, rely=0.7)

        # @todo cancel button?

    def bind_ok_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)

    def update_label(self, edge_label: Optional[str] = None) -> None:
        """Update the label text to include the edge being removed."""
        edge_label = "these contexts" if edge_label is None else f"{edge_label}"
        self.label.configure(text=f"Why are you deleting the stratigraphic relationship between {edge_label}?")

    def get_reason(self) -> str:
        """Get the reason from the text area"""
        return self.text.get("1.0", "end")
