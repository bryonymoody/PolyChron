from typing import Protocol


class Navigator(Protocol):
    """Interface for classes which provide methods to swtich the active view/presenter, as expected by Presenters

    This avoids a circular dependency between the GUIApp and presenters.

    @todo rename? main window specifc?
    """

    def switch_main_presenter(self, key: str) -> None:
        """Switch the active presenter & view by string key."""
        ...
