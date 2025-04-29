from sys import stderr
from typing import Any, Optional

from ..interfaces import Mediator
from ..views.ProjectSelectView import ProjectSelectView
from .BaseFramePresenter import BaseFramePresenter


class ProjectSelectPresenter(BaseFramePresenter):
    def __init__(self, mediator: Mediator, view: ProjectSelectView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind button callbacks to presenter methods
        # @todo - be consistent with use of lambdas or not. For presenter class methods, should be fine without?
        view.bind_load_button(self.on_load_button)
        view.bind_back_button(self.on_back_button)

        # Bind callback for when a project is selected
        view.bind_list_select(self.on_select)

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model"""
        self.view.update_project_list(list(self.model.projects.keys()))
        pass  # @todo

    def on_load_button(self) -> None:
        """When the load button is pressed, update the wider application model data structure and close the popup"""
        selected_project = self.view.get_selected_project()
        if selected_project is not None:
            # Update the data model to include the selected project
            self.model.selected_project = selected_project
            # Switch views
            self.mediator.switch_presenter("model_select")
        else:
            print("Warning: No project selected. @todo this in gui if mouse click not on enter?", file=stderr)

    def on_back_button(self) -> None:
        """When the Back button is pressed, update the previous view and switch to it"""
        self.model.selected_project = None
        self.mediator.switch_presenter("project_welcome")

    def on_select(self, event=None) -> None:
        """When a list item is selected, do soemthing"""
        pass  # @todo
