from abc import ABC, abstractmethod
from typing import Any, Optional

from ..interfaces import Navigator
from ..views.BaseFrameView import BaseFrameView


class BaseMainWindowPresenter(ABC):
    """Abstract Base class for Presenters for views which are in the main window, which act as the middle man between a veiw and the underlying data structures (model).

    @todo should / could this be combined with a simialr class for popup window presenters?

    @todo - rename. Remove base? "FramePresenter" or similar?
    """

    def __init__(self, navigator: Navigator, view: BaseFrameView, model: Optional[Any] = None):
        """Initialise the presenter

        Args:
            navigator (Navigator): an object which implements the Navigator protocol, i.e. the MainApp
            view (BaseFrameView): The view instance to be presented
            model (Optional[Any]): Model objects which include data and buiseness logic
        """

        self.navigator: Navigator = navigator
        """Reference to the parent navigator class, to enable switching between presenters/views"""

        self.view: BaseFrameView = view
        """View managed by this presenter"""

        self.model: Optional[Any] = model
        """Model objects which include data and buisness logic which are presented by this presenter/view"""

    @abstractmethod
    def update_view(self) -> None:
        """Update view data for the current state of the model

        @todo - actually do this in smaller methods?
        @todo - rename?
        """
        pass

    # @todo - bind abstract method which binds all callbacks?
