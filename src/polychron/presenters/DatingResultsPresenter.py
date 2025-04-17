from .BaseMainWindowPresenter import BaseMainWindowPresenter
from ..views.DatingResultsView import DatingResultsView
from typing import Any, Optional
from ..interfaces import Navigator


class DatingResultsPresenter(BaseMainWindowPresenter):
    def __init__(self, navigator: Navigator, view: DatingResultsView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        print("DatingResutlsPresenter.__init__()")

        view.bind_sasd_tab_button(lambda: self.navigator.switch_main_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.navigator.switch_main_presenter("DatingResults"))
