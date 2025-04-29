from abc import ABC, abstractmethod
from typing import Any, Optional

from ..interfaces import Mediator
from ..views.BasePopupView import BasePopupView


class BasePopupPresenter(ABC):
    """Abstract Base class for Presenters for views which are in the main window, which act as the middle man between a veiw and the underlying data structures (model).

    @todo common base class with BaseFramePresenter?

    @todo rename, Base is superflous.
    """

    def __init__(self, mediator: Mediator, view: type[BasePopupView], model: Optional[Any] = None):
        """Initialise the presenter

        Args:
            mediator (Mediator): an object which implements the Mediator protocol, i.e. the MainApp
            view (type[BasePopupView]): The view instance to be presented
            model (Optional[Any]): Model objects which include data and buiseness logic
        """

        self.mediator: Mediator = mediator
        """Reference to the parent mediator class, to enable switching between presenters/views"""

        self.view: type[BasePopupView] = view
        """View managed by this presenter"""

        self.model: Optional[Any] = model
        """Model objects which include data and buisness logic which are presented by this presenter/view"""

        # Bind keyboard shortcuts for the popup window
        # @todo - make this a method which can be overridden?
        self.view.register_keybinds({"<Control-w>": self.close_view})
        # Bind protocols for the popup window
        # @todo - make this a method which can be overridden?
        self.view.register_protocols({"WM_DELETE_WINDOW": self.close_view})

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
        self.view.lift()

    def minimise_view(self) -> None:
        """Minimise the view"""
        self.view.iconify()

    def hide_view(self) -> None:
        """Hide (withdraw) the view"""
        self.view.withdraw()

    def close_view(self, event: Optional[Any] = None) -> None:
        """Close the popup aftger performing any actions. This method should be overridden by presenters which require graceful destruction

        @todo consider if this should be an abstract method or not"""
        self.view.destroy()
        # @todo - a destroyed view object is not very useful? in which case the presenter is no longer useful either?
