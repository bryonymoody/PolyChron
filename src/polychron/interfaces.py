from typing import Optional, Protocol


class Navigator(Protocol):
    """Interface for classes which provide methods to swtich the active view/presenter, as expected by Presenters

    This avoids a circular dependency between the GUIApp and presenters.

    @todo rename? main window specifc?

    @todo - this needs some more thought / multiple types of navigator:
    - Things which contain multiple presenters which can be switched between (GUIApp)
    - Popup windows which contain multiple presenters to switch between, or to close with the ability to handle how it is closed
    - Popup windows which can only contain a single presenter, but that can create new popup windows.
    """

    def switch_presenter(self, key: str) -> None:
        """Switch the active presenter & view by string key."""
        ...

    def close_navigator(self, reason: Optional[str] = None) -> None:
        """Gracefully close the navigator (i.e. popup window / main window)

        @param reason: A string to pass to the presenter, enabling follow on actions. @todo think of a better way to handle this control flow.

        @todo do something about making sure global application state has been updated"""
        ...
