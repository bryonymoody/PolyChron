from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ProjectWelcomeView import ProjectWelcomeView
from .FramePresenter import FramePresenter


class ProjectWelcomePresenter(FramePresenter[ProjectWelcomeView, ProjectSelection]):
    def __init__(self, mediator: Mediator, view: ProjectWelcomeView, model: ProjectSelection) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind button callbacks to presenter methods
        view.bind_load_button(lambda: self.on_load_button())
        view.bind_create_button(lambda: self.on_create_button())

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model"""
        pass

    def on_load_button(self) -> None:
        """When the load button is pressed, update the SelectProject view and switch to it"""
        # Update the list of available projects from disk (in case any have been created since)
        self.model.projects_directiory.lazy_load()
        self.mediator.switch_presenter("project_select")

    def on_create_button(self) -> None:
        """When the load button is pressed, update the CreateProject view and switch to it"""
        self.mediator.switch_presenter("project_create")
