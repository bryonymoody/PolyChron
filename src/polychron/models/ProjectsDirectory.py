import pathlib
from dataclasses import dataclass

from .Project import Project


@dataclass
class Project:
    """MVP Model representing the projects directory"""

    path: pathlib.Path
    """path to the projects direcotry this objet reprsents"""

    projects: dict[str, Project]
    """projects within the projects directory"""
