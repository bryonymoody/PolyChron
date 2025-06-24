import sys

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ProjectCreateView import ProjectCreateView
from .FramePresenter import FramePresenter


class ProjectCreatePresenter(FramePresenter[ProjectCreateView, ProjectSelection]):
    def __init__(self, mediator: Mediator, view: ProjectCreateView, model: ProjectSelection) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        # Bind button callbacks to presenter methods
        view.bind_submit_button(lambda: self.on_submit_button())
        view.bind_back_button(lambda: self.on_back_button())

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        pass

    def on_submit_button(self) -> None:
        """When the submit button is pressed, update the CreateModel view and switch to it"""
        new_project_name: str = self.view.get_name()
        if new_project_name is not None and len(new_project_name) > 0:
            self.model.next_project_name = new_project_name
            # Mark the flag indicating we are using the project_create process
            self.model.using_new_project_process = True
            # Switch to the model creation view
            self.mediator.switch_presenter("model_create")
        else:
            print("Warning: a project name must be provided.", file=sys.stderr)

    def on_back_button(self) -> None:
        """When the back button is pressed, return to the project_welcome view"""
        # Clear the new project name
        self.model.next_project_name = None
        # Clear the flag indicating we are using the project_create process
        self.model.using_new_project_process = False
        # Switch to the welcome presenter/view.
        self.mediator.switch_presenter("project_welcome")
