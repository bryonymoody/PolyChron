from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ModelSelectView import ModelSelectView
from .BaseFramePresenter import BaseFramePresenter


class ModelSelectPresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: ModelSelectView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind button callbacks
        view.bind_load_button(lambda: self.on_load_button())
        view.bind_back_button(lambda: self.on_back_button())
        view.bind_create_model_button(lambda: self.on_create_model_button())

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model"""
        pass  # @todo

    def on_load_button(self) -> None:
        """When the load button is pressed, update the wider application model data structure and close the popup"""
        print("@todo - update data strucutres loading the model")
        self.navigator.close_navigator("load_model")

    def on_back_button(self) -> None:
        """When the Back button is pressed, update the previous view and switch to it"""
        # @todo - this back button needs to be a true back button, not just go back to project_create (matching 0.1 behaviour)
        self.navigator.switch_presenter("project_create")

    def on_create_model_button(self) -> None:
        """When the load button is pressed, update the current modeldata and switch to the model_create view"""
        self.navigator.switch_presenter("model_create")
