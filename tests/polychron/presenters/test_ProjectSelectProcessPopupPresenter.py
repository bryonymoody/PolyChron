from __future__ import annotations

import pathlib
from unittest.mock import MagicMock, patch

import pytest

from polychron.interfaces import Mediator
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.ModelCreatePresenter import ModelCreatePresenter
from polychron.presenters.ModelSelectPresenter import ModelSelectPresenter
from polychron.presenters.ProjectCreatePresenter import ProjectCreatePresenter
from polychron.presenters.ProjectSelectPresenter import ProjectSelectPresenter
from polychron.presenters.ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter
from polychron.presenters.ProjectWelcomePresenter import ProjectWelcomePresenter
from polychron.views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView


class TestProjectSelectProcessPopupPresenter:
    """Unit tests for the ProjectSelectProcessPopupPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.

    Child Views are mocked out in an autouse fixture, with mock handles made available through instance properties
    """

    @pytest.fixture(autouse=True)
    def patch_child_views(self):
        """Patch child views which are constructed by ProjectSelectProcessPopupPresenter

        The mocks stored in self.mock_child_views are class mocks, so .return_value must be used to check if methods were called on the more recent instance of the mocked class"""

        # Note: these patch strings must match where the view is imported, not the true path to the view instance.
        # Autospec is not used her to avoid the performance impact
        with (
            patch(
                "polychron.presenters.ProjectSelectProcessPopupPresenter.ProjectWelcomeView"
            ) as mock_ProjectWelcomeView,
            patch(
                "polychron.presenters.ProjectSelectProcessPopupPresenter.ProjectSelectView"
            ) as mock_ProjectSelectView,
            patch(
                "polychron.presenters.ProjectSelectProcessPopupPresenter.ProjectCreateView"
            ) as mock_ProjectCreateView,
            patch("polychron.presenters.ProjectSelectProcessPopupPresenter.ModelSelectView") as mock_ModelSelectView,
            patch("polychron.presenters.ProjectSelectProcessPopupPresenter.ModelCreateView") as mock_ModelCreateView,
        ):
            # Store the mock class objects in a test class variable
            self.mock_child_views = (
                mock_ProjectWelcomeView,
                mock_ProjectSelectView,
                mock_ProjectCreateView,
                mock_ModelSelectView,
                mock_ModelCreateView,
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

    def test_init(self):
        """Tests the __init__ method of the ProjectSelectProcessPopupPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectProcessPopupView)
        mock_view.container = MagicMock()  # the container property is accessed directly, so must also be mocked

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectProcessPopupPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # assert child presenters are setup correctly
        assert "project_welcome" in presenter.presenters
        assert isinstance(presenter.presenters["project_welcome"], ProjectWelcomePresenter)
        assert "project_select" in presenter.presenters
        assert isinstance(presenter.presenters["project_select"], ProjectSelectPresenter)
        assert "project_create" in presenter.presenters
        assert isinstance(presenter.presenters["project_create"], ProjectCreatePresenter)
        assert "model_select" in presenter.presenters
        assert isinstance(presenter.presenters["model_select"], ModelSelectPresenter)
        assert "model_create" in presenter.presenters
        assert isinstance(presenter.presenters["model_create"], ModelCreatePresenter)

        # Assert that the initial presenter has been set
        assert presenter.current_presenter_key == "project_welcome"

        # Assert that the place_in_container method was called on instances of the mock class (via .return_value)
        for mock_child_view in self.mock_child_views:
            mock_child_view_instance = mock_child_view.return_value
            mock_child_view_instance.place_in_container.assert_called()

    def test_update_view(self):
        """Test the update view method can be called"""
        # Create mocked objects
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectProcessPopupView)
        mock_view.container = MagicMock()  # the container property is accessed directly, so must also be mocked

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectProcessPopupPresenter(mock_mediator, mock_view, model)

        # Call update_view, which should not raise
        presenter.update_view()

        # No side effects to detect

    def test_set_window_title(self):
        """Test the set window title method behaves as intended"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectProcessPopupView)
        mock_view.container = MagicMock()  # the container property is accessed directly, so must also be mocked

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectProcessPopupPresenter(mock_mediator, mock_view, model)

        # Assert the default title
        presenter.set_window_title()
        mock_view.title.assert_called_with("PolyChron loading page")

        # Assert suffix behaviour
        presenter.set_window_title(suffix="")
        mock_view.title.assert_called_with("PolyChron loading page")

        presenter.set_window_title(suffix="foo")
        mock_view.title.assert_called_with("PolyChron loading page | foo")

    def test_get_presenter(self):
        """Test that get_presenter reeturns the expected FramePresenters or None"""
        # Create mocked objects
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectProcessPopupView)
        mock_view.container = MagicMock()  # the container property is accessed directly, so must also be mocked

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectProcessPopupPresenter(mock_mediator, mock_view, model)

        # Assert that get_presenter returns expected values for valid keys
        assert isinstance(presenter.get_presenter("project_welcome"), ProjectWelcomePresenter)
        assert isinstance(presenter.get_presenter("project_select"), ProjectSelectPresenter)
        assert isinstance(presenter.get_presenter("project_create"), ProjectCreatePresenter)
        assert isinstance(presenter.get_presenter("model_select"), ModelSelectPresenter)
        assert isinstance(presenter.get_presenter("model_create"), ModelCreatePresenter)

        # Assert that get_presenter returns None for unexpected keys
        assert presenter.get_presenter("unexpected_key") is None
        assert presenter.get_presenter(None) is None

    def test_switch_presenter(self):
        """Test that switch_presenter behaves as expected for valid and invalid keys.

        Not all validkeys are checked as this is covered by other tests
        """
        # Create mocked objects
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectProcessPopupView)
        mock_view.container = MagicMock()  # the container property is accessed directly, so must also be mocked

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectProcessPopupPresenter(mock_mediator, mock_view, model)

        # Test expected values are correct for a valid key
        presenter.switch_presenter("model_create")
        assert presenter.current_presenter_key == "model_create"

        # Test an exception is raised if an invalid key is provided
        with pytest.raises(RuntimeError, match="Invalid presenter key 'unexpected_key'"):
            presenter.switch_presenter("unexpected_key")

    def test_close_window(self):
        """Assert that close_window behaves as expected"""
        # Create mocked objects
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectProcessPopupView)
        mock_view.container = MagicMock()  # the container property is accessed directly, so must also be mocked

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectProcessPopupPresenter(mock_mediator, mock_view, model)

        # no reason should just destory the view
        presenter.close_window()
        mock_mediator.switch_presenter.assert_not_called()
        mock_view.destroy.assert_called()

        # new_model should switch presenter and close the view
        presenter.close_window("new_model")
        mock_mediator.switch_presenter.assert_called_with("Model")
        mock_view.destroy.assert_called()

        # load_model should switch presenter and close the view
        presenter.close_window("load_model")
        mock_mediator.switch_presenter.assert_called_with("Model")
        mock_view.destroy.assert_called()

        # An unknown reason should raise a ValueError
        with pytest.raises(ValueError, match="Unknown reason"):
            presenter.close_window("unknown")
