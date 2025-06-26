from __future__ import annotations

import pathlib
import tkinter as tk
from importlib.metadata import version
from tkinter import ttk
from unittest.mock import patch

import pytest
from ttkthemes import ThemedStyle, ThemedTk

from polychron.Config import Config
from polychron.GUIApp import GUIApp
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.DatingResultsPresenter import DatingResultsPresenter
from polychron.presenters.ModelPresenter import ModelPresenter
from polychron.presenters.SplashPresenter import SplashPresenter


class TestGUIApp:
    """Unit tests for the GUIApp class.

    This is the main class for the GUI, so is the only place which should include tkinter code outside of the views submodule, so tkinter elements also need mocking out.

    Child Views are mocked out in an autouse fixture, with mock handles made available through instance properties
    """

    @pytest.fixture(autouse=True)
    def patch_child_views(self):
        """Patch child views which are constructed by GUIApp

        The mocks stored in self.mock_child_views are class mocks, so .return_value must be used to check if methods were called on the more recent instance of the mocked class"""

        # Note: these patch strings must match where the view is imported, not the true path to the view instance.
        # Autospec is not used her to avoid the performance impact
        with (
            patch("polychron.GUIApp.SplashView") as mock_SplashView,
            patch("polychron.GUIApp.ModelView") as mock_ModelView,
            patch("polychron.GUIApp.DatingResultsView") as mock_DatingResultsView,
        ):
            # Store the mock class objects in a test class variable
            self.mock_child_views = (
                mock_SplashView,
                mock_ModelView,
                mock_DatingResultsView,
            )
            yield
            self.mock_child_views = None

    @pytest.fixture(autouse=True)
    def setup_tmp_projects_directory(self, tmp_path: pathlib.Path):
        """Fixture to create a mock projects directory and ProjectSelection instance

        This is scoped per test to ensure the mock projects directory is reset between tests"""

        # Store and crete a temporary projects directory
        self.tmp_projects_dir = tmp_path / "projects"
        self.tmp_projects_dir.mkdir()

        # Create a ProjectSelection object with a single project containing 2 models.
        self.project_selection = ProjectSelection(tmp_path / "projects")
        foo = self.project_selection.projects_directory.get_or_create_project("foo")
        foo.create_model("bar")
        foo.create_model("baz")

        # Yield control to the tests
        yield

        # post-test cleanup. tmp_path_factory automatically temporary directory/file deletion
        self.tmp_projects_dir = None
        self.project_selection = None

    @pytest.fixture(autouse=True)
    def patch_config(self, setup_tmp_projects_directory, tmp_path: pathlib.Path):
        """Patch out get_config to always return a fresh instance, rather than the real instance"""
        with patch(
            "polychron.GUIApp.get_config", return_value=Config(projects_directory=self.tmp_projects_dir)
        ) as mock_get_config:
            self.mock_get_config = mock_get_config
            yield
            self.mock_get_config = None

    @pytest.fixture(autouse=True)
    def patch_tkinter(self):
        """Patch out ttk.style and ThemedStyle to check they were called"""
        with (
            patch("polychron.GUIApp.ThemedStyle", autospec=ThemedStyle) as mock_ThemedStyle,
            patch("polychron.GUIApp.ttk.Style", spec=ttk.Style) as mock_ttk_Style,
        ):
            self.mock_ThemedStyle = mock_ThemedStyle
            self.mock_ttk_Style = mock_ttk_Style
            yield
            self.mock_ThemedStyle = None
            self.mock_ttk_Style = None

    def test_init(self):
        """Tests the __init__ method of the GUIApp class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Instantiate the Presenter
        app = GUIApp()

        # Assert that presenter attributes are set as intended
        assert app.config == self.mock_get_config.return_value
        assert isinstance(app.root, ThemedTk)

        # Assert that styling was mutated
        self.mock_ThemedStyle.assert_called()
        self.mock_ttk_Style.assert_called()

        # Todo: Assert that set_window_title, resize_window, register_global_keybinds, register_protocols were called

        # Assert that the container was set up
        assert isinstance(app.container, tk.Frame)

        # Assert the ProjectSelection object is set up and is using the path from the mocked config instance (i.e a temporary projects directory)
        assert isinstance(app.project_selector_obj, ProjectSelection)
        assert app.project_selector_obj.projects_directory.path == self.tmp_projects_dir

        # assert child presenters are setup correctly
        assert "Splash" in app.presenters
        assert isinstance(app.presenters["Splash"], SplashPresenter)
        assert "Model" in app.presenters
        assert isinstance(app.presenters["Model"], ModelPresenter)
        assert "DatingResults" in app.presenters
        assert isinstance(app.presenters["DatingResults"], DatingResultsPresenter)

        # Assert that the initial presenter has been set
        assert app.current_presenter_key == "Splash"

        # Assert that the place_in_container method was called on instances of the mock class (via .return_value)
        for mock_child_view in self.mock_child_views:
            mock_child_view_instance = mock_child_view.return_value
            mock_child_view_instance.place_in_container.assert_called()

    def test_set_window_title(self):
        """Test the set window title method behaves as intended, by patching ThemedTk.title"""
        app = GUIApp()

        expected_base_title = f"PolyChron {version('polychron')}"

        # Patch out .title so we can check it was called as expected
        with patch("polychron.GUIApp.ThemedTk.title") as mock_root_title:
            # Assert the default title
            app.set_window_title()
            mock_root_title.assert_called_with(expected_base_title)

            # Assert suffix behaviour
            app.set_window_title(suffix="")
            mock_root_title.assert_called_with(f"{expected_base_title}")

            app.set_window_title(suffix="foo")
            mock_root_title.assert_called_with(f"{expected_base_title} | foo")

    def test_get_presenter(self):
        """Test that get_presenter reeturns the expected FramePresenters or None"""
        app = GUIApp()

        # Assert that get_presenter returns expected values for valid keys
        assert isinstance(app.get_presenter("Splash"), SplashPresenter)
        assert isinstance(app.get_presenter("Model"), ModelPresenter)
        assert isinstance(app.get_presenter("DatingResults"), DatingResultsPresenter)

        # Assert that get_presenter returns None for unexpected keys
        assert app.get_presenter("unexpected_key") is None
        assert app.get_presenter(None) is None

    def test_switch_presenter(self):
        """Test that switch_presenter behaves as expected for valid and invalid keys.

        Not all valid keys are checked as this is covered by other tests
        """
        app = GUIApp()

        # Test expected values are correct for a valid key
        assert app.current_presenter_key != "Model"
        app.switch_presenter("Model")
        assert app.current_presenter_key == "Model"

        # Test an exception is raised if an invalid key is provided
        with pytest.raises(RuntimeError, match="Invalid presenter key 'unexpected_key'"):
            app.switch_presenter("unexpected_key")

    def test_close_window(self):
        """Assert that close_window behaves as expected"""
        app = GUIApp()

        # patch out ThemedTK.quit to ensure we can detect it would have been called
        with patch("polychron.GUIApp.ThemedTk.quit") as mock_root_quit:
            # no reason should just quit the tkinter app
            app.close_window()
            mock_root_quit.assert_called()
            mock_root_quit.reset_mock()

            # Reasons can be provided, but currently there is no reason specific behaviour
            app.close_window("unknown")
            mock_root_quit.assert_called()
            mock_root_quit.reset_mock()

    @pytest.mark.skip(reason="test_GUIApp not fully implemented")
    def test_register_global_keybinds(self):
        """Assert that close_window behaves as expected"""
        app = GUIApp()
        app.register_global_keybinds()
