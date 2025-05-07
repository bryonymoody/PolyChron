from typing import Any, Optional

from ..interfaces import Mediator
from ..views.ManageGroupRelationshipsView import ManageGroupRelationshipsView
from ..views.ManageIntrusiveOrResidualContextsView import ManageIntrusiveOrResidualContextsView
from .BasePopupPresenter import BasePopupPresenter
from .ManageGroupRelationshipsPresenter import ManageGroupRelationshipsPresenter


class ManageIntrusiveOrResidualContextsPresenter(BasePopupPresenter):
    """Presenter for managing the MCMC progress bar popup view.

    When MCMC calibration has completed, and the popup closes, the DatingResults tab should be loaded
    """

    def __init__(self, mediator: Mediator, view: ManageIntrusiveOrResidualContextsView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind the back button
        self.view.bind_back_button(lambda: self.on_back())
        # Bind the proceed button
        self.view.bind_proceed_button(lambda: self.on_proceed())

        # Initialise the view's drop down elements
        if self.model is not None:
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

        # Create popup3
        # @todo - abstract this somewhere else? as this will be duplicated in modelPresenter.resid_check

        # show the residual check presenter, formerly popupWindow3
        popup_presenter = ManageGroupRelationshipsPresenter(
            self.mediator, ManageGroupRelationshipsView(self.view), self.model
        )
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()  # @todo - not sure these are neccesary
        self.view.wait_window(popup_presenter.view)  # @todo - abstract this somewhere?
        # self.popup3 = popupWindow3(startpage, startpage.graph, startpage.littlecanvas2, startpage.phase_rels, self.dropdown_ns, self.dropdown_intru, self.resid_list, self.intru_list)

        # Setup inputs for the MCMC function
        # @todo - make sure these are in Model for now.
        # self.CONT_TYPE = self.popup3.CONT_TYPE
        # self.prev_phase = self.popup3.prev_phase
        # self.post_phase = self.popup3.post_phase
        # self.phi_ref = self.popup3.phi_ref
        # self.context_no_unordered = self.popup3.context_no_unordered
        # self.graphcopy = self.popup3.graphcopy
        # self.node_del_tracker = self.popup3.node_del_tracker

        # Close the popup
        self.close_view()
        # Also close the parent popup.
        # @todo - do this nicely, this is probably a leak of the presenter and view objects
        self.view.parent.destroy()
