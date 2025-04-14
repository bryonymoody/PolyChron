"""The main GUI App class, which initialises the GUI application and can be used to run the main render loop"""

from importlib.metadata import version
import re
from tkinter import ttk
from ttkthemes import ThemedTk
from typing import Any, Dict, Optional

from .Config import Config
from .views.WelcomeView import WelcomeView
from .views.ModelCreateView import ModelCreateView
from .views.ModelSelectView import ModelSelectView
from .views.ProjectCreateView import ProjectCreateView
from .views.ProjectSelectView import ProjectSelectView

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

        # register protocols and global key bindings
        self.register_global_keybinds()
        self.register_protocols()

        # @todo MVP

        # setup the initial view

    def register_global_keybinds(self):
        """Register application-wide key bindings"""
        # ctrl+w to close the window @todo this might need changing for sub-windows..
        self.root.bind("<Control-w>", self.exit_application)
    
    def register_protocols(self):
        """Register protocols with the root window - i.e. what to do on (graceful) application exit"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def exit_application(self, event: Optional[Any] = None) -> None:
        """Callback function for graceful application exit via keybind or window manager close. """
        # @todo - add any exit behaviour here
        # Quit the root window
        self.root.quit()

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

    def launch(self, viewName: Optional[str], viewIdx: Optional[int]) -> None:
        """Method to launch the GUIApp, i.e. start the render loop
        
        @todo - remove the viewName and viewIdx params
        """

        # Temporary dictionary of view instances, for use during refactoring before the addition of Models or Presenters
        views: Dict[str, ttk.Frame] = {
            "WelcomeView": WelcomeView,
            "ProjectCreateView": ProjectCreateView,
            "ProjectSelectView": ProjectSelectView,
            "ModelCreateView": ModelCreateView,
            "ModelSelectView": ModelSelectView,
        }

        # Temporary view-only cli options for testing views
        print("--view options:")
        for i, v in enumerate(views):
            print(f"  {i}: {v}")
        viewClass = views[list(views.keys())[0]]
        if viewName is not None:
            if viewName not in views:
                raise Exception(f"--view {viewName} is not valid")
            viewClass = views[viewName]
        elif viewIdx is not None:
            if viewIdx < 0 or viewIdx >= len(views):
                raise Exception(f"--viewidx {viewIdx} invalid, must be in range [0, {len(views)})")
            viewClass = views[list(views.keys())[viewIdx]]

        viewClass(self.root)

        self.root.mainloop()
