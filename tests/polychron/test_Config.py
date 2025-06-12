import os
import pathlib
import platform

import pytest

from polychron.Config import Config


class TestConfig:
    def test_default_values(self):
        c = Config()
        expected_projects_directory = pathlib.Path.home() / "Documents" / "polychron" / "projects"
        assert c.projects_directory == expected_projects_directory

    @pytest.mark.skip(reason="test not implemented")
    def test_load(self):
        pass

    @pytest.mark.skip(reason="test not implemented")
    def test_save(self):
        pass

    def test__get_config_dir(self):
        config_dir = Config._get_config_dir()
        # It should be a path
        assert isinstance(config_dir, pathlib.Path)
        # And starts with something else depending on the platform.
        if platform.system() == "Windows":
            if "LOCALAPPDATA" in os.environ:
                pytest.skip("Test not fully implemented")
            else:
                pytest.skip("Test not fully implemented")
        else:
            if "XDG_CONFIG_HOME" in os.environ:
                pytest.skip("Test not fully implemented")
            else:
                assert config_dir == pathlib.Path.home() / ".config" / "polychron"

    def test__get_config_filepath(self):
        filepath = Config._get_config_filepath()
        # It should be a path
        assert isinstance(filepath, pathlib.Path)
        # Which ends with the expected filename
        assert filepath.name == "config.yaml"
        # And should just be the config dir
        assert filepath.parent == Config._get_config_dir()
