from __future__ import annotations

import tkinter as tk
from typing import Any, Callable

from .PopupView import PopupView


class RemoveContextView(PopupView):
    """View for removing contexts, providing a free-text reason

    Formerly `popupWindow5`
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        self.configure(bg="white")
        self.geometry("1000x400")
        self.title("Removal of context")
        self.attributes("-topmost", "true")

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

        # Cancel Button
        self.cancel_button = tk.Button(
            self, text="Cancel", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6", command=self.destroy
        )
        self.cancel_button.place(relx=0.72625, rely=0.7)

    def bind_ok_button(self, callback: Callable[[], Any]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)

    def bind_cancel_button(self, callback: Callable[[], Any | None]) -> None:
        """Bind the callback for when the cancel_button is pressed"""
        if callback is not None:
            self.cancel_button.config(command=callback)

    def update_label(self, context: str | None = None) -> None:
        """Update the label text to include the context being removed."""
        context_name = "this context" if context is None else f"'{context}'"
        self.label.configure(text=f"Why are you removing {context_name} from your stratigraphy?")

    def get_reason(self) -> str:
        """Get the reason from the text area"""
        return self.text.get("1.0", "end")
