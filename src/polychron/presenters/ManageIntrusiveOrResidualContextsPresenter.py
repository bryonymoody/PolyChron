from ..interfaces import Mediator
from ..models.Model import Model
from ..views.ManageGroupRelationshipsView import ManageGroupRelationshipsView
from ..views.ManageIntrusiveOrResidualContextsView import ManageIntrusiveOrResidualContextsView
from .ManageGroupRelationshipsPresenter import ManageGroupRelationshipsPresenter
from .PopupPresenter import PopupPresenter


class ManageIntrusiveOrResidualContextsPresenter(PopupPresenter[Model]):
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
        self.view.create_dropdowns(self.model.resid_list, self.model.intru_list)

        # Update the view
        self.update_view()

    def update_view(self) -> None:
        pass

    def on_back(self) -> None:
        """Callback for when the back button is pressed, which closes the popup (and previous popup origianlly)"""
        # @todo decide / check if this should actualyl close the parent window or not
        self.close_view()

    def on_proceed(self) -> None:
        """Callback for when the back button is pressed, which closes the popup (and previous popup origianlly)

        Formerly (some of) popupWindow4.move_to_graph
        """

        # Update the model with the selected values for the intrusive and residual drop downs.
        self.model.resid_dropdowns = self.view.get_resid_dropdown_selections()
        self.model.intru_dropdowns = self.view.get_intru_dropdown_selections()

        # Create the group relationship manager
        # @todo - abstract this somewhere else? as this will be duplicated in modelPresenter.resid_check
        # show the residual check presenter, formerly popupWindow3
        popup_presenter = ManageGroupRelationshipsPresenter(
            self.mediator, ManageGroupRelationshipsView(self.view), self.model
        )
        popup_presenter.view.lift()  # @todo - not sure these are neccesary
        self.view.wait_window(popup_presenter.view)  # @todo - abstract this somewhere?

        # Close the popup
        self.close_view()
        # Also close the parent popup.
        # @todo - do this nicely, this is probably a leak of the presenter and view objects
        self.view.parent.destroy()
