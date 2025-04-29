from typing import Any, Dict, Optional

from ..interfaces import Mediator
from ..views.ModelCreateView import ModelCreateView
from ..views.ModelSelectView import ModelSelectView
from ..views.ProjectCreateView import ProjectCreateView
from ..views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from ..views.ProjectSelectView import ProjectSelectView
from ..views.ProjectWelcomeView import ProjectWelcomeView
from .BaseFramePresenter import BaseFramePresenter
from .BasePopupPresenter import BasePopupPresenter
from .ModelCreatePresenter import ModelCreatePresenter
from .ModelSelectPresenter import ModelSelectPresenter
from .ProjectCreatePresenter import ProjectCreatePresenter
from .ProjectSelectPresenter import ProjectSelectPresenter
from .ProjectWelcomePresenter import ProjectWelcomePresenter


class ProjectSelectProcessPopupPresenter(BasePopupPresenter, Mediator):
    """Presenter for the project new or select process, which is a mult-frame presenter, much like the main window.

    @todo - this is a bit different from a regular PopupPresenter, as it contains multiple views & itself probable needs to be a Mediator. Some of this could be abstracted.

    @todo - this class name is terrible. Maybe split presenters/views into submopdules for mainwindow/popup etc

    @todo - rename Mediator & Mediator protocols, something like MultiPresenterMediator?
    """

    def __init__(self, mediator: Mediator, view: ProjectSelectProcessPopupView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Build a dictionary of child presenter-view pairings
        self.current_presenter_key = None
        self.presenters: Dict[str, BaseFramePresenter] = {
            "project_welcome": ProjectWelcomePresenter(self, ProjectWelcomeView(self.view.container), self.model),
            "project_select": ProjectSelectPresenter(self, ProjectSelectView(self.view.container), self.model),
            "project_create": ProjectCreatePresenter(self, ProjectCreateView(self.view.container), self.model),
            # @todo - should the model_ be children of the select/create bits instead?
            "model_select": ModelSelectPresenter(self, ModelSelectView(self.view.container), self.model),
            "model_create": ModelCreatePresenter(self, ModelCreateView(self.view.container), self.model),
        }
        # Intiialse all the views within the parent view
        # @todo - abstract this somewhere?
        for presenter in self.presenters.values():
            presenter.view.grid(row=0, column=0, sticky="nsew")
            presenter.view.grid_remove()

        # Set the initial sub-presenter
        self.switch_presenter("project_welcome")

    def update_view(self) -> None:
        pass  # @todo

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
        else:
            raise Exception("@todo better error missing frame")

    def close_window(self, reason: str = None):
        # 3.10 required for match, so using elif
        if reason is None:
            pass
        elif reason == "new_model":
            # @todo - update model state in the relevant view
            self.mediator.switch_presenter("Model")
        elif reason == "load_model":
            # @todo - update model state in the relevant view
            self.mediator.switch_presenter("Model")
        else:
            raise Exception("@todo - bad reason for close_window.")
        # Close the view
        self.view.destroy()
        self.view = None  # @todo this is mega dangerous / risky / will break things.

        # @todo - presumably this is a memory leak? as although the popup.destroy() is called, the presenter is never removed / is still in scope?
