import pathlib
from dataclasses import dataclass


@dataclass
class Model:
    """MVP Model representing a polychron model."""

    name: str
    """The name of the model within the project (unique)"""

    path: pathlib.Path
    """The path to the directory representing this model on disk
    
    @todo - this and name are not both required, could have parent_path and an dynamic path? (i.e. avoid duplication during construction). Or even require path to be proivided for save() and load()
    """

    def save(self):
        """Save the current state of this model to disk at self.path"""
        print(f"@todo - Model.save({self.path})")
