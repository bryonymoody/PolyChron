from typing import Protocol


class Navigator(Protocol):
    """Interface for classes which provide methods to swtich the active view/presenter, as expected by Presenters

    This avoids a circular dependency between the GUIApp and presenters.

    @todo rename? main window specifc?
    """

    def switch_presenter(self, key: str) -> None:
        """Switch the active presenter & view by string key."""
        ...

    def close_navigator(self, reason: str = None) -> None:
        """Gracefully close the navigator (i.e. popup window / main window)

        @param reason: A string to pass to the presenter, enabling follow on actions. @todo think of a better way to handle this control flow.

        @todo do something about making sure global application state has been updated"""
        ...
