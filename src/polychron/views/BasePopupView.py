import tkinter as tk
from typing import Any, Callable, Dict, Optional


class BasePopupView(tk.Toplevel):
    """Base class for Views exist within their own popup window

    @todo - base this on tkk.Toplevel for better theming, but needs changes to extending classes

    @todo - should this contain a Toplevel rahter than extend one? I.e. prevent tkinter leaking out of the view
    """

    def __init__(self, parent: tk.Toplevel) -> None:
        """Call the base class (Toplevel) constructor"""
        # Call the tk.Toplevel's constructor providing the parent/master element
        super().__init__(parent)

        self.parent = parent
        """A reference to the parent frame"""

    def register_keybinds(self, bindings: Dict[str, Callable[[], Optional[Any]]]) -> None:
        """Register window-wide key bindings"""
        for sequence, callback in bindings.items():
            self.bind(sequence, callback)

    def register_protocols(self, bindings: Dict[str, Callable[[], Optional[Any]]]) -> None:
        """Register protocols with the window

        i.e. what happens when the window is closed using the OS decorations"""
        for name, callback in bindings.items():
            self.protocol(name, callback)
