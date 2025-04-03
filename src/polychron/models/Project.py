from dataclasses import dataclass
import pathlib
from .Model import Model

@dataclass
class Project:
    """MVP Model representing a polychron project."""

    name: str
    """The name of the project, which is the same as the final element of the path and must be unique within the projects directory"""

    path: pathlib.Path
    """The direcotry repreenting this project on disk"""

    models: dict[str, Model]
    """A dictionary of models within this project, with their name as the key"""

