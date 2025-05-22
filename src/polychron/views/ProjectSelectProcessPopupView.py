import tkinter as tk

from .PopupView import PopupView


class ProjectSelectProcessPopupView(PopupView):
    """View for the project selection popup window, which contains the frames that the view(s) for each step are placed into and switched between."""

    def __init__(self, parent: tk.Frame) -> None:
        """Construct the view, without binding any callbacks"""
        # Call the parent class constructor
        super().__init__(parent)

        # Set the popup title
        self.title("PolyChron loading page")
        # Set the geometry, which naturally is centered within the parent window
        self.geometry("1000x400")  # @todo - not hardcoded here?
        # @todo - orignal placement code
        # root_x = master.winfo_rootx()
        # root_y = master.winfo_rooty()
        # win_x = root_x + 500
        # win_y = root_y + 200
        # self.top.geometry(f'1000x400+{win_x}+{win_y}')

        # @todo - do this here rather thn in each child?
        # Declare 2 canvas, splitting the UI into 2 columns
        # Subsequent views are placed into one of these canvas elements and switched between by the presenter
        self.container = tk.Frame(self, bg="white")
        self.container.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.sidebar = tk.Frame(self, bg="#AEC7D6")
        self.sidebar.place(relx=0, rely=0, relheight=1, relwidth=0.2)

        # Set the container as a grid of a single element, for switching between contained views
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
