import sys

import pytest

from polychron.views.ModelView import ModelView


class TestModelView:
    """Tests for the ModelView.

    Note:
        Tests for `views` currently only cover importing the class and do not test the actual code.

        This is to avoid the complexities of automated GUI interaction testing, but should atleast ensure that dependencies are met.

        See https://github.com/bryonymoody/PolyChron/issues/44 for more information."""

    @pytest.mark.importable
    def test_is_importable(self):
        """Test that the ModelView class has successfully been imported, but do not attmept to actually test the class"""
        # Assert the module was loaded
        assert "polychron.views.ModelView" in sys.modules
        # Assert the specific class now exists, but do not instantiate it
        assert isinstance(ModelView, type)
