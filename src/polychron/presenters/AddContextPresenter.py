from typing import Dict, Optional

from ..interfaces import Mediator
from ..views.AddContextView import AddContextView
from .PopupPresenter import PopupPresenter


class AddContextPresenter(PopupPresenter[Dict[str, Optional[str]]]):
    """Presenter for adding an additional context to the current model

    Formerly `popupWindow`
    """

    def __init__(self, mediator: Mediator, view: AddContextView, model: Dict[str, Optional[str]]) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind the OK button
        self.view.bind_ok_button(self.on_ok)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass

    def on_ok(self) -> None:
        """When the OK button is pressed, validate user in put, update the model and close the popup"""
        self.model["value"] = self.view.get_input()
        # Close the popup
        self.close_view()
