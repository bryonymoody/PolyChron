import pandas as pd
import pytest

from polychron.models.DatafilePreviewModel import DatafilePreviewModel


class TestDatafilePreviewModel:
    """Unit Tests for the `models.DatafilePreviewModel` class which contains a datafile to preview"""

    def test_init(self):
        """Test the constructor default values and explicit setting of initial values"""
        obj = DatafilePreviewModel(pd.DataFrame())
        pd.testing.assert_frame_equal(obj.df, pd.DataFrame())
        assert obj.result == "cancel"

        obj = DatafilePreviewModel(pd.DataFrame(), "load")
        pd.testing.assert_frame_equal(obj.df, pd.DataFrame())
        assert obj.result == "load"

        # Assert that an excetpion is raised if no arguments provided
        with pytest.raises(TypeError):
            obj = DatafilePreviewModel()

    def test_df(self):
        """Test getting and setting the context"""
        obj = DatafilePreviewModel(pd.DataFrame())
        pd.testing.assert_frame_equal(obj.df, pd.DataFrame())

        obj.df = pd.DataFrame({"foo": ["a", "b"], "bar": [1, 2]})
        pd.testing.assert_frame_equal(obj.df, pd.DataFrame({"foo": ["a", "b"], "bar": [1, 2]}))

    def test_result(self):
        """Test getting and setting the result"""
        obj = DatafilePreviewModel(pd.DataFrame())
        assert obj.result == "cancel"

        obj.result = "load"
        assert obj.result == "load"
