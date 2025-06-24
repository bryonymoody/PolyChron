from __future__ import annotations

from typing import Dict

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

        # Build a dictionary of child presenter-view pairings
        self.current_presenter_key = None
        self.presenters: Dict[str, FramePresenter] = {
            "project_welcome": ProjectWelcomePresenter(self, ProjectWelcomeView(self.view.container), self.model),
            "project_select": ProjectSelectPresenter(self, ProjectSelectView(self.view.container), self.model),
            "project_create": ProjectCreatePresenter(self, ProjectCreateView(self.view.container), self.model),
            "model_select": ModelSelectPresenter(self, ModelSelectView(self.view.container), self.model),
            "model_create": ModelCreatePresenter(self, ModelCreateView(self.view.container), self.model),
        }
        # Intiialse all the views within the parent view
        for presenter in self.presenters.values():
            presenter.view.grid(row=0, column=0, sticky="nsew")
            presenter.view.grid_remove()

        # Set the initial sub-presenter
        self.switch_presenter("project_welcome")

    def update_view(self) -> None:
        pass

    def get_presenter(self, key: str | None) -> FramePresenter | None:
        if key is not None and key in self.presenters:
            return self.presenters[key]
        else:
            return None

    def switch_presenter(self, key: str | None) -> None:
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
        else:
            raise RuntimeError(
                f"Invalid presenter key '{key}' for ProjectSelectProcessPopupPresenter.switch_presenter. Valid values: {list(self.presenters.keys())}"
            )

    def close_window(self, reason: str = None) -> None:
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
