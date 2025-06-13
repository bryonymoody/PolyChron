from typing import TYPE_CHECKING, Optional, Protocol, Union

# Avoid circular dependencies but provide type hints
if TYPE_CHECKING:
    from .presenters.FramePresenter import FramePresenter
    from .presenters.PopupPresenter import PopupPresenter


class Mediator(Protocol):
    """Interface for classes which provide methods to swtich the active view/presenter, as expected by Presenters

    This avoids a circular dependency between the GUIApp and presenters."""

    def switch_presenter(self, key: Optional[str]) -> None:
        """Switch the active presenter & view by string key.

        Parameters:
            key: The key of the presenter to switch to"""
        ...

    def get_presenter(self, key: Optional[str]) -> Optional[Union["FramePresenter", "PopupPresenter"]]:
        """Get a presenter by it's Key, if it valid

        Parameters:
            key: The key of the presenter to fetch

        Returns:
            The FramePresenter or PopupPresenter to be switchted to, or None
        """
        ...

    def close_window(self, reason: Optional[str] = None) -> None:
        """Gracefully close any windows this meadiator is in charge of.

        Parameters:
            reason (str): A string to pass to the presenter, enabling follow on actions.
        """
        ...
