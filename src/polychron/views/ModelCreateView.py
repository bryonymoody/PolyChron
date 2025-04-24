import tkinter as tk
from typing import Any, Callable, Optional

from .BaseFrameView import BaseFrameView


class ModelCreateView(BaseFrameView):
    """Passive view for model creation"""

    def __init__(self, parent: tk.Frame):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # Set this element's background to white @todo use a theme?
        self.config(background="white")

        # Receiving user's folder_name selection
        self.model = tk.StringVar()

        self.text_1 = tk.Label(self, text="Input model name:", bg="white", font=("helvetica 14 bold"), fg="#2F4858")
        self.text_1.place(relx=0.4, rely=0.2)
        self.user_input = tk.Entry(self, textvariable=self.model)
        self.user_input.place(relx=0.35, rely=0.4, relwidth=0.3, relheight=0.08)
        self.submit_button = tk.Button(self, text="Submit ", bg="#ec9949", font=("Helvetica 12 bold"), fg="#2F4858")
        self.submit_button.place(relx=0.66, rely=0.4)
        # self.top.bind('<Return>', (lambda event:  self.create_file(folder_dir, load))) # @todo
        self.back_button = tk.Button(self, text="Back", bg="#dcdcdc", font=("helvetica 12 bold"), fg="#2F4858")
        self.back_button.place(relx=0.21, rely=0.01)

    def bind_submit_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the submit_button is pressed"""
        if callback is not None:
            self.submit_button.config(command=callback)

    def bind_back_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the back button is pressed"""
        if callback is not None:
            self.back_button.config(command=callback)

    def get_name(self) -> str:
        """Get the model name provided by the user"""
        return str(self.model)
