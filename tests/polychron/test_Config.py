from __future__ import annotations

import os
import pathlib
from typing import Dict
from unittest.mock import patch

import pytest
import yaml

from polychron.Config import Config, get_config


@pytest.fixture
def monkeypatch_Config_get_config_dir():
    """Locally-scoped non-default fixture which enables per-test opt-in use of the original get_config_dir behaviour.

    This overrides the autouse fixture of the same name defined in conftest.py, allowing the real get_config_dir method to be tested
    """
    return


class TestConfig:
    """Tests for the `polychron.Config` class"""

    def test_default_values(self):
        """Test the default values of the Config class are as expected"""
        c = Config()
        expected_projects_directory = pathlib.Path.home() / "Documents" / "polychron" / "projects"
        assert c.projects_directory == expected_projects_directory
        assert c.verbose is False
        assert c.geometry == "1920x1080"

    def test_load(self, tmp_path: pathlib.Path):
        """Test loading yaml from disk behaves as intended, using a temporary path probided by pathlib"""
        # Define expected data
        expected = {
            "projects_directory": str(tmp_path / "polychron_projects"),  # store as str
            "verbose": True,
            "geometry": "1280x720",
        }
        # Write to temporary path on disk.
        tmp_config_path = tmp_path / "config.yml"
        with open(tmp_config_path, "w") as tmp_config_file:
            yaml.dump(expected, tmp_config_file)

        # Call the load method
        c = Config()
        c.load(tmp_config_path)

        # Assert that values are as expected
        assert c.projects_directory == pathlib.Path(expected["projects_directory"])  # is stored as a Path in-class
        assert c.verbose == expected["verbose"]
        assert c.geometry == expected["geometry"]

    def test_save(self, tmp_path: pathlib.Path):
        """Ensure that saving a config object on disk behaves as intended"""
        # Create a Config instance to save, with non-default values
        c1 = Config(projects_directory=tmp_path / "projects", verbose=True, geometry="1280x720")
        # Build a tmp path, and ensure the file doesn't exist yet
        tmp_config_path = tmp_path / "config.yml"
        assert not tmp_config_path.exists()

        # Create the temporary file
        c1.save(tmp_config_path)

        # Ensure that a file exists at the expected location
        assert tmp_config_path.exists()
        assert tmp_config_path.is_file()

        # Check the path loads
        c2 = Config()
        c2.load(tmp_config_path)

        # Check the configuration objects match
        assert c2 == c1

    @pytest.mark.parametrize(
        ("platform_name", "env_vars", "expected_path"),
        [
            ("Linux", {}, pathlib.Path.home() / ".config/polychron"),
            ("Linux", {"XDG_CONFIG_HOME": "/foo/bar"}, pathlib.Path("/foo/bar/polychron")),
            ("Windows", {}, pathlib.Path.home() / "AppData/Local/polychron"),
            ("Windows", {"LOCALAPPDATA": "/c/foo/bar"}, pathlib.Path("/c/foo/bar/polychron")),
            # ("Darwin", {}, ".config/polychron"),
        ],
    )
    def test__get_config_dir(
        self,
        platform_name: str,
        env_vars: Dict[str, str],
        expected_path: pathlib.Path,
        monkeypatch_Config_get_config_dir,
    ):
        """Ensure that the platform and environmental variable-specific method to get the expected directory for the configuration file behaves as intended

        This method is monkeypatched by a default fixture, `monkeypatch_Config_get_config_dir` from conftestpy, but the original behaviour is restored by explicitly requesting a locally-scoped fixture with the same name

        Parameters:
            platform_name: The (mock) platform name otherwise returned by `platform.system`
            env_vars: A dictionary of environment variables. Other env vars will be discarded
            expected_path: The value which should be returned by `Config._get_config_dir()` for the parameterized `platform_name` and `env_vars`
        """
        # Patch methods:
        # - platform.system for the parameterized versions of this test
        # - environment variables to override.
        with (
            patch("polychron.Config.platform.system", return_value=platform_name),
            patch.dict(os.environ, env_vars, clear=True),
        ):
            config_dir = Config._get_config_dir()
            # It should be a path
            assert isinstance(config_dir, pathlib.Path)
            # Which matches the expected value defined in the paramaeterisation
            assert config_dir == expected_path

    def test__get_config_filepath(self):
        """Check that the get config file path method behaves as intended

        This test can be simpler, as we are can rely on test__get_config_dir for coverage"""
        filepath = Config._get_config_filepath()
        # It should be a path
        assert isinstance(filepath, pathlib.Path)
        # Which ends with the expected filename
        assert filepath.name == "config.yaml"
        # And should just be the config dir
        assert filepath.parent == Config._get_config_dir()

    def test_from_default_filepath(self, tmp_path: pathlib.Path):
        """Test the class method from_default_filepath returns a default instance if one does not exist, or one at the correct location.

        This mocks' the default file to avoid writing a file in the users home directory"""

        # Mock the config filepath
        tmp_config_file = tmp_path / "config.yaml"
        with patch("polychron.Config.Config._get_config_filepath", return_value=tmp_config_file):
            # Make sure the temp path does not exist.
            assert not tmp_config_file.exists()
            # Get the config object, ensuring it does not throw and is default.
            c = Config.from_default_filepath()
            assert c == Config()

            # Create a temporary object with non-default values
            c1 = Config(projects_directory=tmp_path / "projects", verbose=True, geometry="1280x720")
            c1.save(tmp_config_file)
            assert tmp_config_file.is_file()

            # Get the non-default file via from_default_filepath
            c = Config.from_default_filepath()
            assert c == c1


class TestGetConfig:
    """Tests for the module-scoped `polychron.get_config` method, which returns a shared instance of a Config.

    the default instance, stored in polychron.Config.__config_instance, is monkeypatched by `monkeypatch_Config__config_instance` in `tests/conftest.py` to ensure that the config singleton is never instanciated with the path in the users home directory
    """

    def test_get_config(self, tmp_path):
        """Test the get_config method always returns the same instance, which is the monkeypatched version that does not use the default projects_directory"""

        # Patch the default config filepath to a temporary file, to avoid accessing the current users config if they have one.
        tmp_config_file = tmp_path / "config.yaml"
        with patch("polychron.Config.Config._get_config_filepath", return_value=tmp_config_file):
            # Get the config instance, it should be the monkeypatched default
            c0 = get_config()
            assert c0 == Config(projects_directory=tmp_path / "projects")

            # Get the same instance again, assert they are the same object
            c1 = get_config()
            assert c1 == c0
            assert id(c1) == id(c0)

            # Mutate c0, check c1 has been updated
            old_value = c0.projects_directory
            c0.projects_directory = tmp_path / "c1"
            assert c1.projects_directory != old_value

            # Restore the old value, while this is not being fixtured
            c0.projects_directory = old_value
