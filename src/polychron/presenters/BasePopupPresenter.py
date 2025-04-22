from abc import ABC, abstractmethod
from typing import Any, Optional

from ..interfaces import Navigator
from ..views.BasePopupView import BasePopupView


class BasePopupPresenter(ABC):
    """Abstract Base class for Presenters for views which are in the main window, which act as the middle man between a veiw and the underlying data structures (model).

    @todo common base class with BaseMainWindowPresenter?
    """

    def __init__(self, navigator: Navigator, view: BasePopupView, model: Optional[Any] = None):
        """Initialise the presenter

        Args:
            navigator (Navigator): an object which implements the Navigator protocol, i.e. the MainApp
            view (BasePopupView): The view instance to be presented
            model (Optional[Any]): Model objects which include data and buiseness logic
        """

        self.navigator: Navigator = navigator
        """Reference to the parent navigator class, to enable switching between presenters/views"""

        self.view: BasePopupView = view
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

    def display_view(self) -> None:
        """Make the view visible (and not minimised)"""
        self.view.deiconify()

    def minimise_view(self) -> None:
        """Minimise the view"""
        self.view.iconify()
    
    def hide_view(self) -> None:
        """Hide (withdraw) the view"""
        self.view.withdraw()

    # @todo - bind abstract method which binds all callbacks?
