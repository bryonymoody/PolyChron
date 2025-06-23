import pathlib
from unittest.mock import MagicMock, patch

import pytest

from polychron.Config import Config
from polychron.interfaces import Mediator
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.CalibrateModelSelectPresenter import CalibrateModelSelectPresenter
from polychron.views.CalibrateModelSelectView import CalibrateModelSelectView


class TestCalibrateModelSelectPresenter:
    """Unit tests for the CalibrateModelSelectPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    @pytest.fixture(autouse=True)
    def setup_tmp_projects_directory(self, tmp_path: pathlib.Path):
        """Fixture to create a mock projects directory

        This is scoped per test to ensure the mock projects directory is reset between tests"""

        # Store and crete a temporary projects directory
        self.tmp_projects_dir = tmp_path / "projects"
        self.tmp_projects_dir.mkdir()

        # Create a ProjectSelection object with a single project containig 2 models.
        self.project_selection = ProjectSelection(tmp_path / "projects")
        foo = self.project_selection.projects_directory.get_or_create_project("foo")
        foo.create_model("bar")
        foo.create_model("baz")

        # Yeild control to the tests
        yield

        # post-test cleanup. tmp_path_factory automatically temporary directory/file deletion
        self.tmp_projects_dir = None
        self.project_selection = None

    def test_init(self):
        """Tests the __init__ method of the CalibrateModelSelectPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=CalibrateModelSelectView)

        # Get the ProjectSelection model object provided by the fixture
        model = self.project_selection

        # Instantiate the Presenter
        presenter = CalibrateModelSelectPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that bind_ok_button was called on the view, and provided a single callable argument
        mock_view.bind_ok_button.assert_called_once()
        args, _ = mock_view.bind_ok_button.call_args
        assert len(args) == 1
        assert callable(args[0])

        # Assert that bind_select_all_button was called on the view, and provided a single callable argument
        mock_view.bind_select_all_button.assert_called_once()
        args, _ = mock_view.bind_select_all_button.call_args
        assert len(args) == 1
        assert callable(args[0])

    def test_update_view(self):
        """Test that update_view calls appropriate methods on the view with expected data"""

        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=CalibrateModelSelectView)

        # Get the ProjectSelection model object provided by the fixture
        model = self.project_selection

        # Instantiate the Presenter
        presenter = CalibrateModelSelectPresenter(mock_mediator, mock_view, model)

        # Call the method to be tested, and Assert that view.update_model_list was most recently called with an empty list, as the mock projects directory does not have an active project
        presenter.update_view()
        mock_view.update_model_list.assert_called_with([])

        # set the current project, and expect that it was still not called with any data
        model.current_project_name = "foo"
        presenter.update_view()
        mock_view.update_model_list.assert_called_with([])

        # Mark some models as being ready for simulation, and assert their names were provided
        model.current_project.get_model("bar").load_check = True
        model.current_project.get_model("baz").load_check = True
        presenter.update_view()
        mock_view.update_model_list.assert_called_with(["bar", "baz"])

    @patch("polychron.presenters.CalibrateModelSelectPresenter.get_config", return_value=Config())
    def test_on_ok_button(self, mock_get_config):
        """Test that the on_ok button callback would call Model.MCMC_func and call save methods, using mocking to avoid requiring a fully populated Model instance, if atleast one model was selected from the dropdown

        Patches out get_config to not mutate global state"""

        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=CalibrateModelSelectView)

        # Get the ProjectSelection model object provided by the fixture
        model = self.project_selection

        # Instantiate the Presenter
        presenter = CalibrateModelSelectPresenter(mock_mediator, mock_view, model)

        # Call on_ok_button when the current project is not valid, which should just call the parents close view (which has been mocked out)
        with patch(
            "polychron.presenters.CalibrateModelSelectPresenter.CalibrateModelSelectPresenter.close_view"
        ) as mock_close_view:
            presenter.on_ok_button()
            mock_close_view.assert_called_once()

        # Call on_ok_button with a current project specified. This should just calls close_view
        model.current_project_name = "foo"
        with patch(
            "polychron.presenters.CalibrateModelSelectPresenter.CalibrateModelSelectPresenter.close_view"
        ) as mock_close_view:
            presenter.on_ok_button()
            mock_close_view.assert_called_once()

        # Call on_ok_button with a current project and models marked as ready for mcmc (via load_check)
        # Mocks out model.MCMC_func, which should have been called once per load_check model which was mocked as returned by the method
        # mcmc_check should now be True
        # Mocks out MCMCData.save, which should have been called
        # Mocks out Model.save which should have been called
        # Mocks out close_view, which should have been called once
        model.current_project.get_model("bar").load_check = True
        model.current_project.get_model("baz").load_check = True

        # Ensure that the mocked view returns the loaded models for get_selected_models
        mock_view.get_selected_models.return_value = ["bar", "baz"]
        with (
            patch(
                "polychron.presenters.CalibrateModelSelectPresenter.CalibrateModelSelectPresenter.close_view"
            ) as mock_close_view,
            patch("polychron.models.Model.Model.MCMC_func") as mock_model_mcmc_func,
            patch("polychron.models.Model.Model.save") as mock_model_save,
            patch("polychron.models.MCMCData.MCMCData.save") as mock_mcmcdata_save,
        ):
            # Ensure that the mock Model.MCMC_func method returns a tuple of 10 elements of the correct types
            mock_model_mcmc_func.return_value = tuple([[], [], [], [], 12, 12, [], [], {}, {}])

            # Call the on_ok_button method
            presenter.on_ok_button()

            # Assert that MCMC_func should have been called twice
            assert mock_model_mcmc_func.call_count == 2
            # Assert that the mcmc_check property of both models is now True
            assert model.current_project.get_model("bar").mcmc_check
            assert model.current_project.get_model("baz").mcmc_check
            # Assert that the save methods were called
            assert mock_model_save.call_count == 2
            assert mock_mcmcdata_save.call_count == 2
            # Assert that the view should have been closed
            mock_close_view.assert_called_once()

    def test_on_select_all(self):
        """Test the on_select_all callback, which should just call a method on the view which is mocked out"""

        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=CalibrateModelSelectView)

        # Get the ProjectSelection model object provided by the fixture
        model = self.project_selection

        # Instantiate the Presenter
        presenter = CalibrateModelSelectPresenter(mock_mediator, mock_view, model)

        # Call the method
        presenter.on_select_all()

        # Assert that CalibrateModelSelectView.select_all_models was called
        mock_view.select_all_models.assert_called_once()
