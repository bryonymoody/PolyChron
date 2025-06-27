from __future__ import annotations

import pathlib
import tkinter as tk
from importlib.metadata import version
from tkinter import ttk
from unittest.mock import MagicMock, patch

import pytest
from ttkthemes import ThemedStyle, ThemedTk

from polychron.Config import Config
from polychron.GUIApp import GUIApp
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.DatingResultsPresenter import DatingResultsPresenter
from polychron.presenters.ModelPresenter import ModelPresenter
from polychron.presenters.ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter
from polychron.presenters.SplashPresenter import SplashPresenter
from polychron.views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView


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

    def test_register_global_keybinds(self):
        """Test that register_global_keybinds behaves as expected"""
        app = GUIApp()

        # Patch out ThemedTk.bind and check it was called with the expected values
        with patch("polychron.GUIApp.ThemedTk.bind") as mock_root_bind:
            app.register_global_keybinds()
            mock_root_bind.assert_called_once()
            assert len(mock_root_bind.call_args.args) == 2
            assert mock_root_bind.call_args.args[0] == "<Control-w>"
            assert callable(mock_root_bind.call_args.args[1])

    def test_register_protocols(self):
        """Test that register_protocols behaves as expected"""
        app = GUIApp()

        # Patch out ThemedTk.protocol and check it was called with the expected values
        with patch("polychron.GUIApp.ThemedTk.protocol") as mock_root_protocol:
            app.register_protocols()
            mock_root_protocol.assert_called_once()
            assert len(mock_root_protocol.call_args.args) == 2
            assert mock_root_protocol.call_args.args[0] == "WM_DELETE_WINDOW"
            assert callable(mock_root_protocol.call_args.args[1])

    def test_save_current_model(self):
        """Test that save_current_model behaves as expected"""
        app = GUIApp()

        # Patch out Model.save and check it was called
        with patch("polychron.models.Model.Model.save") as mock_model_save:
            print(mock_model_save)
            # Call with a default state app, which should not call the save method.
            app.save_current_model()
            mock_model_save.assert_not_called()
            mock_model_save.reset_mock()

            # Being on thee Model or DatingResults presenter but without a valid model should not trigger a save
            app.switch_presenter("Model")
            assert app.project_selector_obj.current_model is None
            # Call save_current_model
            app.save_current_model()
            # Assert Model.save was not called
            mock_model_save.assert_not_called()
            mock_model_save.reset_mock()

            app.switch_presenter("DatingResults")
            assert app.project_selector_obj.current_model is None
            # Call save_current_model
            app.save_current_model()
            # Assert Model.save was not called
            mock_model_save.assert_not_called()
            mock_model_save.reset_mock()

            # Switch to the Model presenter, and select a valid model which should trigger save
            app.switch_presenter("Model")
            app.project_selector_obj.next_project_name = "foo"
            app.project_selector_obj.next_model_name = "bar"
            app.project_selector_obj.switch_to_next_project_model()
            # Call save_current_model
            app.save_current_model()
            # Assert Model.save was called
            mock_model_save.assert_called()
            mock_model_save.reset_mock()

            # Switch to the DatingResults presenter, and select a valid model which should trigger save
            app.switch_presenter("DatingResults")
            app.project_selector_obj.next_project_name = "foo"
            app.project_selector_obj.next_model_name = "bar"
            app.project_selector_obj.switch_to_next_project_model()
            # Call save_current_model
            app.save_current_model()
            # Assert Model.save was called
            mock_model_save.assert_called()
            mock_model_save.reset_mock()

    def test_exit_application(self):
        """Test that exit_application behaves as expected"""
        app = GUIApp()

        # patch out ThemedTK.quit to ensure we can detect it would have been called
        with patch("polychron.GUIApp.ThemedTk.quit") as mock_root_quit:
            # no event should just quit the tkinter app
            app.exit_application()
            mock_root_quit.assert_called()
            mock_root_quit.reset_mock()

            # Also takes an optional event, but it does not alter behaviour
            app.exit_application(None)
            mock_root_quit.assert_called()
            mock_root_quit.reset_mock()

    @pytest.mark.parametrize(
        ("input_str", "expected_geometry_arg"),
        [
            ("1280x720", "1280x720"),  # Smaller than screen
            ("1920x1080", "1920x1080"),  # Same as screen
            ("10000x10000", "1920x1080"),  # bigger than screen
            ("-1280x-720", None),  # negative, does nothing
            ("1280", None),  # single value, does nothing
            ("axb", None),  # not digits, does nothing
            ("", None),  # empty string, does nothing
            ("1280x720+0+0", None),  # with positioning, currently does nothing but should be supported
        ],
    )
    def test_resize_window(self, input_str: str, expected_geometry_arg: str | None):
        """Test that the resize window is valid for multiple geometry strings.

        This mocks out the winfo_screenwidth and winfo_screenheight to ensure that test behaviour is consistent"""
        app = GUIApp()

        # patch out winfo_screenwidth & winfo_screenheight for test consistency, and ThemedTK.geometry to ensure we can detect it would have been called
        with (
            patch("polychron.GUIApp.ThemedTk.winfo_screenwidth") as mock_screenwidth,
            patch("polychron.GUIApp.ThemedTk.winfo_screenheight") as mock_screenheight,
            patch("polychron.GUIApp.ThemedTk.geometry") as mock_root_geometry,
        ):
            # Set the return values for mocked screen width and height
            mock_screenwidth.return_value = 1920
            mock_screenheight.return_value = 1080

            # Test with the parametrized value
            app.resize_window(input_str)
            # If the expected value is not None, check it was passed to the mock geometry method
            if expected_geometry_arg is not None:
                mock_root_geometry.assert_called_with(expected_geometry_arg)
            else:
                # Otherwise, assert that .geometry() was not called
                mock_root_geometry.assert_not_called()

    @pytest.mark.parametrize(
        (
            "project_name",
            "model_name",
            "expected_child_presenter_switch",
            "expected_child_presenter_close",
            "expect_stderr",
        ),
        [
            ("foo", "bar", None, "load_model", False),  # existing project and model
            ("foo", "new", None, "new_model", False),  # existing project, new model
            ("new", "new", None, "new_model", False),  # new project, new model
            ("new", None, "model_create", None, False),  # new project, no model
            ("foo", None, "model_select", None, False),  # existing project, no model
            (None, None, None, None, False),  # no project or model
            ("foo", ".", None, None, True),  # valid project, invalid model name
            # (".", "foo", None, None, True),  # Invalid project, valid model name
        ],
    )
    @patch("polychron.GUIApp.ProjectSelectProcessPopupPresenter")
    @patch("polychron.GUIApp.ProjectSelectProcessPopupView")
    def test_launch(
        self,
        MockProjectSelectProcessPopupView,
        MockProjectSelectProcessPopupPresenter,
        project_name: str | None,
        model_name: str | None,
        expected_child_presenter_switch: str | None,
        expected_child_presenter_close: str | None,
        expect_stderr: bool,
        capsys: pytest.CaptureFixture,
    ):
        """Test launch behaves as expected, mocking out methods which would trigger side effects to ensure the correct paths are taken.

        Todo:
            - Ensure that invalid project names are correctly handled
        """
        app = GUIApp()

        # Prepare the Mocked child/popup View
        mock_child_view_instance = MagicMock(spec=ProjectSelectProcessPopupView)
        MockProjectSelectProcessPopupView.return_value = mock_child_view_instance
        # Prepare the Mocked child/popup Presenter, including explicit setting of a mocked view member
        mock_child_presenter_instance = MagicMock(spec=ProjectSelectProcessPopupPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockProjectSelectProcessPopupPresenter.return_value = mock_child_presenter_instance

        # Mock out root.mainloop()
        with patch("polychron.GUIApp.ThemedTk.mainloop") as mock_root_mainloop:
            capsys.readouterr()
            # Call launch
            app.launch(project_name, model_name)

            # Check if stderr was printed to or not
            captured = capsys.readouterr()
            if expect_stderr:
                assert len(captured.err) > 0
            else:
                assert len(captured.err) == 0

            # Todo: Assert that the lazy_load method was called

            # Assert the child presenter was instantiated
            MockProjectSelectProcessPopupView.assert_called_once()
            MockProjectSelectProcessPopupPresenter.assert_called_once()

            # Assert that switch_presenter was called on the mock child_presenter instance with the expected value, if expected
            if expected_child_presenter_switch is not None:
                mock_child_presenter_instance.switch_presenter.assert_called_with(expected_child_presenter_switch)
            else:
                mock_child_presenter_instance.switch_presenter.assert_not_called()

            # If the popup was expected to be closed, ensure that it was with an expected value.
            if expected_child_presenter_close is not None:
                mock_child_presenter_instance.close_window.assert_called_with(expected_child_presenter_close)
            else:
                mock_child_presenter_instance.close_window.assert_not_called()

            # Assert that the project_selector_obj is in the correct state

            # If the project name was not provided, or invalid so expecting stderr, current and next should be None
            if project_name is None or expect_stderr:
                assert app.project_selector_obj.current_project_name is None
                assert app.project_selector_obj.current_model_name is None
                assert app.project_selector_obj.next_project_name is None
                assert app.project_selector_obj.next_model_name is None
            # Otherwise if we have a project name but no model name, only the next_project_name should be set
            elif project_name is not None and model_name is None:
                assert app.project_selector_obj.current_project_name is None
                assert app.project_selector_obj.current_model_name is None
                assert app.project_selector_obj.next_project_name is project_name
                assert app.project_selector_obj.next_model_name is None
            # Otherwise if we have a project name and a model name, the current project should be set
            elif project_name is not None and model_name is not None:
                assert app.project_selector_obj.current_project_name == project_name
                assert app.project_selector_obj.current_model_name == model_name
                assert app.project_selector_obj.next_project_name is None
                assert app.project_selector_obj.next_model_name is None

            # Assert the render loop should have been started
            mock_root_mainloop.assert_called_once()
