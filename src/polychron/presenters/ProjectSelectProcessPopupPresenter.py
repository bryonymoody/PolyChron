from __future__ import annotations

from typing import Dict

from ..GUIThemeManager import GUIThemeManager
from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ModelCreateView import ModelCreateView
from ..views.ModelSelectView import ModelSelectView
from ..views.ProjectCreateView import ProjectCreateView
from ..views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from ..views.ProjectSelectView import ProjectSelectView
from ..views.ProjectWelcomeView import ProjectWelcomeView
from .FramePresenter import FramePresenter
from .ModelCreatePresenter import ModelCreatePresenter
from .ModelSelectPresenter import ModelSelectPresenter
from .PopupPresenter import PopupPresenter
from .ProjectCreatePresenter import ProjectCreatePresenter
from .ProjectSelectPresenter import ProjectSelectPresenter
from .ProjectWelcomePresenter import ProjectWelcomePresenter


class ProjectSelectProcessPopupPresenter(PopupPresenter[ProjectSelectProcessPopupView, ProjectSelection], Mediator):
    """Presenter for the project new or select process, which is a mult-frame presenter, much like the main window."""

    def __init__(self, mediator: Mediator, view: ProjectSelectProcessPopupView, model: ProjectSelection) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        # Store a refenrece to the GUIThemeManager object from the mediator internally, to be forwarded later if required (as this is also a Mediator)
        self.theme_manager = mediator.get_theme_manager()

        # Build a dictionary of child presenter-view pairings
        self.current_presenter_key = None
        self.presenters: Dict[str, FramePresenter] = {
            "project_welcome": ProjectWelcomePresenter(
                self, ProjectWelcomeView(self.view.container, self.theme_manager), self.model
            ),
            "project_select": ProjectSelectPresenter(
                self, ProjectSelectView(self.view.container, self.theme_manager), self.model
            ),
            "project_create": ProjectCreatePresenter(
                self, ProjectCreateView(self.view.container, self.theme_manager), self.model
            ),
            "model_select": ModelSelectPresenter(
                self, ModelSelectView(self.view.container, self.theme_manager), self.model
            ),
            "model_create": ModelCreatePresenter(
                self, ModelCreateView(self.view.container, self.theme_manager), self.model
            ),
        }
        # Intiialse all the views within the parent view
        for presenter in self.presenters.values():
            presenter.view.place_in_container()

        # Set the initial sub-presenter
        self.switch_presenter("project_welcome")

    def update_view(self) -> None:
        pass

    def set_window_title(self, suffix: str | None = None) -> None:
        """Update the popup window title to reflect the current state of the project selection process

        Parameters:
            suffix: an optional suffix which will be appended to the default window title
        """
        title = "PolyChron loading page"
        if suffix is not None and len(str(suffix)) > 0:
            title += f" | {suffix}"
        self.view.title(title)

    def get_presenter(self, key: str | None) -> FramePresenter | None:
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

        # If the new presenter key is valid, replace the current presenter with the new one
        if new_presenter := self.get_presenter(key):
            # Hide the current presenter if set
            if current_presenter is not None:
                current_presenter.view.not_visible_in_container()
                self.current_presenter_key = None
            # Update the now-current presenter & view
            self.current_presenter_key = key
            # Apply any view updates in case the model has been changed since last rendered
            new_presenter.update_view()
            # Make the new presenter's view visible
            new_presenter.view.visible_in_container()

            # Update the window title to potentially include a suffix.
            self.set_window_title(new_presenter.get_window_title_suffix())
        else:
            raise RuntimeError(
                f"Invalid presenter key '{key}' for ProjectSelectProcessPopupPresenter.switch_presenter. Valid values: {list(self.presenters.keys())}"
            )

    def close_window(self, reason: str = None) -> None:
        """Close the process popup window, changing the main window presenter/view as required

        Todo:
            close_view and close_window should be combined.
        """
        # 3.10 required for match, so using elif
        if reason is None:
            pass
        elif reason == "new_model":
            self.mediator.switch_presenter("Model")
        elif reason == "load_model":
            self.mediator.switch_presenter("Model")
        else:
            raise ValueError(f"Unknown reason {reason} for `ProjectSelectProcessPopupPresenter.close_window")
        # Close the view
        self.view.destroy()

    def get_theme_manager(self) -> GUIThemeManager:
        return self.theme_manager
