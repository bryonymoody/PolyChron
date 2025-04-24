from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ManageIntrusiveOrResidualContextsView import ManageIntrusiveOrResidualContextsView
from .BasePopupPresenter import BasePopupPresenter


class ManageIntrusiveOrResidualContextsPresenter(BasePopupPresenter):
    """Presenter for managing the MCMC progress bar popup view.

    When MCMC calibration has completed, and the popup closes, the navigator should change to the DatingResults tab
    """

    def __init__(self, navigator: Navigator, view: ManageIntrusiveOrResidualContextsView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind the back button
        self.view.bind_back_button(lambda: self.on_back())
        # Bind the proceed button
        self.view.bind_proceed_button(lambda: self.on_proceed())
        # Update the view
        self.update_view()

    def on_back(self) -> None:
        """Callback for when the back button is pressed, which closes the popup (and previous popup origianlly)"""
        # @todo decide / check if this should actualyl close the parent window or not
        self.close_view()

    def on_proceed(self) -> None:
        """Callback for when the back button is pressed, which closes the popup (and previous popup origianlly)"""
        print("@todo - actually update the data model before closing the window?")
        self.close_view()
        # also close the parent popup.
        # @todo - do this nicely, this is probably a leak of the presenter and view objects
        self.view.parent.destroy()

    def update_view(self) -> None:
        # @todo - update view elements aas required once data is present
        pass
