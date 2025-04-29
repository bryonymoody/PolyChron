from typing import Any, Dict, Optional

from ..interfaces import Mediator
from ..presenters.BaseFramePresenter import BaseFramePresenter
from ..presenters.BasePopupPresenter import BasePopupPresenter
from ..presenters.ResidualCheckConfirmPresenter import ResidualCheckConfirmPresenter
from ..presenters.ResidualCheckPresenter import ResidualCheckPresenter
from ..views.ResidualCheckConfirmView import ResidualCheckConfirmView
from ..views.ResidualCheckPopupView import ResidualCheckPopupView
from ..views.ResidualCheckView import ResidualCheckView


class ResidualCheckPopupPresenter(BasePopupPresenter, Mediator):
    """Presenter for the residual check process, as a container which contains the 2 underlying presenter-view pairs.

    @todo this can probably be refactored nicer
    """

    def __init__(self, mediator: Mediator, view: ResidualCheckPopupView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Build a dictionary of child presenter-view pairings
        self.current_presenter_key = None
        self.presenters: Dict[str, BaseFramePresenter] = {
            "residual_check": ResidualCheckPresenter(self, ResidualCheckView(self.view.container), self.model),
            "residual_check_confirm": ResidualCheckConfirmPresenter(
                self, ResidualCheckConfirmView(self.view.container), self.model
            ),
        }

        # Intiialse all the views within the parent view
        # @todo - abstract this somewhere?
        for presenter in self.presenters.values():
            presenter.view.grid(row=0, column=0, sticky="nsew")
            presenter.view.grid_remove()

        # Set the initial sub-presenter
        self.switch_presenter("residual_check")

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass  # @todo

    def get_presenter(self, key: Optional[str]):
        if key in self.presenters:
            return self.presenters[key]
        else:
            return None

    def switch_presenter(self, key: Optional[str]):
        if new_presenter := self.get_presenter(key):
            # Hide the current presenter if set
            if current_presenter := self.get_presenter(self.current_presenter_key):
                current_presenter.view.grid_remove()
                self.current_presenter_key = None

            # Update the now-current view
            self.current_presenter_key = key
            # Apply any view updates in case the model has been changed since last rendered
            new_presenter.update_view()
            # Re-place the frame using grid, with settings remembered from before
            new_presenter.view.grid()
            # Give it focus for any keybind events
            new_presenter.view.focus_set()
        else:
            raise Exception(f"@todo better error missing frame {key} {self.presenters}")

    def close_window(self, reason: Optional[str] = None):
        # @todo
        # Close the view
        self.view.destroy()
        # @todo - presumably this is a memory leak? as although the popup.destroy() is called, the presenter is never removed / is still in scope?
