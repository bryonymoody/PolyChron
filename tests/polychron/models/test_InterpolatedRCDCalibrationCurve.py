from __future__ import annotations

from polychron.models.InterpolatedRCDCalibrationCurve import InterpolatedRCDCalibrationCurve


class TestInterpolatedRCDCalibrationCurve:
    """Unit Tests for the class representing interpolated radio carbon dating calibration curves"""

    def test_default_values(self):
        """Test the default values of an IRCDCC instance"""
        instance = InterpolatedRCDCalibrationCurve()
        # Assert the path is defined and ends in "resources/linear_interpolation.txt"
        assert instance.path.name == "linear_interpolation.txt"
        assert instance.path.parent.name == "resources"
        # Assert the default path file exists
        assert instance.path.is_file()

        # Assert the dataframe is initially None
        assert instance._InterpolatedRCDCalibrationCurve__dataframe is None

    def test_load(self):
        """Test that the load method behaves as intended

        This accesses private members which is not ideal but acceptable for a test."""
        instance = InterpolatedRCDCalibrationCurve()
        assert instance._InterpolatedRCDCalibrationCurve__dataframe is None
        instance.load()
        assert instance._InterpolatedRCDCalibrationCurve__dataframe is not None
        assert len(instance._InterpolatedRCDCalibrationCurve__dataframe) > 0

    def test_df(self):
        """Test accessing the dataframe behaves as intended"""
        instance = InterpolatedRCDCalibrationCurve()
        # When accessed through the property, if the df had not been loaded it is loaded before being returned.
        assert instance.df is not None
        assert len(instance.df) > 0

    def test_default_df_data(self):
        """Test that the dataframe contains the expected columns, for the default dataframe"""
        instance = InterpolatedRCDCalibrationCurve()
        df = instance.df
        # There should be 4 columns
        assert len(df.columns) == 4
        # Check the expected column names are all present
        assert "Calendar_year" in df.columns
        assert "Carbon_year" in df.columns
        assert "Carbon_error" in df.columns
        # Assert there should be 55001 rows [0, 55000] inclusive
        assert len(df) == 55001
