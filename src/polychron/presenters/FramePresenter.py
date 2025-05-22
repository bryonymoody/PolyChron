from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from ..interfaces import Mediator
from ..views.FrameView import FrameView

# TypeVar allowing for the Type of the model to be overidden.
T = TypeVar("T", bound=Any)


class FramePresenter(ABC, Generic[T]):
    """Abstract Base Class for Presenters for views which are in the main window, which act as the middle man between a veiw and the underlying data structures (model).

    @todo should / could this be combined with a simialr class for popup window presenters?

    @todo - use Generic and TypeVar for the tpye of the model (and of the view??). Can't use class Foo[T] as that requires 3.12+ Same in other ABCs.
    """

    def __init__(self, mediator: Mediator, view: type[FrameView], model: T) -> None:
        """Initialise the presenter

        Args:
            mediator (Mediator): an object which implements the Mediator protocol, i.e. the MainApp
            view (type[FrameView]): The frame view instance to be presented
            model (T): The MVP model object which includes the data to be presented and methods to manipulate it
        """

        self.mediator: Mediator = mediator
        """Reference to the parent mediator class, to enable switching between presenters/views"""

        self.view: type[FrameView] = view
        """View managed by this presenter"""

        self.model: T = model
        """Model objects which include data and buisness logic which are presented by this presenter/view"""

    @abstractmethod
    def update_view(self) -> None:
        """Update view data for the current state of the model

        @todo - actually do this in smaller methods?
        @todo - rename?
        """
        pass

    def get_window_title_suffix(self) -> Optional[str]:
        """Get a optional suffix for the window title, for this frame.

        Returns:
            Optional suffix for the window title when this frame is being displayed"""
        return None

    # @todo - bind abstract method which binds all callbacks?
