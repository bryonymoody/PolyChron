from typing import Optional, Protocol


class Mediator(Protocol):
    """Interface for classes which provide methods to swtich the active view/presenter, as expected by Presenters

    This avoids a circular dependency between the GUIApp and presenters.

    @todo - add a get_presenter() method, and switch_presenter overload which takes a Presenter. This will allow a presenter to pass data to another presenter (for model updating)

    @todo Split into Frame, Popup and maybe PopupFrame verisons which extend one another?
    - Things which contain multiple presenters which can be switched between (GUIApp)
    - Popup windows which contain multiple presenters to switch between, or to close with the ability to handle how it is closed
    - Popup windows which can only contain a single presenter, but that can create new popup windows.

    @todo Consider adding popups here? Should maybe be a presenter thing though.

    """

    def switch_presenter(self, key: str) -> None:
        """Switch the active presenter & view by string key."""
        ...

    def close_window(self, reason: Optional[str] = None) -> None:
        """Gracefully close any windows this meadiator is in charge of.

        @param reason: A string to pass to the presenter, enabling follow on actions. @todo think of a better way to handle this control flow.
        """
        ...
