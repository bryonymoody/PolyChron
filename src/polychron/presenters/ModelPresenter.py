from .BaseMainWindowPresenter import BaseMainWindowPresenter
from ..views.ModelView import ModelView
from typing import Any, Optional
from ..interfaces import Navigator


class ModelPresenter(BaseMainWindowPresenter):
    def __init__(self, navigator: Navigator, view: ModelView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        view.bind_sasd_tab_button(lambda: self.navigator.switch_main_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.navigator.switch_main_presenter("DatingResults"))
