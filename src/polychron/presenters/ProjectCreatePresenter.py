from sys import stderr
from typing import Any, Optional

from ..interfaces import Mediator
from ..views.ProjectCreateView import ProjectCreateView
from .BaseFramePresenter import BaseFramePresenter


class ProjectCreatePresenter(BaseFramePresenter):
    def __init__(self, mediator: Mediator, view: ProjectCreateView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

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
        new_project_name: str = self.view.get_name()
        if new_project_name is not None and len(new_project_name) > 0:
            # @todo - validate that the new project is not a taken name. If so error.
            # @todo - polychron 0.1 does not perform this check.
            self.model.new_project = new_project_name
            # Switch to the model creation view
            self.mediator.switch_presenter("model_create")
        else:
            print("Warning: a project name must be provieded. @todo GUI error message", file=stderr)

    def on_back_button(self) -> None:
        """When the back button is pressed, return to the project_welcome view"""
        # @todo double check this is the only option for the back button / implement a true back button.
        # Clear the new project name
        self.model.new_project = None
        self.mediator.switch_presenter("project_welcome")
