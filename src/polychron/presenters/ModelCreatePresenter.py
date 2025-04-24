from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ModelCreateView import ModelCreateView
from .BaseFramePresenter import BaseFramePresenter


class ModelCreatePresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: ModelCreateView, model: Optional[Any] = None):
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
        """When the submit button is pressed, update the data model and close the view"""
        # @todo input validation, both for new projects and existing projects (i.e. needs knowledge about where this view was from)
        print("@todo - Validate model name input and update global application state")
        self.navigator.close_navigator("new_model")

    def on_back_button(self) -> None:
        """When the back button is pressed, return to the previous view"""
        # @todo make this a true back button. For now this always returns to the project_create page, when it should be bale to return to project_create or model_select
        self.navigator.switch_presenter("project_create")
