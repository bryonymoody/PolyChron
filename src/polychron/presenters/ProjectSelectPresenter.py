from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ProjectSelectView import ProjectSelectView
from .BaseFramePresenter import BaseFramePresenter


class ProjectSelectPresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: ProjectSelectView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind button callbacks to presenter methods
        view.bind_load_button(lambda: self.on_load_button())
        view.bind_back_button(lambda: self.on_back_button())

        # Update the view data for the model
        self.update_view()

    def update_view(self) -> None:
        """Update text & tables within the view to reflect the current state of the model"""
        pass  # @todo

    def on_load_button(self) -> None:
        """When the load button is pressed, update the wider application model data structure and close the popup"""
        # @todo - do something with the selected entry
        self.navigator.switch_presenter("model_select")

    def on_back_button(self) -> None:
        """When the Back button is pressed, update the previous view and switch to it"""
        self.navigator.switch_presenter("project_welcome")
