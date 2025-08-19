from __future__ import annotations

import importlib.resources
import pathlib
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class InterpolatedRCDCalibrationCurve:
    """Class containing an interpolated radiocarbon dating calibration curve

    An intcal.org calibration curve, linearly interpolated to fill sparser regions of the published curves.

    The dataframe will include columns:

    - `` - the row index
    - `Calendar_year`
    - `Carbon_year`
    - `Carbon_error`
    """

    curve_name: str

    __dataframe: pd.DataFrame | None = field(default=None, init=False)

    @property
    def path(self) -> pathlib.Path:
        """Path to the calibration curve CSV based on the selected curve name."""
        return importlib.resources.files(__name__.split(".")[0]).joinpath(f"resources/{self.curve_name}.csv")

    def load(self) -> None:
        """Load the calibration data from disk into a DataFrame."""
        self.__dataframe = pd.read_csv(self.path, sep=",")

    @property
    def df(self) -> pd.DataFrame:
        """Get the calibration data as a DataFrame (loaded on first access)."""
        if self.__dataframe is None:
            self.load()
        return self.__dataframe.copy()

    @classmethod
    def load_from_csv(cls, csv_path: str | pathlib.Path) -> InterpolatedRCDCalibrationCurve:
        """
        Create an InterpolatedRCDCalibrationCurve instance directly from a CSV file path.

        This bypasses the internal name-to-path resolution and lets you load arbitrary CSVs.
        """
        csv_path = pathlib.Path(csv_path)
        curve_name = csv_path.stem  # file name without extension
        instance = cls(curve_name)
        instance.__dataframe = pd.read_csv(csv_path)
        return instance
