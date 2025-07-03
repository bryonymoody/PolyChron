import dataclasses
import os
import pathlib
import platform
import sys

import yaml


@dataclasses.dataclass
class Config:
    """A dataclass representing user configuration, loaded from yaml on disk."""

    projects_directory: pathlib.Path = pathlib.Path.home() / "Documents" / "polychron" / "projects"
    """Path to the projects directory for the user"""

    verbose: bool = False
    """If verbose output is enabled or not"""

    geometry: str = "1920x1080"
    """The initial window geometry"""

    def __post_init__(self) -> None:
        """Fixup member variables post initialisation

        This ensures that environment variables and ~ have been expanded in the projects_directory
        """
        if self.projects_directory is not None:
            self.projects_directory = pathlib.Path(os.path.expandvars(self.projects_directory.expanduser()))

    def load(self, path: pathlib.Path) -> None:
        """Load values from the specified path on disk"

        Parameters:
            path (pathlib.Path): The path to a yaml file where configuration should be loaded from.
        """
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
        """Save the on-disk representation of the application config to the specified path as yaml

        Parameters:
            path (pathlib.Path): The path where the file should be saved

        Note:
            - this is not comment or order preserving
            - this will save default values to disk, rather than just mutated or loaded values, which is not ideal
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
                elif isinstance(value, pathlib.Path):
                    data[field.name] = str(os.path.expandvars(value.expanduser()))
                else:
                    data[field.name] = str(value)

        # Ensure the parent exists before saving the file
        path.parent.mkdir(parents=True, exist_ok=True)

        # Attempt to save the yaml representation to disk at the specified path
        try:
            with open(path, "w") as f:
                yaml.dump(data, f, sort_keys=False)
        except (IOError, yaml.YAMLError) as e:
            print(f"Error saving configuration: {e}", file=sys.stderr)

    @classmethod
    def _get_config_dir(cls) -> pathlib.Path:
        """Gets the appropriate configuration directory based on the operating system.

        Returns:
            The platform specific configuration directory for polychron, based on common standards such as XDG on linux.
        """
        system = platform.system()
        if system == "Windows":
            from_env = os.environ.get("LOCALAPPDATA")
            user_config_dir = pathlib.Path(from_env) if from_env else pathlib.Path.home() / "AppData" / "Local"
            return user_config_dir / "polychron"
        else:
            from_env = os.environ.get("XDG_CONFIG_HOME")
            user_config_dir = pathlib.Path(from_env) if from_env else pathlib.Path.home() / ".config"
            return user_config_dir / "polychron"

    @classmethod
    def _get_config_filepath(cls) -> pathlib.Path:
        """Get the default/expected file path for the config file on disk

        Returns:
            The platform specific path to the expected configuration file location on disk
        """
        return cls._get_config_dir() / "config.yaml"

    @classmethod
    def from_default_filepath(cls) -> "Config":
        """Construct a Config instance from the default configuration file path

        Returns:
            A Config instance, populated from the config file at the platform specific location
        """
        c = Config()
        try:
            c.load(Config._get_config_filepath())
        except Exception:
            pass
        return c


# Module-scoped variable to hold a single instance of a configuration object, which can be accessed (and initialised) by calls to get_config
__config_instance: Config = None


def get_config() -> Config:
    """Get the single 'global' Configuration object instance.

    On first call, the instance will be initialised to a value from disk, based on the platform-specific default location.

    Returns:
        The single application wide Configuration object.

    Note:
        This is not thread-safe.
    """
    global __config_instance
    if __config_instance is None:
        __config_instance = Config.from_default_filepath()
    return __config_instance
