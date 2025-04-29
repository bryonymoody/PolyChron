from typing import Any, Optional

from ..interfaces import Mediator
from ..views.AddContextView import AddContextView
from .BasePopupPresenter import BasePopupPresenter


class AddContextPresenter(BasePopupPresenter):
    """Presenter for adding an additional context to the current model

    Formerly `popupWindow`
    """

    def __init__(self, mediator: Mediator, view: AddContextView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind the OK button
        self.view.bind_ok_button(self.on_ok)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass  # @todo

    def on_ok(self) -> None:
        """When the OK button is pressed, validate user in put, update the model and close the popup"""
        # @todo - validate input and if ok update the model / trigger follow on actions.
        self.close_view()
        # @todo - this is prolly a memory leak.
