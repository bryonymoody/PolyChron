import pathlib
import sys
from dataclasses import dataclass, field

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

    models: dict[str, Model] = field(default_factory=dict)
    """A dictionary of models within this project, with their name as the key"""

    def create_dirs(self) -> bool:
        """Create the project directory.

        Returns:
            Boolean indicating success of directory creation
        """
        try:
            # Ensure the model (and implictly project) directory exists
            self.path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # @todo - better error handling. Should be due to permsissions, invalid filepaths or disk issues only
            print(e, file=sys.stderr)
            return False
