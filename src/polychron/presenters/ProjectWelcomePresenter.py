from typing import Optional

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ProjectWelcomeView import ProjectWelcomeView
from .BaseFramePresenter import BaseFramePresenter


class ProjectWelcomePresenter(BaseFramePresenter):
    def __init__(self, mediator: Mediator, view: ProjectWelcomeView, model: Optional[ProjectSelection] = None) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

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
        # Update the list of available projects from disk (in case any have been created since)
        self.model.projects_directiory.lazy_load()  # @todo - could this go in an on_switched_to() for the dest presenter instead? Unsure how viable with tkinter
        self.mediator.switch_presenter("project_select")

    def on_create_button(self) -> None:
        """When the load button is pressed, update the CreateProject view and switch to it"""
        self.mediator.switch_presenter("project_create")
