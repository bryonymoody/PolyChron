from __future__ import annotations

import tkinter as tk
from typing import Any, Callable

from ..GUIThemeManager import GUIThemeManager
from .PopupView import PopupView


class RemoveStratigraphicRelationshipView(PopupView):
    """View for providing the reason wehn removing a specific stratigraphic relationship

    Formerly `popupWindow6`
    """

    def __init__(self, parent: tk.Frame, theme_manager: GUIThemeManager) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent, theme_manager)

        self.configure(bg="white")
        self.geometry("1000x400")
        self.title("Removal of stratigraphic relationship")
        self.attributes("-topmost", "true")

        # Add a label, without the text value set by update_label to avoid duplication
        self.label = tk.Label(
            self,
            bg="white",
            font=self.theme_manager.font(12),
            fg=GUIThemeManager.colour("slate_grey"),
        )
        self.update_label()
        self.label.place(relx=0.3, rely=0.1)

        # Place a text entry box
        self.text = tk.Text(self, font=self.theme_manager.font(12), fg=GUIThemeManager.colour("slate_grey"))
        self.text.place(relx=0.3, rely=0.2, relheight=0.5, relwidth=0.5)

        # Place an OK button
        self.ok_button = tk.Button(
            self, text="OK", bg=GUIThemeManager.colour("slate_grey"), fg=GUIThemeManager.colour("offwhite2")
        )
        self.ok_button.place(relx=0.3, rely=0.7)

        # Place a Cancel Button
        self.cancel_button = tk.Button(
            self,
            text="Cancel",
            bg=GUIThemeManager.colour("slate_grey"),
            fg=GUIThemeManager.colour("offwhite2"),
            command=self.destroy,
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

    def update_label(self, edge_label: str | None = None) -> None:
        """Update the label text to include the edge being removed."""
        edge_label = "these contexts" if edge_label is None else f"{edge_label}"
        self.label.configure(text=f"Why are you deleting the stratigraphic relationship between {edge_label}?")

    def get_reason(self) -> str:
        """Get the reason from the text area"""
        return self.text.get("1.0", "end")
