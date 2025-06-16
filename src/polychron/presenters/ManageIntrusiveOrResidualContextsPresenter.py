from ..interfaces import Mediator
from ..models.Model import Model
from ..views.ManageGroupRelationshipsView import ManageGroupRelationshipsView
from ..views.ManageIntrusiveOrResidualContextsView import ManageIntrusiveOrResidualContextsView
from .ManageGroupRelationshipsPresenter import ManageGroupRelationshipsPresenter
from .PopupPresenter import PopupPresenter


class ManageIntrusiveOrResidualContextsPresenter(PopupPresenter[ManageIntrusiveOrResidualContextsView, Model]):
    """Presenter for managing the MCMC progress bar popup view.

    When MCMC calibration has completed, and the popup closes, the DatingResults tab should be loaded
    """

    def __init__(self, mediator: Mediator, view: ManageIntrusiveOrResidualContextsView, model: Model = None) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind the back button
        self.view.bind_back_button(lambda: self.on_back())
        # Bind the proceed button
        self.view.bind_proceed_button(lambda: self.on_proceed())

        # Initialise the view's drop down elements
        self.view.create_dropdowns(self.model.residual_contexts, self.model.intrusive_contexts)

        # Update the view
        self.update_view()

    def update_view(self) -> None:
        pass

    def on_back(self) -> None:
        """Callback for when the back button is pressed, which closes the popup (and previous popup origianlly)"""
        self.close_view()

    def on_proceed(self) -> None:
        """Callback for when the back button is pressed, which closes the popup (and previous popup origianlly)

        Formerly (some of) popupWindow4.move_to_graph
        """

        # Update the model with the selected values for the intrusive and residual drop downs.
        self.model.residual_context_types = self.view.get_resid_dropdown_selections()
        self.model.intrusive_context_types = self.view.get_intru_dropdown_selections()

        # Create the group relationship manager
        # show the residual check presenter, formerly popupWindow3
        popup_presenter = ManageGroupRelationshipsPresenter(
            self.mediator, ManageGroupRelationshipsView(self.view), self.model
        )
        popup_presenter.view.lift()
        self.view.wait_window(popup_presenter.view)

        # Close the popup
        self.close_view()
        # Also close the parent popup.
        self.view.parent.destroy()
