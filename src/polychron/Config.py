import dataclasses
import os
import pathlib
import platform
import sys

import yaml


@dataclasses.dataclass
class Config:
    """A dataclass representing user configuration
    
    Todo:
        @todo - handle relative user provided paths (and home/env vars here?) via @property and @projects_directory.setter? although ideally a save would not include the expansion"""

    projects_directory: pathlib.Path = pathlib.Path.home() / "Documents" / "polychron" / "projects"
    """Value on disk for the users projects directory, which defaults to the value provided by get_default_projects_directory"""

    verbose: bool = False
    """If verbose output is enabled or not"""

    geometry: str = "1920x1080"
    """The initial window geometry"""

    def load(self, path: pathlib.Path) -> None:
        """Load values from the specified path on disk"""
        if path.is_file():
            try:
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
                    if data:
                        for field in dataclasses.fields(self):
                            if field.name in data:
                                setattr(self, field.name, field.type(data[field.name]))
            except (yaml.YAMLError, FileNotFoundError, TypeError) as e:
                print(f"Error loading configuration: {e}", file=sys.stderr)

    def save(self, path: pathlib.Path) -> None:
        """Save the on-disk representation of the application config to the specified path

        note: this is not comment or order preserving
        note: this will save default values to disk, rather than just mutated or loaded values, which is not ideal. @todo
        """

        # Ensure the target file is not an existing directory
        if path.is_dir():
            print(f"Unable to load Config from '{path}', it is a directory", file=sys.stderr)
            return

        # Construct a dictionary representing this configuration object.
        data = {}
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if value is not None:
                if isinstance(value, (str, int, float)):
                    data[field.name] = value
                else:
                    data[field.name] = str(value)

        # Ensure the parent exists before saving the file
        # @todo - this should probably be made more safe?
        path.parent.mkdir(parents=True, exist_ok=True)
        # Attempt to save the yaml represenation to disk at the specified path
        try:
            with open(path, "w") as f:
                yaml.dump(data, f, sort_keys=False)
        except (IOError, yaml.YAMLError) as e:
            print(f"Error saving configuration: {e}", file=sys.stderr)

    @classmethod
    def _get_config_dir(cls) -> pathlib.Path:
        """Gets the appropriate configuration directory based on the operating system."""
        system = platform.system()
        if system == "Windows":
            return pathlib.Path(os.environ.get("LOCALAPPDATA", pathlib.Path.home() / "AppData" / "Local")) / "polychron"
        else:
            return pathlib.Path(os.environ.get("XDG_CONFIG_HOME", pathlib.Path.home() / ".config")) / "polychron"

    @classmethod
    def _get_config_filepath(cls) -> pathlib.Path:
        """Get the default/expected file path for the config file on disk"""
        return cls._get_config_dir() / "config.yaml"

    @classmethod
    def from_default_filepath(cls) -> "Config":
        """Construct a Config instance from the default configuration file path"""
        c = Config()
        try:
            c.load(Config._get_config_filepath())
        except Exception:
            pass
        return c


# Module-scoped variable to hold a single instance of a configuration object, which can be accessed (and initialied) by calls to get_config
__config_instance: Config = None


def get_config() -> Config:
    """Get the single 'global' Configuraiton object instance.

    On first call, the instance will be initialised to a value from disk, based on the platform-specific default location.

    Returns:
        The single application wide Configuraiton object.

    Note:
        This is not thread-safe.
    """
    global __config_instance
    if __config_instance is None:
        __config_instance = Config.from_default_filepath()
    return __config_instance
