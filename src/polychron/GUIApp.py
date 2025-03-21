"""The main GUI App class, which initialises the GUI application and can be used to run the main render loop"""

from importlib.metadata import version
import re
from ttkthemes import ThemedTk

from .Config import Config


class GUIApp:
    def __init__(self) -> None:
        # Initialse the application config object
        self.config: Config = Config.from_default_filepath()

        # Construct the root tkinter window, as a themed TK app
        self.root: ThemedTk = ThemedTk(theme="arc")

        # Set the window title
        self.root.title(f"PolyChron {version('polychron')}")
        # Set the root window geometry from the potentially user provided size.
        self.resize_window(self.config.geometry)

        # @todo MVP

        # setup the initial view

    def resize_window(self, geometry: str) -> None:
        """resize the root window geometry to be the maximum of the configured size and the screen size reported by tkinter.

        Note for multi-monitor setups this may/will be incorrect."""

        match = re.match("^([0-9]+)x([0-9]+)", geometry)
        if match:
            # Extract the groups
            target_width = int(match.group(1))
            target_height = int(match.group(2))
            # Query the screen infor
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            # Build the new geometry string
            new_geometry = f"{min(target_width, screen_width)}x{min(target_height, screen_height)}"
            # Apply the new window geometry
            self.root.geometry(new_geometry)

    def launch(self) -> None:
        """Method to launch the GUIApp, i.e. start the render loop"""
        self.root.mainloop()
