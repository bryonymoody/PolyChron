from __future__ import annotations

from typing import Dict

from ..interfaces import Mediator
from ..views.RemoveStratigraphicRelationshipView import RemoveStratigraphicRelationshipView
from .PopupPresenter import PopupPresenter


class RemoveStratigraphicRelationshipPresenter(
    PopupPresenter[RemoveStratigraphicRelationshipView, Dict[str, str | None]]
):
    """Presenter for a popup window to provide the reason for the removal of a single stratigraphic relationship

    Formerly `popupWindow6`, called by StartPage.edge_del_popup, triggered when "Delete stratigraphic relationship" is selected on an edge
    """

    def __init__(
        self, mediator: Mediator, view: RemoveStratigraphicRelationshipView, model: Dict[str, str | None]
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
        self.model["reason"] = self.view.get_reason()
        self.close_view()
