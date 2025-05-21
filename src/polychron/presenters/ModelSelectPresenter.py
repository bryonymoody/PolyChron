from sys import stderr
from typing import Any, Optional

from ..interfaces import Mediator
from ..views.ModelSelectView import ModelSelectView
from .BaseFramePresenter import BaseFramePresenter


class ModelSelectPresenter(BaseFramePresenter):
    """Presenter for a frame allowing the user to select a model from a list of models within a project, or a button to create a new one.

    @todo - Sort the list of models?
    """

    def __init__(self, mediator: Mediator, view: ModelSelectView, model: Optional[Any] = None) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind button callbacks
        view.bind_load_button(lambda: self.on_load_button())
        view.bind_back_button(lambda: self.on_back_button())
        view.bind_create_model_button(lambda: self.on_create_model_button())

        # Bind callback for when a model is selected
        view.bind_list_select(self.on_select)

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model

        @todo - sort the models list? Will also need to adjust getting the select model to refer to the sorted list.
        """
        # Update the list of models to select from, if a project has been selected
        # @todo - move some of this logic into the Model class?
        if self.model.selected_project is not None and self.model.selected_project in self.model.projects:
            self.view.update_model_list(list(self.model.projects[self.model.selected_project].models.keys()))

    def on_load_button(self) -> None:
        """When the load button is pressed, update the wider application model data structure and close the popup"""
        selected_model = self.view.get_selected_model()
        if selected_model is not None:
            # Update the data model to include the selected project
            self.model.selected_model = selected_model
            # Close the popup and switch to the ModelPresenter/View
            self.mediator.close_window("load_model")
        else:
            print("Warning: No model selected. @todo this in gui if mouse click not on enter?", file=stderr)

    def on_back_button(self) -> None:
        """When the Back button is pressed, update the previous view and switch to it

        Unlike polychron 0.1 which returned to the project create or load screen, this returns to the project select screen
        """
        # Clear any selected model value, just in case
        self.model.selected_model = None
        # A previous project should be known, so we can return to it. Fallback to the welcome view
        if self.model.selected_project is not None and self.model.selected_project in self.model.projects:
            self.mediator.switch_presenter("project_select")
        else:
            self.mediator.switch_presenter("project_welcome")

    def on_create_model_button(self) -> None:
        """When the load button is pressed, update the current modeldata and switch to the model_create view"""
        self.mediator.switch_presenter("model_create")

    def on_select(self, event=None) -> None:
        """When a list item is selected"""
        pass  # @todo - could update state here instead of only on click?
