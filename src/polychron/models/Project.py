import pathlib
from dataclasses import dataclass

from .Model import Model


@dataclass
class Project:
    """MVP Model representing a polychron project."""

    name: str
    """The name of the project, which is the same as the final element of the path and must be unique within the projects directory"""

    path: pathlib.Path
    """The directory representing this project on disk
    
    @todo - this and name are not both required, could have parent_path and an dynamic path? (i.e. avoid duplication during construction)
    """

    models: dict[str, Model]
    """A dictionary of models within this project, with their name as the key"""
