from __future__ import annotations

import tkinter.font as tkFont

from ttkthemes import ThemedTk


class GUIThemeManager:
    """Class for the style of UI elements, including colours and fonts.

    This should be constructed and owned by the GUIApp, and provided to `views` for use (where views cannot just use a ttk style.)
    """

    COLOURS: dict[str, str] = {
        # The main UI colours for backgrounds and text
        "background_white": "#FFFFFF",
        "background_offwhite": "#FCFDFD",
        # The polychron primary colour (blue) and variants
        "primary": "#33658a",
        "primary_light": "#AEC7D6",
        "primary_dark": "#2F4858",
        # The polychron secondary colour (orange) and variants
        "secondary": "#CC5F00",
        "secondary_light": "#FFE9D6",
        "secondary_dark": "#8F4300",
        # Colour used for the histograms
        "histogram": "#0504aa",
        # Other colours
        "slate_grey": "#2F4858",
        "offwhite2": "#EFF3F6",
        "submit_orange": "#EC9949",
        "back_white": "#DCDCDC",
    }
    """A dictionary of named colours to be used throughout polychron, to avoid repeated use of hex codes as string literals."""

    def __init__(self, root: ThemedTk, verbose: bool = False):
        """Initialise the GUIThemeManager instance, setting up fonts, ttk styles and internal state

        This is one of the only class/file which should import tkinter / ThemedTK other than View classes

        Parameters:
            root: The root window which themes are conifgured for.
            verbose: If verbose output is enabled, printing the actual font
        """

        self.__font_family = "helvetica"
        """The font family to use. if the requested font is not available, tkinter should use fc-match and similar to request a compatible font, which can be checked by `tkFont.Font.actual`"""

        # If verbose output was enabled, print the requested and actually used fonts
        if verbose:
            print(f"GUIThemeManager: Requested font '{self.__font_family}', using '{self.__actual_font_family()}'")

        # Modify the TKDefaultFont to use the requested font
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family=self.__font_family, size=12, weight="bold")

        # set the default font option for tkinter Menu elements, including when add_command is used.
        root.option_add("*Menu.font", (self.__font_family, 12, "bold"))

        # Get and modify the ThemedStyle to change the defaults for ttk elements, and define some additional custom styles.
        # Using ttkthemes and arc, custom button background colours are non trivial, so tk.Button are stil used.
        # style = ThemedStyle(root)

        # Define a custom ttk.label style for listbox titles, used in the project selection process.
        # style.configure(
        #     "ListboxTitle.TLabel",
        #     background="white",
        #     foreground=GUIThemeManager.colour("slate_grey"),
        #     font=(self.__font_family, 14, "bold"),
        # )

    def font(self, size: int, weight: str = "normal") -> tkFont.Font:
        """Get a TKFont instance with the speficified size and optional weight, using the 'default' font.

        Parameters:
            size: The size of font int points if positive, pixels if negative
            weight: the font weight (NORMAL or BOLD)
        """
        return tkFont.Font(family=self.__font_family, size=size, weight=weight)

    @classmethod
    def colour(self, name: str) -> str:
        """Get a polychron theme colour by it's name

        Parameters:
            name: the named colour to retrieve

        Returns:
            an RGB hex code for the requested theme colour. If the name is not valid, a default value of #000000 is returned
        """
        return self.COLOURS.get(name, "#000000")

    def __actual_font_family(self) -> str:
        """Return the resolved font, for the requested font family"""
        return tkFont.Font(family=self.__font_family).actual().get("family", "")
