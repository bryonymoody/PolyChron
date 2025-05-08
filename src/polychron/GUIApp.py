"""The main GUI App class, which initialises the GUI application and can be used to run the main render loop"""

import re
import tkinter as tk
import tkinter.font as tkFont
from importlib.metadata import version
from tkinter import ttk
from typing import Any, Dict, Optional

from ttkthemes import ThemedStyle, ThemedTk

from .Config import Config
from .interfaces import Mediator
from .models.InterpolationData import InterpolationData
from .models.ProjectsDirectory import ProjectsDirectory
from .presenters.BaseFramePresenter import BaseFramePresenter
from .presenters.DatingResultsPresenter import DatingResultsPresenter
from .presenters.ModelPresenter import ModelPresenter
from .presenters.ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter
from .presenters.SplashPresenter import SplashPresenter
from .views.DatingResultsView import DatingResultsView
from .views.ModelView import ModelView
from .views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from .views.SplashView import SplashView


class GUIApp(Mediator):
    """Main GUIApp which is provides the main entry point, initialises the Models, Views and Presenters and opens the main window.

    This includes code which used to belong to `MainFrame`

    This is the only class/file which should import tkinter / ThemedTK other than View classes (unless needed for typehinting?)

    @todo @enhancement ensure all tk.messagebox calls withint the app have the appropriate parent set (or replace with in-window messages)
    """

    def __init__(self) -> None:
        # Initialse the application config object
        self.config: Config = Config.from_default_filepath()

        # Construct the root tkinter window, as a themed TK app
        self.root: ThemedTk = ThemedTk(theme="arc")

        # style / font configuration options.
        # @todo - abstract into a method somewhere
        # @todo - check these actually behave as intended.
        # style.set_theme("arc")
        style = ThemedStyle(self.root)
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=12, weight="bold")
        style = ttk.Style(self.root)
        style.configure("TEntry", font=("Helvetica", 12, "bold"))
        style.configure("TButton", font=("Helvetica", 12, "bold"))
        style.configure("TLabel", font=("Helvetica", 12, "bold"))
        style.configure("TOptionMenu", font=("Helvetica", 12, "bold"))
        style.configure("TTreeView", font=("Helvetica", 12, "bold"))

        # Set the window title
        self.set_window_title()
        # Set the root window geometry from the potentially user provided size.
        self.resize_window(self.config.geometry)

        # register protocols and global key bindings
        self.register_global_keybinds()
        self.register_protocols()

        # Add a frame which fills the full root window, in to which other main window frames will be placed.
        # @todo - make this a ttk frame instead?
        # @todo - make this ContainerView or something?
        self.container = tk.Frame(self.root)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Instantiate the "global" applcation data object
        # @todo - may need to have a ProjectsDirectory object which does not actually parse the Project/Models, but instead just provides accessors.
        # @todo rename.
        self.projects_directory_obj: ProjectsDirectory = ProjectsDirectory(path=self.config.projects_directory)

        # @todo - move this to where it is needed, though checking on startup is nice.
        self.calibration: InterpolationData = InterpolationData()
        # self.calibration.load() # @todo

        # Construct the views and presenters for main window views (i.e. not-popups)
        self.current_presenter_key: Optional[str] = None
        # @todo - decide on and use the appropriate data object for the MVP model parameter for each display. May need to
        self.presenters: Dict[str, BaseFramePresenter] = {
            "Splash": SplashPresenter(self, SplashView(self.container), self.projects_directory_obj),
            "Model": ModelPresenter(self, ModelView(self.container), self.projects_directory_obj),
            "DatingResults": DatingResultsPresenter(
                self, DatingResultsView(self.container), self.projects_directory_obj
            ),
        }

        # Place each main window within the container
        # @todo - make this part of a common base class mainWindowFrameView?
        for presenter in self.presenters.values():
            presenter.view.grid(row=0, column=0, sticky="nsew")
            # Immeditely hide the frame, but remember it's settings.
            presenter.view.grid_remove()

        # Construct views and presenters for popups? @todo
        # Or should these be owned by the presenter which leads to them being opened? @todo

    def set_window_title(self, suffix: Optional[str] = None) -> None:
        """Update the window title to include Polychron, the version of polychron, and the optional suffix"""
        title = f"PolyChron {version('polychron')}"
        if suffix is not None and len(str(suffix)) > 0:
            title += f" | {suffix}"
        self.root.title(title)

    def get_presenter(self, key: Optional[str]):
        if key is not None and key in self.presenters:
            return self.presenters[key]
        else:
            return None

    def switch_presenter(self, key: Optional[str]):
        if new_presenter := self.get_presenter(key):
            # Hide the current presenter if set
            if current_presenter := self.get_presenter(self.current_presenter_key):
                current_presenter.view.grid_remove()
                self.current_presenter_key = None

            # Update the now-current view
            self.current_presenter_key = key
            # Apply any view updates in case the model has been changed since last rendered
            new_presenter.update_view()
            # Re-place the frame using grid, with settings remembered from before
            new_presenter.view.grid()
            # Give it focus for any keybind events
            new_presenter.view.focus_set()

            # @todo - move the title logic to the presenter and just call an appropraite method here
            if (
                key == "Model"
                or key == "DatingResults"
                and self.projects_directory_obj.selected_project is not None
                and self.projects_directory_obj.selected_model is not None
            ):
                self.set_window_title(
                    f"{self.projects_directory_obj.selected_project} - {self.projects_directory_obj.selected_model}"
                )
            else:
                self.set_window_title()
        else:
            raise Exception("@todo better error missing frame")

    def close_window(self, reason: Optional[str] = None) -> None:
        print(
            "@todo - decide on if this should existr, or implement GUIApp::close_window or separate a Mediator and ClosableMediator"
        )
        self.exit_application()

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

    def launch(self, project_name: Optional[str] = None, model_name: Optional[str] = None) -> None:
        """Method to launch the GUIApp, i.e. start the render loop

        Parameters:
            project_name: An optional project to start with
            model_name: An optional model, within the optional project, to start with
        """

        # Set the initial view to the splash view
        self.switch_presenter("Splash")
        splash_presenter = self.get_presenter("Splash")

        # @todo - this is a bit gross and needs improving.
        # Instantiate the child presenter and view, which otherwise would be done by SplashPresenter.on_select_project
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self, ProjectSelectProcessPopupView(splash_presenter.view), self.projects_directory_obj
        )

        # If an initial project is provided, attempt to start with it
        if project_name is not None:
            # Load projects and models
            self.projects_directory_obj.load()
            # @todo - validate cli provided project / model names
            # @todo - move this logic somewhere else & de-duplicate.
            if project_name in self.projects_directory_obj.projects:
                self.projects_directory_obj.selected_project = project_name
                if model_name is not None:
                    project = self.projects_directory_obj.projects[project_name]
                    if model_name in project.models:
                        self.projects_directory_obj.selected_model = model_name
                        # Close the popup
                        popup_presenter.close_window("load_model")
                    else:
                        self.projects_directory_obj.new_model = model_name
                        # Create the new model and close
                        self.projects_directory_obj.create_model_from_self()
                        popup_presenter.close_window("new_model")
                else:
                    # Switch to the select model presenter, to allowe selection or input
                    popup_presenter.switch_presenter("model_select")
            else:
                self.projects_directory_obj.new_project = project_name
                if model_name is not None:
                    self.projects_directory_obj.new_model = model_name
                    # Create the new model and close
                    self.projects_directory_obj.create_model_from_self()
                    popup_presenter.close_window("new_model")
                else:
                    # switch to the create model page
                    popup_presenter.switch_presenter("model_create")

        # If the window has not been closed, make it visible and on top
        # @todo - this is likely to need changing
        if popup_presenter.view is not None:
            # Ensure the project selection popup is visible and on top
            popup_presenter.view.lift()

        # Start the render loop
        self.root.mainloop()
