import tkinter as tk

from .BasePopupView import BasePopupView


class ResidualCheckPopupView(BasePopupView):
    """View for the residual check popup

    This contains a single frame into which other views are placed

    @todo - the child views have commoon elements, so it might be better to refactor this into a single presenter/view
    """

    def __init__(self, parent: tk.Frame, start_visible=False):
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent, start_visible)

        # Set the popup title
        self.title("Adding group relationships")

        # Set the geometry, which naturally is centered within the parent window
        self.geometry("1500x400")

        # Ensure this window is on top
        self.attributes("-topmost", "true")  # @todo maybe remove.

        # Place a single, maximised containing element for child views to be inserted into
        self.container = tk.Frame(self, bg="white")
        self.container.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
