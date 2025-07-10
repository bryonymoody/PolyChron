from ..interfaces import Mediator
from ..models.RemoveStratigraphicRelationshipModel import RemoveStratigraphicRelationshipModel
from ..views.RemoveStratigraphicRelationshipView import RemoveStratigraphicRelationshipView
from .PopupPresenter import PopupPresenter


class RemoveStratigraphicRelationshipPresenter(
    PopupPresenter[RemoveStratigraphicRelationshipView, RemoveStratigraphicRelationshipModel]
):
    """Presenter for a popup window to provide the reason for the removal of a single stratigraphic relationship

    Formerly `popupWindow6`, called by `StartPage.edge_del_popup`, triggered when "Delete stratigraphic relationship" is selected on an edge
    """

    def __init__(
        self, mediator: Mediator, view: RemoveStratigraphicRelationshipView, model: RemoveStratigraphicRelationshipModel
    ) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        # Bind buttons
        self.view.bind_ok_button(self.on_ok_button)
        self.view.bind_cancel_button(self.on_cancel)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        """Update the RemoveStratigraphicRelationshipView to include the relationship which is being removed"""
        self.view.update_label(self.model.edge_label())

    def on_ok_button(self) -> None:
        """When the ok button is pressed, store the dataframe in the model and close the popup"""
        self.model.reason = self.view.get_reason()
        self.close_view()

    def on_cancel(self) -> None:
        """When the Cancel button is pressed, close the popup without changing the model"""
        self.model.reason = None
        self.close_view()
