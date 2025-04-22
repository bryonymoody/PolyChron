from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ModelView import ModelView
from .BaseMainWindowPresenter import BaseMainWindowPresenter


class ModelPresenter(BaseMainWindowPresenter):
    def __init__(self, navigator: Navigator, view: ModelView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind callback functions for switching between the main view tabs
        view.bind_sasd_tab_button(lambda: self.navigator.switch_main_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.navigator.switch_main_presenter("DatingResults"))

        # Bind menu callbacks
        # @todo

        # Bind button clicks
        # @todo

        # Bind mouse & keyboard events
        # @todo

        # Update data

    def update_view(self):
        pass  # @todo
