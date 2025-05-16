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

    def load(self) -> None:
        """Load this project from disk, i.e. populate the models dictionary

        @todo - decide if this should lazy load models or not. I.e. just check for the presence of the directory and expected file(s), and have a separtate way to load a model from its path later (i.e. when the user presses load, not when they open polychron). This should reduce memory consumption.

        @todo - decide if this should return success or raise/not raise / return the number of models?
        """

        if self.path.is_dir:
            # @todo sorting?
            for item in self.path.iterdir():
                if item.is_dir():
                    try:
                        # Try and load the model from disk
                        model = Model.load_from_disk(item)
                        # If loading succeded (no exceptions thrown) store the model
                        self.models[model.name] = model
                    except Exception as e:
                        # @todo - correclty handle any exceptions attempting to load models
                        print(f"loading exception @Todo {e}")
