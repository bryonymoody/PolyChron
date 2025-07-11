from typing import Dict, Optional

from ..interfaces import Mediator
from ..views.AddContextView import AddContextView
from .PopupPresenter import PopupPresenter


class AddContextPresenter(PopupPresenter[AddContextView, Dict[str, Optional[str]]]):
    """Presenter for adding an additional context to the current model

    Formerly `popupWindow`
    """

    def __init__(self, mediator: Mediator, view: AddContextView, model: Dict[str, Optional[str]]) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        # Bind the OK button
        self.view.bind_ok_button(self.on_ok)

        # Bind the cancel button
        self.view.bind_cancel_button(self.on_cancel)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass

    def on_ok(self) -> None:
        """When the OK button is pressed, validate user in put, update the model and close the popup"""
        self.model["value"] = self.view.get_input()
        # Close the popup
        self.close_view()

    def on_cancel(self) -> None:
        """When the Cancel button is pressed, close the popup without changing the model"""
        self.close_view()
