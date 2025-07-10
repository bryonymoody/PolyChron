from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd


@dataclass
class DatafilePreviewModel:
    """Dataclass / MVP model containing data required for previewing a loaded datafile/csv"""

    df: pd.DataFrame
    """The datafile to preview"""

    result: Literal["load", "cancel"] = "cancel"
    """If the preview was approved or cancelled"""
