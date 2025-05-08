from abc import ABC, abstractmethod
from typing import Any, Optional

from ..interfaces import Mediator
from ..views.BaseFrameView import BaseFrameView


class BaseFramePresenter(ABC):
    """Abstract Base class for Presenters for views which are in the main window, which act as the middle man between a veiw and the underlying data structures (model).

    @todo should / could this be combined with a simialr class for popup window presenters?

    @todo rename, Base is superflous.
    """

    def __init__(self, mediator: Mediator, view: type[BaseFrameView], model: Optional[Any] = None) -> None:
        """Initialise the presenter

        Args:
            mediator (Mediator): an object which implements the Mediator protocol, i.e. the MainApp
            view (type[BaseFrameView]): The view instance to be presented
            model (Optional[Any]): Model objects which include data and buiseness logic
        """

        self.mediator: Mediator = mediator
        """Reference to the parent mediator class, to enable switching between presenters/views"""

        self.view: type[BaseFrameView] = view
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
