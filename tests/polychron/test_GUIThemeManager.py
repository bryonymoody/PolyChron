from __future__ import annotations

import tkinter.font as tkFont

import pytest
from ttkthemes import ThemedTk

from polychron.GUIThemeManager import GUIThemeManager


class TestGUIThemeManager:
    """Test the GUIThemeManager class which is where tkinter theming is modified, and a single source of truth for UI fonts"""

    def test_init(self, capsys: pytest.CaptureFixture):
        """Test the contructor sets properties as expected and mutates tkinter defaults. This requires a root window."""

        root = ThemedTk()
        root.withdraw()

        # Not verbose by default
        capsys.readouterr()
        obj = GUIThemeManager(root)
        # Check there was no output to stderr/stdout
        captured = capsys.readouterr()
        assert len(captured.out) == 0
        assert len(captured.err) == 0

        # Assert there is a private __font_family attribute
        assert obj._GUIThemeManager__font_family == "helvetica"

        # Assert that the default TkDefaultFont has been conifgured
        tk_default_font = tkFont.nametofont("TkDefaultFont")
        assert tk_default_font.cget("family") == obj._GUIThemeManager__font_family

        # with verbose output enabled, check there was some stdout output
        capsys.readouterr()
        obj = GUIThemeManager(root, verbose=True)
        # Check there was no output to stderr/stdout
        captured = capsys.readouterr()
        assert len(captured.out) != 0
        assert len(captured.err) == 0

    def test_font(self):
        """Test getting a Font object behaves as intended, using the configured font and the provided size/weight"""
        # Prepare a withdrawn window
        root = ThemedTk()
        root.withdraw()
        # construct the GUIThemeManager object
        obj = GUIThemeManager(root)

        # Get a font with just a size provided
        f = obj.font(12)
        assert isinstance(f, tkFont.Font)
        assert f.cget("family") == obj._GUIThemeManager__font_family
        assert f.cget("size") == 12
        assert f.cget("weight") == "normal"

        # Get a font with a weight provided
        f = obj.font(24, weight="normal")
        assert isinstance(f, tkFont.Font)
        assert f.cget("family") == obj._GUIThemeManager__font_family
        assert f.cget("size") == 24
        assert f.cget("weight") == "normal"

        # Get a font with a bold weight provided
        f = obj.font(32, weight="bold")
        assert isinstance(f, tkFont.Font)
        assert f.cget("family") == obj._GUIThemeManager__font_family
        assert f.cget("size") == 32
        assert f.cget("weight") == "bold"

    def test_colour(self):
        """Test colours from the theme pallette can be fetched, and that the pallette is defined"""

        # Ensure the pallette is a dictionary and contains atleast one element
        assert isinstance(GUIThemeManager.COLOURS, dict)
        assert len(GUIThemeManager.COLOURS) > 0

        # Check getting a missing value returns the default colour
        assert GUIThemeManager.colour("") == "#000000"

        # Check getting a defined colour behaves
        assert "secondary" in GUIThemeManager.COLOURS
        assert GUIThemeManager.colour("secondary") == "#CC5F00"

        # Todo: Assert that all expected colour names are present (but don't check for exact values, that's probably over fitting the test
        assert "primary" in GUIThemeManager.COLOURS
        # ...

        # Check it can also be accessed via an instance
        # Prepare a withdrawn window
        root = ThemedTk()
        root.withdraw()
        # construct the GUIThemeManager object
        obj = GUIThemeManager(root)
        assert obj.colour("") == "#000000"
        assert obj.colour("secondary") == "#CC5F00"

    def test___actual_font_family(self):
        """Test getting the actually used font family returns a string.

        We cannot check the exact value as we don't know what fonts are installed on the user running the tests system."""

        # Prepare a withdrawn window
        root = ThemedTk()
        root.withdraw()
        # construct the GUIThemeManager object
        obj = GUIThemeManager(root)

        # Get the actual font family
        actual = obj._GUIThemeManager__actual_font_family()
        assert isinstance(actual, str)
