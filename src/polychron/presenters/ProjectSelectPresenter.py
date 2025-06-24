from sys import stderr

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ProjectSelectView import ProjectSelectView
from .FramePresenter import FramePresenter


class ProjectSelectPresenter(FramePresenter[ProjectSelectView, ProjectSelection]):
    def __init__(self, mediator: Mediator, view: ProjectSelectView, model: ProjectSelection) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        # Bind button callbacks to presenter methods
        self.view.bind_load_button(self.on_load_button)
        self.view.bind_back_button(self.on_back_button)

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model"""
        project_names = list(self.model.projects_directory.projects.keys())
        self.view.update_project_list(project_names)

    def on_load_button(self) -> None:
        """When the load button is pressed, update the wider application model data structure and close the popup"""
        selected_project = self.view.get_selected_project()
        if selected_project is not None:
            # Update the data model to include the selected project
            self.model.next_project_name = selected_project
            # Switch views
            self.mediator.switch_presenter("model_select")
        else:
            print("Warning: No project selected", file=stderr)

    def on_back_button(self) -> None:
        """When the Back button is pressed, update the previous view and switch to it"""
        self.model.next_project_name = None
        self.mediator.switch_presenter("project_welcome")
