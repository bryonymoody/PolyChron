import importlib.resources
import pathlib
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd


@dataclass
class InterpolationData:
    """Class representing/containing interpolated radiocarbon dating calibration curves

    I.e. IntCal20? using linear interpolation to fill sparser regions of the published curves.

    The dataframe will include columns:

    - `` - the row index
    - `Calendar_year`
    - `Carbon_year`
    - `Carbon_error`

    Todo:
        - @todo - rename to RCDCalibrationCurve or similar?
        - @todo - support curves directly downloaded from intcal.org?
        - @todo - document which calibration curve this is
        - @todo - remove the 0th column (index).
        - @todo - add support for multiple calibration data sets (with a recommended default), i..e IntCal20, SHCal20, Marine20 which can be selected by the user for a proejct (i.e. to support southern hemisphere)
    """

    path: pathlib.Path = importlib.resources.files(__name__.split(".")[0]).joinpath(
        "resources/linear_interpolation.txt"
    )
    """Path to calibration data on disk. Defaults to the location of linear_interpolation.txt within the polychron package."""

    __dataframe: Optional[pd.DataFrame] = field(default=None, init=None)
    """Dataframe containing the parsed calibrationd data
    
    @todo - make this load post construction automatically?"""

    def load(self) -> None:
        """Load the dataframe from the specified path

        Todo:
            Consider using engine="c" or engine="pyarrow" for faster csv reading (for all calls to read_csv)
        """
        self.__dataframe = pd.read_csv(self.path)

    def get_dataframe(self) -> pd.DataFrame:
        """Get the parsed data frame, loading from disk if required"""
        if self.__dataframe is None:
            self.load()
        return self.__dataframe.copy()
