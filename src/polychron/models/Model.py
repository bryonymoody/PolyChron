from dataclasses import dataclass
import pathlib


@dataclass
class Model:
    """MVP Model representing a polychron model."""

    name: str
    """The name of the model within the project (unique)"""

    path: pathlib.Path
    """The path to the directory representing this model on disk"""
