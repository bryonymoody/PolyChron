from typing import Any, Dict, Optional

from ..interfaces import Navigator
from ..presenters.BaseFramePresenter import BaseFramePresenter
from ..presenters.BasePopupPresenter import BasePopupPresenter
from ..presenters.ResidualCheckConfirmPresenter import ResidualCheckConfirmPresenter
from ..presenters.ResidualCheckPresenter import ResidualCheckPresenter
from ..views.ResidualCheckConfirmView import ResidualCheckConfirmView
from ..views.ResidualCheckPopupView import ResidualCheckPopupView
from ..views.ResidualCheckView import ResidualCheckView


class ResidualCheckPopupPresenter(BasePopupPresenter, Navigator):
    """Presenter for the residual check process, as a container which contains the 2 underlying presenter-view pairs.

    @todo this can probably be refactored nicer
    """

    def __init__(self, navigator: Navigator, view: ResidualCheckPopupView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Build a dictionary of child presenter-view pairings
        self.current_presenter = None
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

    def switch_presenter(self, name: str):
        if name in self.presenters:
            # Hide the current presenter if set
            if self.current_presenter is not None and self.current_presenter in self.presenters:
                self.presenters[self.current_presenter].view.grid_remove()
            # Re-place the frame using grid, with settings remembered from before
            self.current_presenter = name
            self.presenters[name].view.grid()
        else:
            raise Exception(f"@todo better error missing frame {name} {self.presenters}")

    def close_navigator(self, reason: str = None):
        # @todo
        # Close the view
        self.view.destroy()
        # @todo - presumably this is a memory leak? as although the popup.destroy() is called, the presenter is never removed / is still in scope?
