from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ResidualCheckConfirmView import ResidualCheckConfirmView
from .BaseFramePresenter import BaseFramePresenter


class ResidualCheckConfirmPresenter(BaseFramePresenter):
    """Presenter for confirming the group relationships specified

    @todo - rename this and associated classes

    @todo - recfactor this and the 2 other presenter/view pairs to reduce duplication
    """

    def __init__(self, navigator: Navigator, view: ResidualCheckConfirmView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind the confirm button
        self.view.bind_render_button(lambda: self.on_render())

        # Bind the change (back) button
        self.view.bind_change_button(lambda: self.on_change())

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass  # @todo

    def on_render(self) -> None:
        """Close the popup and render the chrono graph"""
        # @todo - update model data and trigger the actual render
        self.navigator.close_navigator("render")

    def on_change(self) -> None:
        """Go back to the other view within the popoup, so relationships can be changed once again"""
        self.navigator.switch_presenter("residual_check")
