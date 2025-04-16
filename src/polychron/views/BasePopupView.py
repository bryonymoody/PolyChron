import tkinter as tk

class BasePopupView(tk.Toplevel):
    """Base class for Views exist within their own popup window
    
    @todo - base this on tkk.Toplevel for better theming, but needs changes to extending classes

    @todo - make this more complex
    """

    def __init__(self, parent: tk.Toplevel):
        """Call the base class (Toplevel) constructor"""
        # Call the tk.Toplevel's constructor providing the parent/master element
        super().__init__(parent)
        
        self.parent = parent
        """A reference to the parent frame"""

