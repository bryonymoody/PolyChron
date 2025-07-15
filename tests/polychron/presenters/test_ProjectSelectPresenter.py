import pathlib
from unittest.mock import MagicMock

import pytest

from polychron.interfaces import Mediator
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.ProjectSelectPresenter import ProjectSelectPresenter
from polychron.views.ProjectSelectView import ProjectSelectView


class TestProjectSelectPresenter:
    """Unit tests for the ProjectSelectPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    @pytest.fixture(autouse=True)
    def setup_tmp_projects_directory(self, tmp_path: pathlib.Path):
        """Fixture to create a mock projects directory and ProjectSelection instance

        This is scoped per test to ensure the mock projects directory is reset between tests"""

        # Store and crete a temporary projects directory
        self.tmp_projects_dir = tmp_path / "projects"
        self.tmp_projects_dir.mkdir(exist_ok=True, parents=True)

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
        """Tests the __init__ method of the ProjectSelectPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that bind_load_button was called on the view, with one argument which was a callable
        mock_view.bind_load_button.assert_called_once()
        assert len(mock_view.bind_load_button.call_args.args) == 1
        assert callable(mock_view.bind_load_button.call_args.args[0])

        # Assert that bind_back_button was called on the view, with one argument which was a callable
        mock_view.bind_back_button.assert_called_once()
        assert len(mock_view.bind_back_button.call_args.args) == 1
        assert callable(mock_view.bind_back_button.call_args.args[0])

        # Assert that view.update_project_list was called (within the include call to update_view)
        mock_view.update_project_list.assert_called_with(["foo"])

    def test_update_view(self):
        """Test the update view method can be called"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectPresenter(mock_mediator, mock_view, model)

        # Call update_view, which should not raise
        presenter.update_view()

        # Assert the mocked view.update_project_list method was called with the expected value
        mock_view.update_project_list.assert_called_with(["foo"])

        # Create a new project, which should be displayed before "foo" in a sorted list, and assert the order is sorted lexicographically
        self.project_selection.projects_directory.get_or_create_project("1")
        presenter.update_view()
        mock_view.update_project_list.assert_called_with(["1", "foo"])

    def test_on_load_button(self, capsys: pytest.CaptureFixture):
        """Test the on_load_button callback function

        This mocks out view.get_selected_project to return either a valid project name, an invalid project name, or None
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectPresenter(mock_mediator, mock_view, model)

        # Mock out the view.get_selected_project method to return an expected value
        project_name = "foo"
        mock_view.get_selected_project.return_value = project_name

        # Call the on_load_button method
        presenter.on_load_button()

        # Assert that the model has been updated to set the next presenter name
        assert presenter.model.next_project_name == project_name

        # Assert that mediator.switch_presenter was called with the expected value
        mock_mediator.switch_presenter.assert_called_with("model_select")
        mock_mediator.reset_mock()

        # ---

        # Mock out the view.get_selected_project method to return an unexpected value.
        # This behaviour may be worth changing to only allow setting to a valid project and report the error
        project_name = ""
        mock_view.get_selected_project.return_value = project_name

        # Call the on_load_button method
        presenter.on_load_button()

        # Assert that the model has been updated to set the next presenter name
        assert presenter.model.next_project_name == project_name

        # Assert that mediator.switch_presenter was called with the expected value
        mock_mediator.switch_presenter.assert_called_with("model_select")
        mock_mediator.reset_mock()

        # ---

        # Mock out the view.get_selected_project method to return None,
        project_name = None
        mock_view.get_selected_project.return_value = project_name

        # Clear capture output
        capsys.readouterr()

        # Call the on_load_button method
        presenter.on_load_button()

        # Assert that the model has been updated to set the next presenter name to None
        assert presenter.model.next_project_name is None

        # Assert that something was emitted to stderr
        captured = capsys.readouterr()
        assert len(captured.err) > 0

        # Assert that mediator.switch_presenter was not called
        mock_mediator.switch_presenter.assert_not_called()
        mock_mediator.reset_mock()

    def test_on_back_button(self):
        """Test the on_back_button callback function"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ProjectSelectView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ProjectSelectPresenter(mock_mediator, mock_view, model)

        # Call the on_back_button method
        presenter.on_back_button()

        # Assert that the next_project_name was cleared
        assert presenter.model.next_project_name is None

        # Assert that mediator.switch_presenter was called with the expected value
        mock_mediator.switch_presenter.assert_called_with("project_welcome")
