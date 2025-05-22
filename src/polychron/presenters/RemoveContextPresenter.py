from typing import Dict, Optional

from ..interfaces import Mediator
from ..views.RemoveContextView import RemoveContextView
from .BasePopupPresenter import BasePopupPresenter


class RemoveContextPresenter(BasePopupPresenter[Dict[str, Optional[str]]]):
    """Presenter for a popup window to input the reason for the removal of a node/context

    Formerly `popupWindow5`, called by StartPage.node_del_popup, triggered when "Delete context" is selected on a node

    Todo:
        @todo - use a an actual Model class not just a Dict.
    """

    def __init__(self, mediator: Mediator, view: RemoveContextView, model: Dict[str, Optional[str]]) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind buttons
        self.view.bind_ok_button(self.on_ok_button)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        if "context" in self.model:
            self.view.update_label(self.model["context"])

    def on_ok_button(self) -> None:
        """When the ok button is pressed, store the dataframe in the model and close the popup"""
        # @todo - validate input if it's required?
        # Store the provided reason in the model
        self.model["reason"] = self.view.get_reason()
        # Close the popup
        self.close_view()
