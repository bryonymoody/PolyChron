from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ProjectCreateView import ProjectCreateView
from .BaseFramePresenter import BaseFramePresenter


class ProjectCreatePresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: ProjectCreateView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind button callbacks to presenter methods
        view.bind_submit_button(lambda: self.on_submit_button())
        view.bind_back_button(lambda: self.on_back_button())

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model"""
        pass  # @todo

    def on_submit_button(self) -> None:
        """When the submit button is pressed, update the CreateModel view and switch to it"""
        # @todo update model & relevant view
        self.navigator.switch_presenter("model_create")

    def on_back_button(self) -> None:
        """When the back button is pressed, return to the project_welcome view"""
        # @todo double check this is the only option for the back button / implement a true back button.
        self.navigator.switch_presenter("project_welcome")
