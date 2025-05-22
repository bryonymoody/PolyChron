import pathlib
import sys
from dataclasses import dataclass, field
from typing import Optional

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

    models: dict[str, Optional[Model]] = field(default_factory=dict)
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

    def has_model(self, name: str) -> bool:
        """Cheeck if a model exists within the project.

        @todo - should this return tuple of bools? if it exists, and if it has been loaded?"""
        return name in self.models

    def get_model(self, name: str) -> Optional[Model]:
        """Get a model from within the project, loading from disk if it has not yet been loaded"""
        if name in self.models:
            if self.models[name] is None:
                self.load_model_from_disk(name)
        return self.models.get(name, None)

    def get_or_create_model(self, name: str) -> Model:
        """Get or create a model within this Project.

        Parameters:
            name (str): The name of the model to be fetched or created

        Returns:
            The existing or new model with the specified model name

        Raises:
            @todo - document rasised exceptions

        Todo:
            @todo - Possible disk-race if files/directories are created in this model. Create model first, and if it rases the "this already exists" exception return the loaded one?
        """
        if self.has_model(name):
            model = self.get_model(name)
            if model is not None:
                return model

        # If no model was returned, create one and return it.
        self.create_model(name)

    def create_model(self, name: str) -> None:
        """Create a new model within the project, with the provided name.

        Raises:
            RuntimeError: if the model already exists or an invalid name is provided.
            OSError: if the model directories could not be created, e.g. due to permissions or avialable space.

        @todo - make checking for an existing model lighter weight than a full load?
        @todo - explicitly limit the usable model name characters to reduce the risk of os exceptions (i.e. [a-zA-Z0-9\-_]+)?) This would prevent some valid names."""

        # Attempt to load the model with the provided name.
        existing_model = self.get_model(name)
        # If the model does not exist,
        if existing_model is not None:
            raise RuntimeError(f"A model named '{name}' already exists at '{existing_model.path}'")

        # If the model does not already exist within this project, create a new model and create it's directories
        new_model = Model(name=name, path=self.path / name)

        # Detect some invalid path errors, by checking that the model name matches the model path (i.e. name="/" or ".")
        if new_model.name != new_model.path.name:
            raise RuntimeError(
                f"Model name '{name}' was converted to a non-matching directory name '{new_model.path.name}'. Please use an alternate model name"
            )
        # Attempt to create the directories, reporting an error if an invalid model name was used. Ideally this would be on first-save, but we need the temporary directory to exist.
        try:
            new_model.create_dirs()
        except OSError as e:
            raise e
        except Exception as e:
            raise e
        else:
            # If no exceptions were raised, store the model
            self.models[name] = new_model

    def lazy_load_model_from_disk(self) -> None:
        if self.path.is_dir():
            for p in self.path.iterdir():
                if p.is_dir():
                    self.models[p.name] = None

    def load_model_from_disk(self, name: str) -> None:
        """Load a single model from disk by it's name

        Paramaters:
            name: The name of the model to load.

        @todo - return value or exception of model does not exist?
        """
        import time

        try:
            start = time.monotonic()
            # Try and load the model from disk
            model_path = self.path / name
            model = Model.load_from_disk(model_path)
            # If loading succeded (no exceptions thrown) store the model
            self.models[model.name] = model
            end = time.monotonic()
            print(f"Elapsed loading model {name}: {end - start: .6f}s")
        except Exception as e:
            # @todo - correclty handle any exceptions attempting to load models
            print(f"loading exception @Todo {e}")
            raise e

    def lazy_load(self) -> None:
        """Lazily load all models from disk within this project.

        This update the models dictionary to ensure that each model which could be loaded from disk is listed as a model, without performing the (relatively) expensive disk operations. This does not guarantee the model will be loadable.

        I.e. any non-empty directory within the project directory is considered to be a model.

        @todo - decide if this should return success or raise/not raise / return the number of models?
        """
        if self.path.is_dir():
            for p in self.path.iterdir():
                if p.is_dir():
                    self.models[p.name] = None

    def load(self) -> None:
        """Load all models within this project from disk.

        @todo - decide if this should return success or raise/not raise / return the number of models?
        """
        if self.path.is_dir():
            for p in self.path.iterdir():
                if p.is_dir():
                    try:
                        self.load_model_from_disk(p.name)
                    except Exception as e:
                        raise e  # @todo
