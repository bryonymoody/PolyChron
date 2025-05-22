from sys import stderr
from typing import Optional

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ProjectCreateView import ProjectCreateView
from .BaseFramePresenter import BaseFramePresenter


class ProjectCreatePresenter(BaseFramePresenter):
    def __init__(self, mediator: Mediator, view: ProjectCreateView, model: Optional[ProjectSelection] = None) -> None:
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
            # @todo - validate that the new project is not a taken name. If so error?polychron 0.1 does not perform this check.
            self.model.next_project_name = new_project_name
            # Mark the flag indicating we are using the project_create process
            self.model.using_new_project_process = True
            # Switch to the model creation view
            self.mediator.switch_presenter("model_create")
        else:
            print("Warning: a project name must be provieded. @todo GUI error message", file=stderr)

    def on_back_button(self) -> None:
        """When the back button is pressed, return to the project_welcome view

        Todo:
            @todo - The project_select view could have a "New Project" button, resplacing the welcome view? In which case this back button would need ammending
        """
        # Clear the new project name
        self.model.next_project_name = None
        # Clear the flag indicating we are using the project_create process
        self.model.using_new_project_process = False
        # Switch to the welcome presenter/view.
        self.mediator.switch_presenter("project_welcome")
