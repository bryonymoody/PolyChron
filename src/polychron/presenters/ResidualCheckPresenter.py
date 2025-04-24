from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ResidualCheckView import ResidualCheckView
from .BaseFramePresenter import BaseFramePresenter


class ResidualCheckPresenter(BaseFramePresenter):
    """Presenter for managing Residual vs Intrusive contexsts

    @todo - createa a popup for this and the confirmation version
    """

    def __init__(self, navigator: Navigator, view: ResidualCheckView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind the confirm groups button
        self.view.bind_confirm_button(lambda: self.on_confirm())

        # @todo - bind canvas events for dragging boxes around
        # self.view.bind_

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass  # @todo

    def on_confirm(self) -> None:
        # @todo trigger changes in the model for the confirm view
        self.navigator.switch_presenter("residual_check_confirm")
