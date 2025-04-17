from abc import ABC
from typing import Any, Optional

from ..interfaces import Navigator
from ..views.BaseMainWindowView import BaseMainWindowView


class BaseMainWindowPresenter(ABC):
    """Abstract Base class for Presenters for views which are in the main window, which act as the middle man between a veiw and the underlying data structures (model).

    @todo should / could this be combined with a simialr class for popup window presenters?
    """

    def __init__(self, navigator: Navigator, view: BaseMainWindowView, model: Optional[Any] = None):
        """Initialise the presenter

        Args:
            navigator (Navigator): an object which implements the Navigator protocol, i.e. the MainApp
            view (BaseMainWindowView): The view instance to be presented
            model (Optional[Any]): Model objects which include data and buiseness logic
        """

        self.navigator: Navigator = navigator
        """Reference to the parent navigator class, to enable switching between presenters/views"""

        self.view: BaseMainWindowView = view
        """View managed by this presenter"""

        self.model: Optional[Any] = model
        """Model objects which include data and buisness logic which are presented by this presenter/view"""
