from typing import Any, Optional

from ..interfaces import Navigator
from ..views.BaseFrameView import BaseFrameView
from .BaseMainWindowPresenter import BaseMainWindowPresenter


class WelcomePresenter(BaseMainWindowPresenter):
    def __init__(self, navigator: Navigator, view: BaseFrameView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # @todo - bind callbacks

    def update_view(self):
        pass  # @todo
