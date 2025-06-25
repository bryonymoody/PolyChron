from __future__ import annotations

import pathlib
from typing import List, Literal
from unittest.mock import MagicMock

import pytest

from polychron.interfaces import Mediator
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.ModelSelectPresenter import ModelSelectPresenter
from polychron.views.ModelSelectView import ModelSelectView


class TestModelSelectPresenter:
    """Unit tests for the ModelSelectPresenter class.

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
        """Tests the __init__ method of the ModelSelectPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelSelectView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelSelectPresenter(mock_mediator, mock_view, model)

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

        # Assert that bind_create_model_button was called on the view, with one argument which was a callable
        mock_view.bind_create_model_button.assert_called_once()
        assert len(mock_view.bind_create_model_button.call_args.args) == 1
        assert callable(mock_view.bind_create_model_button.call_args.args[0])

        # Assert that update_view was called, by checking it's side effects
        mock_view.update_model_list.assert_called_once()

    @pytest.mark.parametrize(
        ("next_project_name", "expected_model_names"),
        [
            ("foo", ["bar", "baz"]),
        ],
    )
    def test_update_view(self, next_project_name: str | None, expected_model_names: List[str]):
        """Test the update view method can be called"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelSelectView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelSelectPresenter(mock_mediator, mock_view, model)

        # Set the next_project_name value
        presenter.model.next_project_name = next_project_name

        # Call update_view, which should not raise
        presenter.update_view()

        # Assert that the model list was updated in the view with the expected list of model names
        mock_view.update_model_list.assert_called_with(expected_model_names)

    @pytest.mark.parametrize(
        ("next_project_name", "get_selected_model", "outcome"),
        [
            ("foo", "foo", "error"),  # Err: new model in existing project
            ("bar", "bar", "error"),  # Err: new model in new project
            ("foo", "bar", "success"),  # OK: Existing model in existing proj
            ("foo", ".", "error"),  # Err: invalid model name
            (None, "foo", "error"),  # Err: No next project, popup
            ("foo", None, "stderr"),  # Err: invalid selected_model, stderr
            ("foo", "", "stderr"),  # Err: empty selected_model, stderr
        ],
    )
    def test_on_load_button(
        self,
        next_project_name: str | None,
        get_selected_model: str | None,
        outcome: Literal["success", "error", "stderr"],
        capsys: pytest.CaptureFixture,
    ):
        """Test the on_load_button callback function, with different parameter sets

        This mocks out view.get_selected_model to return either a valid model name, an invalid model name, or None

        Todo:
            - Test this method with a wider array of new model names.
            - Potentially validate the existence of a matching model already at this stage (if an existing project)
            - Validate that a next project is already selected?
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelSelectView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelSelectPresenter(mock_mediator, mock_view, model)
        model.next_project_name = next_project_name

        # Mock out the view.get_selected_model to return a parametrised value
        mock_view.get_selected_model.return_value = get_selected_model

        # Call the on_load_button method
        presenter.on_load_button()

        # Capture stdout/stderr
        captured = capsys.readouterr()

        if outcome == "success":
            # Assert that the model has been switched to the next presenter/model
            assert presenter.model.current_project_name == next_project_name
            assert presenter.model.current_model_name == get_selected_model
            assert presenter.model.next_project_name is None
            assert presenter.model.next_model_name is None
            # Assert that an errorbox was not raised
            mock_view.messagebox_error.assert_not_called()
            # Assert that mediator.close_window was called with the expected value
            mock_mediator.close_window.assert_called_with("load_model")
            # Assert that stderr did not have content
            assert len(captured.err) == 0
        elif outcome == "error":
            # Assert the current_project/model has not been updated, but the attempted next_model_name is correct
            assert presenter.model.current_project_name is None
            assert presenter.model.current_model_name is None
            assert presenter.model.next_project_name == next_project_name
            assert presenter.model.next_model_name == get_selected_model
            # Assert that an error box was raised
            mock_view.messagebox_error.assert_called()
            # Assert that the window was not closed
            mock_mediator.close_window.assert_not_called()
            # Assert that stderr did not have content
            assert len(captured.err) == 0
        elif outcome == "stderr":
            # Assert the current_project/model has not been updated, but the attempted next_model_name is correct
            assert presenter.model.current_project_name is None
            assert presenter.model.current_model_name is None
            assert presenter.model.next_project_name == next_project_name
            assert presenter.model.next_model_name is None
            # Assert that an error box was not raised
            mock_view.messagebox_error.assert_not_called()
            # Assert that the window was not closed
            mock_mediator.close_window.assert_not_called()
            # Assert that stderr had content
            assert len(captured.err) > 0
        else:
            # This should not happen / is a bad test parametrisation
            pytest.fail("Invalid 'outcome' parameter for test_on_load_button")

    @pytest.mark.parametrize(
        ("next_project_name", "expected_switch_presenter"),
        [
            ("foo", "project_select"),
            ("does_not_exist", "project_welcome"),
            (None, "project_welcome"),
        ],
    )
    def test_on_back_button(self, next_project_name: str | None, expected_switch_presenter: str):
        """Test the on_back_button callback function"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelSelectView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelSelectPresenter(mock_mediator, mock_view, model)

        # Set the next_project_name, to test different outcomes
        presenter.model.next_project_name = next_project_name

        # Call the on_back_button method
        presenter.on_back_button()

        # Assert that the next_model_name was cleared
        assert presenter.model.next_model_name is None

        # Assert that mediator.switch_presenter was called with the expected value
        mock_mediator.switch_presenter.assert_called_with(expected_switch_presenter)

    def test_on_create_model_button(self):
        """Test the on_create_model_button callback function"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelSelectView)

        # Get an actual model instance of the correct type
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelSelectPresenter(mock_mediator, mock_view, model)

        # Call the on_create_model_button method
        presenter.on_create_model_button()

        # Assert that mediator.switch_presenter was called with the expected value
        mock_mediator.switch_presenter.assert_called_with("model_create")
