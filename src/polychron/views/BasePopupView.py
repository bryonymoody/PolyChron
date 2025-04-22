import tkinter as tk
from typing import Any, Optional


class BasePopupView(tk.Toplevel):
    """Base class for Views exist within their own popup window

    @todo - base this on tkk.Toplevel for better theming, but needs changes to extending classes

    @todo - should this contain a Toplevel rahter than extend one? I.e. prevent tkinter leaking out of the view

    @todo - make this more complex
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

        # Add a keybind for closing the popupwindow, with a method to gracefully handle it.
        # @todo - should these be replaced with bind mehtods, which are then called by the presenter providing the callback?
        self.register_popup_keybinds()
        self.register_protocols()

    def register_popup_keybinds(self):
        """Register application-wide key bindings

        @todo - check if this needs to be a lambda to support overriding the called mothod"""
        # ctrl+w to close the window @todo this might need changing for sub-windows..
        self.bind("<Control-w>", self.close_popup)

    def register_protocols(self):
        """Register protocols with the root window - i.e. what to do on (graceful) application exit"""
        self.protocol("WM_DELETE_WINDOW", self.close_popup)

    def close_popup(self, event: Optional[Any] = None) -> None:
        """Callback function for graceful application exit via keybind or window manager close."""
        # @todo - add any exit behaviour here
        # Quit the root window
        self.destroy()
