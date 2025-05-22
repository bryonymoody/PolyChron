import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, List, Optional

from .FrameView import FrameView


class ModelSelectView(FrameView):
    """Passive view for Model loading/selection

    @todo @enhancement - Include the current project name in this view.
    """

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # Set this element's background to white @todo use a theme?
        self.config(background="white")

        self.list_label = tk.Label(self, text="Model list", bg="white", font=("helvetica 14 bold"), fg="#2F4858")
        self.list_label.place(relx=0.36, rely=0.1)
        self.model_listbox = tk.Listbox(
            self,
            # listvariable=self.model_list, # @todo consider re-using
            bg="#eff3f6",
            font=("Helvetica 11 bold"),
            fg="#2F4858",
            selectmode="browse",
        )
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.model_listbox.yview)
        self.model_listbox["yscrollcommand"] = scrollbar.set
        self.model_listbox.place(relx=0.36, rely=0.17, relheight=0.4, relwidth=0.28)

        self.load_button = tk.Button(
            self, text="Load selected model", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6"
        )
        self.load_button.place(relx=0.8, rely=0.9, relwidth=0.195)
        self.load_button.bind("<Return>", lambda event: self.load_button.invoke())

        self.back_button = tk.Button(self, text="Back", bg="#eff3f6", font=("Helvetica 12 bold"), fg="#2F4858")
        self.back_button.place(relx=0.21, rely=0.01)
        self.back_button.bind("<Return>", lambda event: self.back_button.invoke())

        self.create_model_button = tk.Button(
            self, text="Create new model", bg="#eff3f6", font=("Helvetica 12 bold"), fg="#2F4858"
        )
        self.create_model_button.place(relx=0.62, rely=0.9, relwidth=0.17)
        self.create_model_button.bind("<Return>", lambda event: self.create_model_button.invoke())

    def bind_load_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the load_button is pressed & when enter is pressed with a list item selected"""
        if callback is not None:
            self.load_button.config(command=callback)
            self.model_listbox.bind("<Return>", lambda event: callback())
            self.model_listbox.bind("<Double-1>", lambda event: callback())

    def bind_back_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the back_button is pressed"""
        if callback is not None:
            self.back_button.config(command=callback)

    def bind_create_model_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the create_model_button is pressed"""
        if callback is not None:
            self.create_model_button.config(command=callback)

    def bind_list_select(self, callback: Callable[[], Optional[Any]]) -> None:
        # @todo - unbind old callback? for this event?
        if callback is not None:
            self.model_listbox.bind("<<ListboxSelect>>", callback)

    def update_model_list(self, model_names: List[str]):
        """Update the list of models to choose from to include the provided list of model names"""
        # Clear old entries
        self.model_listbox.delete(0, tk.END)
        # Insert the new entries
        self.model_listbox.insert(tk.END, *model_names)

    def get_selected_model(self) -> Optional[str]:
        """Get the value of the currently selected model name"""
        selected_index = self.model_listbox.curselection()
        if selected_index:
            return self.model_listbox.get(selected_index[0])
        else:
            return None
