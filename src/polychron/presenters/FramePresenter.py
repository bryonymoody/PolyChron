from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from ..interfaces import Mediator
from ..views.FrameView import FrameView

# TypeVar allowing for Generic view types, which should derive from FrameView
ViewT = TypeVar("ViewT", bound=FrameView)
# TypeVar allowing for Generic model types
ModelT = TypeVar("ModelT", bound=Any)


class FramePresenter(ABC, Generic[ViewT, ModelT]):
    """Abstract Base Class for Presenters for views which are in the main window, which act as the middle man between a veiw and the underlying data structures (model)."""

    def __init__(self, mediator: Mediator, view: ViewT, model: ModelT) -> None:
        """Initialise the presenter

        Args:
            mediator (Mediator): an object which implements the Mediator protocol, i.e. the MainApp
            view (ViewT): The frame view instance to be presented
            model (ModelT): The MVP model object which includes the data to be presented and methods to manipulate it
        """

        self.mediator: Mediator = mediator
        """Reference to the parent mediator class, to enable switching between presenters/views"""

        self.view: ViewT = view
        """View managed by this presenter"""

        self.model: ModelT = model
        """Model objects which include data and buisness logic which are presented by this presenter/view"""

    @abstractmethod
    def update_view(self) -> None:
        """Update view data for the current state of the model"""
        pass

    def get_window_title_suffix(self) -> str | None:
        """Get a optional suffix for the window title, for this frame.

        Returns:
            Optional suffix for the window title when this frame is being displayed"""
        return None
