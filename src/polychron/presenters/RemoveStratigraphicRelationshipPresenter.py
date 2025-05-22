from typing import Dict, Optional

from ..interfaces import Mediator
from ..views.RemoveStratigraphicRelationshipView import RemoveStratigraphicRelationshipView
from .BasePopupPresenter import BasePopupPresenter


class RemoveStratigraphicRelationshipPresenter(BasePopupPresenter[Dict[str, Optional[str]]]):
    """Presenter for a popup window to provide the reason for the removal of a single stratigraphic relationship

    Formerly `popupWindow6`, called by StartPage.edge_del_popup, triggered when "Delete stratigraphic relationship" is selected on an edge

    Todo:
        @todo - use a an actual Model class not just a Dict.
    """

    def __init__(
        self, mediator: Mediator, view: RemoveStratigraphicRelationshipView, model: Dict[str, Optional[str]]
    ) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind buttons
        self.view.bind_ok_button(self.on_ok_button)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        if "context_a" in self.model and "context_b" in self.model:
            edge_label = f"'{self.model['context_a']}' and '{self.model['context_b']}'"
            self.view.update_label(edge_label)

    def on_ok_button(self) -> None:
        """When the ok button is pressed, store the dataframe in the model and close the popup"""
        # @todo - validate input and if ok update the model / trigger follow on actions.
        self.model["reason"] = self.view.get_reason()
        self.close_view()
