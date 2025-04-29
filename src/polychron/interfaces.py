from typing import TYPE_CHECKING, Optional, Protocol, Union

# Avoid circular dependencies but provide type hints
if TYPE_CHECKING:
    from .presenters.BaseFramePresenter import BaseFramePresenter
    from .presenters.BasePopupPresenter import BasePopupPresenter


class Mediator(Protocol):
    """Interface for classes which provide methods to swtich the active view/presenter, as expected by Presenters

    This avoids a circular dependency between the GUIApp and presenters.

    @todo Split into Frame, Popup and maybe PopupFrame verisons which extend one another?
        - Things which contain multiple presenters which can be switched between (GUIApp)
        - Popup windows which contain multiple presenters to switch between, or to close with the ability to handle how it is closed
        - Popup windows which can only contain a single presenter, but that can create new popup windows.

    @todo Consider adding popups here? Should maybe be a presenter thing though.
    """

    def switch_presenter(self, key: Optional[str]) -> None:
        """Switch the active presenter & view by string key."""
        ...

    def get_presenter(self, key: Optional[str]) -> Optional[Union["BaseFramePresenter", "BasePopupPresenter"]]:
        """Get a presenter by it's Key, if it valid"""
        ...

    def close_window(self, reason: Optional[str] = None) -> None:
        """Gracefully close any windows this meadiator is in charge of.

        @param reason: A string to pass to the presenter, enabling follow on actions. @todo think of a better way to handle this control flow.
        """
        ...
