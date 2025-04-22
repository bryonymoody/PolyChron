"""The main GUI App class, which initialises the GUI application and can be used to run the main render loop"""

import re
import tkinter as tk
from importlib.metadata import version
from tkinter import ttk
from typing import Any, Dict, Optional

from ttkthemes import ThemedTk

from .Config import Config
from .interfaces import Navigator
from .presenters.BaseMainWindowPresenter import BaseMainWindowPresenter
from .presenters.DatingResultsPresenter import DatingResultsPresenter
from .presenters.ModelPresenter import ModelPresenter
from .presenters.WelcomePresenter import WelcomePresenter
from .views.AddContextView import AddContextView
from .views.BaseMainWindowView import BaseMainWindowView
from .views.BasePopupView import BasePopupView
from .views.CalibrateModelSelectView import CalibrateModelSelectView
from .views.DatafilePreviewView import DatafilePreviewView
from .views.DatingResultsView import DatingResultsView
from .views.GetSupplementaryDataView import GetSupplementaryDataView
from .views.ManageIntrusiveOrResidualContexts import ManageIntrusiveOrResidualContexts
from .views.MCMCProgressView import MCMCProgressView
from .views.ModelCreateView import ModelCreateView
from .views.ModelSelectView import ModelSelectView
from .views.ModelView import ModelView
from .views.ProjectCreateView import ProjectCreateView
from .views.ProjectSelectView import ProjectSelectView
from .views.RemoveContextView import RemoveContextView
from .views.RemoveStratigraphicRelationshipView import RemoveStratigraphicRelationshipView
from .views.ResidualCheckConfirmView import ResidualCheckConfirmView
from .views.ResidualCheckView import ResidualCheckView
from .views.ResidualOrIntrusiveView import ResidualOrIntrusiveView
from .views.WelcomeView import WelcomeView


class GUIApp(Navigator):
    """Main GUIApp which is provides the main entry point, initialises the Models, Views and Presenters and opens the main window.

    This includes code which used to belong to `MainFrame`

    This is the only class/file which should import tkinter / ThemedTK other than View classes (unless needed for typehinting?)
    """

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

        # Add a frame which fills the full root window, in to which other main window frames will be placed.
        # @todo - make this a ttk frame instead?
        self.container = tk.Frame(self.root)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Construct the views and presenters for main window views (i.e. not-popups)
        self.current_main_window_presenter: Optional[str] = None
        self.main_window_presenters: Dict[str, BaseMainWindowPresenter] = {
            "Welcome": WelcomePresenter(self, WelcomeView(self.container), {"@todo": "todo"}),
            "Model": ModelPresenter(self, ModelView(self.container), {"@todo": "todo"}),
            "DatingResults": DatingResultsPresenter(self, DatingResultsView(self.container), {"@todo": "todo"}),
        }

        # Place each main window within the container
        # @todo - make this part of a common base class mainWindowFrameView?
        for presenter in self.main_window_presenters.values():
            presenter.view.grid(row=0, column=0, sticky="nsew")
            # Immeditely hide the frame, but remember it's settings.
            presenter.view.grid_remove()
        # Hide the

        # @todo MVP

    def switch_main_presenter(self, name: str):
        """Show a speicfic frame/view by it's name on the main window"""
        if name in self.main_window_presenters:
            # Hide the current presenter if set
            if (
                self.current_main_window_presenter is not None
                and self.current_main_window_presenter in self.main_window_presenters
            ):
                self.main_window_presenters[self.current_main_window_presenter].view.grid_remove()

            # Re-place the frame using grid, with settings remembered from before
            self.current_main_window_presenter = name
            self.main_window_presenters[name].view.grid()
        else:
            raise Exception("@todo better error missing frame")

    def register_global_keybinds(self):
        """Register application-wide key bindings"""
        # ctrl+w to close the window @todo this might need changing for sub-windows..
        self.root.bind("<Control-w>", self.exit_application)

    def register_protocols(self):
        """Register protocols with the root window - i.e. what to do on (graceful) application exit"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def exit_application(self, event: Optional[Any] = None) -> None:
        """Callback function for graceful application exit via keybind or window manager close."""
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

        if viewName is None and viewIdx is None:
            # Actual intended body of this method, which should be all that is left once debugging is stripped out.
            # shwo the initial view
            # self.switch_main_presenter("Welcome")
            self.switch_main_presenter("Model")
            # self.switch_main_presenter("DatingResults")
            self.root.mainloop()
        else:
            # Temporary dictionary of view instances, for use during refactoring before the addition of Models or Presenters
            # popupWindow9 and popupWindow10 don't have any view related content + marked as alpha?
            views: Dict[str, ttk.Frame] = {
                "WelcomeView": WelcomeView,
                "ModelView": ModelView,
                "DatingResultsView": DatingResultsView,
                "ProjectCreateView": ProjectCreateView,
                "ProjectSelectView": ProjectSelectView,
                "ModelCreateView": ModelCreateView,
                "ModelSelectView": ModelSelectView,
                "AddContextView": AddContextView,
                "GetSupplementaryDataView": GetSupplementaryDataView,
                "ResidualCheckView": ResidualCheckView,
                "ResidualCheckConfirmView": ResidualCheckConfirmView,
                "ManageIntrusiveOrResidualContexts": ManageIntrusiveOrResidualContexts,
                "RemoveContextView": RemoveContextView,
                "RemoveStratigraphicRelationshipView": RemoveStratigraphicRelationshipView,
                "DatafilePreviewView": DatafilePreviewView,
                "CalibrateModelSelectView": CalibrateModelSelectView,
                "MCMCProgressView": MCMCProgressView,
                "ResidualOrIntrusiveView": ResidualOrIntrusiveView,
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

            # Depending on if mainwindow or popupwindow, handle it differntly.
            if issubclass(viewClass, BaseMainWindowView):
                # This is gross
                self.switch_main_presenter(viewClass.__name__.replace("View", ""))
            elif issubclass(viewClass, BasePopupView):
                v = viewClass(self.root, start_visible=False)
                v.deiconify()
            else:
                viewClass(self.root)
            self.root.mainloop()
