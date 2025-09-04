from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from .PopupView import PopupView


class SelectCalibrationCurveView(PopupView):
    """View for selecting a calibration curve

    Displays a list of available calibration curves for the user to choose from.
    """

    def __init__(self, parent: tk.Frame) -> None:
        super().__init__(parent)

        # Set a window title and size
        self.title("Model calibration")
        self.centered_geometry(400, 300)

        # Label
        self.label = ttk.Label(self, text="Select Calibration Curve")
        self.label.pack(pady=(10, 5))

        # Dropdown (Combobox)
        self.curve_selector = ttk.Combobox(self, state="readonly")
        self.curve_selector.pack(pady=(0, 10))

        # OK Button
        self.ok_button = ttk.Button(self, text="Ok")
        self.ok_button.pack(pady=(0, 5))

        # Cancel Button
        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_button.pack()

    def set_curve_options(self, curve_names: list[str]) -> None:
        """Set the dropdown values for available calibration curves"""
        self.curve_selector["values"] = curve_names
        if curve_names:
            self.curve_selector.current(0)

    def bind_ok_button(self, callback: Callable[[], Any | None]) -> None:
        """Bind a function to the OK button"""
        if callback is not None:
            self.ok_button.config(command=callback)

    def bind_cancel_button(self, callback: Callable[[], Any | None]) -> None:
        """Bind a function to the Cancel button"""
        if callback is not None:
            self.cancel_button.config(command=callback)

    def get_selection(self) -> str:
        """Return the selected calibration curve name"""
        return self.curve_selector.get()
