import importlib.resources
import pathlib
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd


@dataclass
class InterpolationData:
    """Class for interpolation data used as radiocarbon dating calibration data

    Todo:
        @todo - add support for multiple calibration data sets (with a recommended default)
    """

    path: pathlib.Path = importlib.resources.files(__name__.split(".")[0]).joinpath(
        "resources/linear_interpolation.txt"
    )
    """Path to calibration data on disk. Defaults to the location of linear_interpolation.txt within the polychron package."""

    __dataframe: Optional[pd.DataFrame] = field(default=None, init=None)
    """Dataframe containing the parsed calibrationd data
    
    @todo - make this load post construction automatically?"""

    def load(self) -> None:
        """Load the dataframe from the specified path"""
        self.__dataframe = pd.read_csv(self.path)

    def get_dataframe(self) -> pd.DataFrame:
        """Get the parsed data frame, loading from disk if required"""
        if self.__dataframe is None:
            self.load()
        return self.__dataframe.copy()
