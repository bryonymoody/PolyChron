import pathlib
from unittest.mock import MagicMock

import pytest

from polychron.interfaces import Mediator
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.ProjectWelcomePresenter import ProjectWelcomePresenter
from polychron.views.ProjectWelcomeView import ProjectWelcomeView


class TestProjectWelcomePresenter:
    """Unit tests for the ProjectWelcomePresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

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
        """Tests the __init__ method of the ProjectWelcomePresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectWelcomeView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectWelcomePresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that bind_load_button was called on the view, with one argument which was a callable
        mock_view.bind_load_button.assert_called_once()
        assert len(mock_view.bind_load_button.call_args.args) == 1
        assert callable(mock_view.bind_load_button.call_args.args[0])

        # Assert that bind_create_button was called on the view, with one argument which was a callable
        mock_view.bind_create_button.assert_called_once()
        assert len(mock_view.bind_create_button.call_args.args) == 1
        assert callable(mock_view.bind_create_button.call_args.args[0])

    def test_update_view(self):
        """Test the update view method can be called

        In this case it has no impact, to assert for, but must be defined.
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectWelcomeView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectWelcomePresenter(mock_mediator, mock_view, model)

        # Call update_view, which should not raise, currently no side-effects to test (noop)
        presenter.update_view()

    def test_on_load_button(self):
        """Test the on_load_button callback function"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectWelcomeView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectWelcomePresenter(mock_mediator, mock_view, model)

        # Call the on_load_button method
        presenter.on_load_button()

        # Assert that the ProjectsDirectory was lazy loaded.
        # This is currently destructive, potentially discarding data which may need changing
        assert len(presenter.model.projects_directory.projects) == 1
        assert len(presenter.model.projects_directory.get_project("foo").models) == 2

        # Assert that mediator.switch_presenter was called with the expected value
        mock_mediator.switch_presenter.assert_called_with("project_select")

    def test_on_create_button(self):
        """Test the on_create_button callback function"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectWelcomeView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectWelcomePresenter(mock_mediator, mock_view, model)

        # Call the on_create_button method
        presenter.on_create_button()

        # Assert that mediator.switch_presenter was called with the expected value
        mock_mediator.switch_presenter.assert_called_with("project_create")
