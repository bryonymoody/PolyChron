from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, List

from ..GUIThemeManager import GUIThemeManager
from .FrameView import FrameView


class ProjectSelectView(FrameView):
    """Passive view for project loading/selection"""

    def __init__(self, parent: tk.Frame, theme_manager: GUIThemeManager) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent, theme_manager)
        self.parent = parent

        # Set this element's background to white
        self.config(background="white")

        self.list_label = ttk.Label(self, text="Select project", style="ListboxTitle.TLabel")
        self.list_label.place(relx=0.36, rely=0.1)

        self.project_listbox = tk.Listbox(
            self,
            bg=GUIThemeManager.colour("offwhite2"),
            font=self.theme_manager.font(11, "bold"),
            fg=GUIThemeManager.colour("slate_grey"),
            selectmode="browse",
        )
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.project_listbox.yview)
        self.project_listbox["yscrollcommand"] = scrollbar.set
        self.project_listbox.place(relx=0.36, rely=0.17, relheight=0.4, relwidth=0.28)

        self.load_button = tk.Button(
            self, text="Load project", bg=GUIThemeManager.colour("slate_grey"), fg=GUIThemeManager.colour("offwhite2")
        )
        self.load_button.place(relx=0.8, rely=0.9, relwidth=0.19)
        self.load_button.bind("<Return>", lambda event: self.load_button.invoke())

        self.back_button = tk.Button(
            self, text="Back", bg=GUIThemeManager.colour("offwhite2"), fg=GUIThemeManager.colour("slate_grey")
        )
        self.back_button.place(relx=0.21, rely=0.01)
        self.back_button.bind("<Return>", lambda event: self.back_button.invoke())

    def bind_load_button(self, callback: Callable[[], Any]) -> None:
        """Callback function for the load button, which is also bound for <Return> events with a list box selected"""
        if callback is not None:
            self.load_button.config(command=callback)
            self.project_listbox.bind("<Return>", lambda event: callback())
            self.project_listbox.bind("<Double-1>", lambda event: callback())

    def bind_back_button(self, callback: Callable[[], Any]) -> None:
        if callback is not None:
            self.back_button.config(command=callback)

    def bind_list_select(self, callback: Callable[[], Any]) -> None:
        if callback is not None:
            self.project_listbox.bind("<<ListboxSelect>>", callback)

    def update_project_list(self, project_names: List[str]) -> None:
        """Update the list of projects to choose from to include the provided list of project names"""
        # Clear old entries
        self.project_listbox.delete(0, tk.END)
        # Insert the new entries
        self.project_listbox.insert(tk.END, *project_names)

    def get_selected_project(self) -> str | None:
        """Get the value of the currently selected project name"""
        selected_index = self.project_listbox.curselection()
        if selected_index:
            return self.project_listbox.get(selected_index[0])
        else:
            return None
