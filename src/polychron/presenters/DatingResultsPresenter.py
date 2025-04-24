from typing import Any, Optional

from ..interfaces import Navigator
from ..views.DatingResultsView import DatingResultsView
from .BaseFramePresenter import BaseFramePresenter


class DatingResultsPresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: DatingResultsView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind callback functions for switching between the main view tabs
        view.bind_sasd_tab_button(lambda: self.navigator.switch_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.navigator.switch_presenter("DatingResults"))

        # @todo - bind menu buttons

        # @todo - bind callbacks

    def update_view(self) -> None:
        pass  # @todo
