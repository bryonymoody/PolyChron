from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from ..interfaces import Mediator
from ..views.PopupView import PopupView

# TypeVar allowing for Generic view types, which should derive from PopupView
ViewT = TypeVar("ViewT", bound=PopupView)
# TypeVar allowing for Generic model types
ModelT = TypeVar("ModelT", bound=Any)


class PopupPresenter(ABC, Generic[ViewT, ModelT]):
    """Abstract Base Class for Presenters for views which are in the main window, which act as the middle man between a veiw and the underlying data structures (model)."""

    def __init__(self, mediator: Mediator, view: ViewT, model: ModelT) -> None:
        """Initialise the presenter

        Args:
            mediator (Mediator): An object which implements the Mediator protocol
            view (ViewT): The popup view instance to be presented
            model (ModelT): The MVP model object which includes the data to be presented and methods to manipulate it
        """

        self.mediator: Mediator = mediator
        """Reference to the parent mediator class, to enable switching between presenters/views"""

        self.view: ViewT = view
        """View managed by this presenter"""

        self.model: ModelT = model
        """The MVP model object which includes the data to be presented and methods to manipulate it"""

        # Bind keyboard shortcuts for the popup window
        self.view.register_keybinds({"<Control-w>": lambda _: self.close_view()})
        # Bind protocols for the popup window
        self.view.register_protocols({"WM_DELETE_WINDOW": lambda: self.close_view()})

    @abstractmethod
    def update_view(self) -> None:
        """Update view data for the current state of the model"""
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
        """Close the popup aftger performing any actions.

        This method should be overridden by presenters which require graceful destruction or wish to disable window closing."""
        self.view.destroy()
