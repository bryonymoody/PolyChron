from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from ..interfaces import Mediator
from ..views.PopupView import PopupView

# TypeVar allowing for the Type of the model to be overidden.
T = TypeVar("T", bound=Any)


class PopupPresenter(ABC, Generic[T]):
    """Abstract Base Class for Presenters for views which are in the main window, which act as the middle man between a veiw and the underlying data structures (model).

    @todo common base class with FramePresenter?
    """

    def __init__(self, mediator: Mediator, view: type[PopupView], model: T) -> None:
        """Initialise the presenter

        Args:
            mediator (Mediator): An object which implements the Mediator protocol
            view (type[PopupView]): The popup view instance to be presented
            model (T): The MVP model object which includes the data to be presented and methods to manipulate it
        """

        self.mediator: Mediator = mediator
        """Reference to the parent mediator class, to enable switching between presenters/views"""

        self.view: type[PopupView] = view
        """View managed by this presenter"""

        self.model: T = model
        """The MVP model object which includes the data to be presented and methods to manipulate it"""

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

        @todo consider if this should be an abstract method or not
        """
        self.view.destroy()
        # @todo - a destroyed view object is not very useful? in which case the presenter is no longer useful either?
