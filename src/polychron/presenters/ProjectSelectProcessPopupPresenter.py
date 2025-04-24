from typing import Any, Dict, Optional

from ..interfaces import Navigator
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


class ProjectSelectProcessPopupPresenter(BasePopupPresenter, Navigator):
    """Presenter for the project new or select process, which is a mult-frame presenter, much like the main window.

    @todo - this is a bit different from a regular PopupPresenter, as it contains multiple views & itself probable needs to be a Navigator. Some of this could be abstracted.

    @todo - this class name is terrible. Maybe split presenters/views into submopdules for mainwindow/popup etc

    @todo - rename Navigator & Navigator protocols, something like MultiPresenterNavigator?
    """

    def __init__(self, navigator: Navigator, view: ProjectSelectProcessPopupView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Build a dictionary of child presenter-view pairings
        self.current_presenter = None
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

    def switch_presenter(self, name: str):
        if name in self.presenters:
            # Hide the current presenter if set
            if self.current_presenter is not None and self.current_presenter in self.presenters:
                self.presenters[self.current_presenter].view.grid_remove()
            # Re-place the frame using grid, with settings remembered from before
            self.current_presenter = name
            self.presenters[name].view.grid()
        else:
            raise Exception("@todo better error missing frame")

    def close_navigator(self, reason: str = None):
        print("@todo update global applciations state")
        # 3.10 required for match, so using elif
        if reason is None:
            pass
        elif reason == "new_model":
            # @todo - update model state in the relevant view
            self.navigator.switch_presenter("Model")
        elif reason == "load_model":
            # @todo - update model state in the relevant view
            self.navigator.switch_presenter("Model")
        else:
            raise Exception("@todo - bad reason for close_navigator.")
        # Close the view
        self.view.destroy()

        # @todo - presumably this is a memory leak? as although the popup.destroy() is called, the presenter is never removed / is still in scope?
