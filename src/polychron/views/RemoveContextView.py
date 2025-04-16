import tkinter as tk
from typing import Any, Callable, Optional
from .BasePopupView import BasePopupView


class RemoveContextView(BasePopupView):
    """View for removing contexts, providing a free-text reason

    Formerly `popupWindow5`
    """

    def __init__(self, parent: tk.Tk):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)
        self.parent = parent

        self.configure(bg="white")
        self.geometry("1000x400")
        self.title("Removal of context")
        self.attributes("-topmost", "true")  # @todo maybe remove. # Forces the top level to always be on top.

        self.label = tk.Label(
            self,
            text="Why are you removing this context from your stratigraphy?",
            bg="white",
            font="helvetica 12",
            fg="#2f4858",
        )
        self.label.place(relx=0.3, rely=0.1)
        self.text = tk.Text(self, font="helvetica 12", fg="#2f4858")
        self.text.place(relx=0.3, rely=0.2, relheight=0.5, relwidth=0.5)
        self.ok_button = tk.Button(self, text="OK", bg="#2F4858", font=("Helvetica 12 bold"), fg="#eff3f6")
        self.ok_button.place(relx=0.3, rely=0.7)

    # def cleanup(self):
    #     self.value=self.text.get('1.0', 'end')
    #     self.destroy()

    def bind_ok_button(self, callback: Callable[[], Optional[Any]]) -> None:
        """Bind the callback for when the ok_button is pressed"""
        if callback is not None:
            self.ok_button.config(command=callback)
