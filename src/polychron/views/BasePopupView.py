import tkinter as tk
from typing import Any, Callable, Dict, Optional


class BasePopupView(tk.Toplevel):
    """Base class for Views exist within their own popup window

    @todo - base this on tkk.Toplevel for better theming, but needs changes to extending classes

    @todo - should this contain a Toplevel rahter than extend one? I.e. prevent tkinter leaking out of the view

    @todo - make this more complex

    @todo - start visisble=False breaks winfo_width/height until it has been made visible, but without it the window placement is not centered over the parent, so will need to provide +x+y to geometry strings, computed relateive to the root window (parent may be a tkframe, though maybe it should be enforced as a topLevel (or have parent and parentTL))
    """

    def __init__(self, parent: tk.Toplevel, start_visible=False):
        """Call the base class (Toplevel) constructor"""
        # Call the tk.Toplevel's constructor providing the parent/master element
        super().__init__(parent)

        self.parent = parent
        """A reference to the parent frame"""

        # Start with the view hidden
        if not start_visible:
            # withdraw to hide, deiconify to show, iconify to show minimised
            self.withdraw()
        else:
            # Otherwise try to make sure it is on top
            self.lift()

        # @todo - optionall prevent the parent window from being used while the popup is open.
        # useing grab_set() and wait_window(self) can lead to unclosable windows if not careful

    def register_keybinds(self, bindings: Dict[str, Callable[[], Optional[Any]]]):
        """Register window-wide key bindings"""
        for sequence, callback in bindings.items():
            self.bind(sequence, callback)

    def register_protocols(self, bindings: Dict[str, Callable[[], Optional[Any]]]):
        """Register protocols with the window

        i.e. what happens when the window is closed using the OS decorations"""
        for name, callback in bindings.items():
            self.protocol(name, callback)
