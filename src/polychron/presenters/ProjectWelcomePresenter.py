from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ProjectWelcomeView import ProjectWelcomeView
from .BaseFramePresenter import BaseFramePresenter


class ProjectWelcomePresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: ProjectWelcomeView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind button callbacks to presenter methods
        view.bind_load_button(lambda: self.on_load_button())
        view.bind_create_button(lambda: self.on_create_button())

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model"""
        pass  # @todo

    def on_load_button(self) -> None:
        """When the load button is pressed, update the SelectProject view and switch to it"""
        self.navigator.switch_presenter("project_select")

    def on_create_button(self) -> None:
        """When the load button is pressed, update the CreateProject view and switch to it"""
        self.navigator.switch_presenter("project_create")
