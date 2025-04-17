from .BaseMainWindowPresenter import BaseMainWindowPresenter
from ..views.BaseMainWindowView import BaseMainWindowView
from typing import Any, Optional
from ..interfaces import Navigator


class WelcomePresenter(BaseMainWindowPresenter):
    def __init__(self, navigator: Navigator, view: BaseMainWindowView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        print("WelcomePresenter.__init__()")
