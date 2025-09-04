"""The main GUI App class, which initialises the GUI application and can be used to run the main render loop"""

from __future__ import annotations

import re
import sys
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from typing import Any, Dict

from ttkthemes import ThemedStyle, ThemedTk

from . import __version__
from .Config import Config, get_config
from .interfaces import Mediator
from .models.ProjectSelection import ProjectSelection
from .presenters.DatingResultsPresenter import DatingResultsPresenter
from .presenters.FramePresenter import FramePresenter
from .presenters.ModelPresenter import ModelPresenter
from .presenters.ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter
from .presenters.SplashPresenter import SplashPresenter
from .util import check_graphviz_usable
from .views.DatingResultsView import DatingResultsView
from .views.ModelView import ModelView
from .views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from .views.SplashView import SplashView


class GUIApp(Mediator):
    """Main GUIApp which is provides the main entry point, initialises the Models, Views and Presenters and opens the main window.

    This includes code which used to belong to `MainFrame`

    This is the only class/file which should import tkinter / ThemedTK other than View classes (unless needed for typehinting?)
    """

    def __init__(self) -> None:
        # Initialise the application config object
        self.config: Config = get_config()

        # Construct the root tkinter window, as a themed TK app
        self.root: ThemedTk = ThemedTk(theme="arc")

        # style / font configuration options.
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
        self.container = tk.Frame(self.root)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Instantiate the "global" application data object
        self.project_selector_obj: ProjectSelection = ProjectSelection(self.config.projects_directory)

        # Construct the views and presenters for main window views (i.e. not-popups)
        self.current_presenter_key: str | None = None
        self.presenters: Dict[str, FramePresenter] = {
            "Splash": SplashPresenter(self, SplashView(self.container), self.project_selector_obj),
            "Model": ModelPresenter(self, ModelView(self.container), self.project_selector_obj),
            "DatingResults": DatingResultsPresenter(self, DatingResultsView(self.container), self.project_selector_obj),
        }

        # Place each main window within the container
        for presenter in self.presenters.values():
            presenter.view.place_in_container()

        # Set the initial presenter
        self.switch_presenter("Splash")

    def set_window_title(self, suffix: str | None = None) -> None:
        """Update the window title to include Polychron, the version of polychron, and the optional suffix

        Parameters:
            suffix: an optional suffix which will be appended to the default window title
        """
        title = f"PolyChron {__version__}"
        if suffix is not None and len(str(suffix)) > 0:
            title += f" | {suffix}"
        self.root.title(title)

    def get_presenter(self, key: str | None) -> FramePresenter | None:
        """Get a main frame presenter by it's name.

        Parameters:
            key: The string key used for the presenter

        Returns:
            The FramePresenter if the key is valid, else None.
        """
        if key is not None and key in self.presenters:
            return self.presenters[key]
        else:
            return None

    def switch_presenter(self, key: str | None) -> None:
        """Switch the current presenter using the provided key

        Parameters:
            key: The key for the presenter to switch to (if not None)"""
        # Get the current presenter
        current_presenter = self.get_presenter(self.current_presenter_key)
        # If the key is None, clear the current presenter
        if key is None and current_presenter is not None:
            current_presenter.view.grid_remove()
            self.current_presenter_key = None
            return

        if (new_presenter := self.get_presenter(key)) is not None:
            # Hide the current presenter if set
            if current_presenter := self.get_presenter(self.current_presenter_key):
                current_presenter.view.not_visible_in_container()
                self.current_presenter_key = None

            # Update the now-current view
            self.current_presenter_key = key
            # Apply any view updates in case the model has been changed since last rendered
            new_presenter.update_view()
            # Re-place the frame using grid, with settings remembered from before
            new_presenter.view.visible_in_container()

            # Update the window title to potentially include a suffix.
            self.set_window_title(new_presenter.get_window_title_suffix())
        else:
            raise RuntimeError(
                f"Invalid presenter key '{key}' for GUIApp.switch_presenter. Valid values: {list(self.presenters.keys())}"
            )

    def close_window(self, reason: str | None = None) -> None:
        self.exit_application()

    def register_global_keybinds(self) -> None:
        """Register application-wide key bindings"""
        # ctrl+w to close the window
        self.root.bind("<Control-w>", self.exit_application)
        # ctrl+s to save the current model
        # self.root.bind("<Control-s>", self.save_current_model)

    def register_protocols(self) -> None:
        """Register protocols with the root window - i.e. what to do on (graceful) application exit"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def save_current_model(self, event: Any | None = None) -> None:
        """If a model is currently open, save it"""
        if self.current_presenter_key in ["Model", "DatingResults"]:
            if model := self.project_selector_obj.current_model:
                model.save()

    def exit_application(self, event: Any | None = None) -> None:
        """Callback function for graceful application exit via keybind or window manager close."""
        # Quit the root window
        self.root.quit()

    def resize_window(self, geometry: str) -> None:
        """resize the root window geometry to be the maximum of the configured size and the screen size reported by tkinter.

        Note for multi-monitor setups this may/will be incorrect."""
        if match := re.match("^([0-9]+)x([0-9]+)$", geometry):
            # Extract the groups
            target_width = int(match.group(1))
            target_height = int(match.group(2))
            # Query the screen info
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            # Build the new geometry string
            new_geometry = f"{min(target_width, screen_width)}x{min(target_height, screen_height)}"
            # Apply the new window geometry
            self.root.geometry(new_geometry)

    def launch(self, project_name: str | None = None, model_name: str | None = None) -> None:
        """Method to launch the GUIApp, i.e. start the render loop

        If an invalid project or model name is provided (i.e '.'), a warning is printed to console and the model selector is started.

        Parameters:
            project_name: An optional project to start with
            model_name: An optional model, within the optional project, to start with
        """

        # Set the initial view to the splash view
        self.switch_presenter("Splash")

        # Check if graphviz is available
        graphviz_usable = check_graphviz_usable()

        if graphviz_usable:
            # Schedule for the project selection presenter process to be initialised after the main render loop is started.
            self.root.after(50, lambda: self._launch_project_selection(project_name, model_name))
        else:
            # Create an error box, scheduled to appear after the render loop starts (with a short delay to ensure error box placement is over the parent window)
            self.root.after(200, lambda: self._show_graphviz_missing_error())

        # Start the render loop
        self.root.mainloop()

    def _launch_project_selection(self, project_name: str | None = None, model_name: str | None = None) -> None:
        """Function for creating the popup presenter for project selection during launch.
        This is scheduled via tkinter .after and a lambda to ensure that the root window geometry is known when the popup is created.

        Parameters:
            project_name: An optional project to start with
            model_name: An optional model, within the optional project, to start with
        """
        # Ensure the root window has been placed / it's geometry and position are set
        self.root.update_idletasks()

        # Lazily load the projects directory, so (potential) existing models and projects are known.
        self.project_selector_obj.projects_directory.lazy_load()

        # Instantiate the child presenter and view, which otherwise would be done by SplashPresenter.on_select_project. This does not start hidden
        splash_presenter = self.get_presenter(self.current_presenter_key)
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self, ProjectSelectProcessPopupView(splash_presenter.view), self.project_selector_obj
        )

        # Handle the --project and --model cli-provided arguments.
        have_project_name = project_name is not None and len(project_name) > 0
        have_model_name = model_name is not None and len(model_name) > 0

        # If we have a project name
        if have_project_name:
            # update the project selection model with it.
            self.project_selector_obj.next_project_name = project_name

            # If we do not have a model name
            if not have_model_name:
                # If the project does not exist, or contains 0 (potential) models
                if (project := self.project_selector_obj.next_project) is None or len(project.models) == 0:
                    # switch to the new model popup
                    popup_presenter.switch_presenter("model_create")
                else:
                    # Otherwise switch to the new model select popup
                    popup_presenter.switch_presenter("model_select")
            else:
                # If we also have a model name, store it in the project selection model
                self.project_selector_obj.next_model_name = model_name

                # Get the reason that the presenter is being closed.
                reason = "load_model" if self.project_selector_obj.next_model is not None else "new_model"

                try:
                    # Try to update the model to the "next" project & model.
                    self.project_selector_obj.switch_to_next_project_model(load_ok=True, create_ok=True)
                except RuntimeError as e:
                    # Invalid project/model names should raise an exception, for which the message should be presented to the user.
                    print(f"{e}", file=sys.stderr)
                    # Clear the project selector next state
                    self.project_selector_obj.next_project_name = None
                    self.project_selector_obj.next_model_name = None
                else:
                    # Close the popup window with the appropriate reason (load or new model)
                    popup_presenter.close_window(reason)

    def _show_graphviz_missing_error(self) -> None:
        """If graphviz was not avialable, display an error popup and close the polychron when the popup is closed"""
        # Show the error message
        self.get_presenter(self.current_presenter_key).view.messagebox_error(
            "Error: Graphviz required",
            "Graphviz must be installed and available on your PATH.\n\nSee the PolyChron Documentation for more information.\n\nhttps://bryonymoody.github.io/PolyChron/getting-started/#graphviz",
        )
        # When the error message is dismissed, close polychron
        self.close_window()
