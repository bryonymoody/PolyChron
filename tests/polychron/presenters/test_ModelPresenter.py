import pathlib
import platform
from unittest.mock import MagicMock, patch

import pytest

from polychron.interfaces import Mediator
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.ModelPresenter import ModelPresenter
from polychron.views.ModelView import ModelView


class TestModelPresenter:
    """Unit tests for the ModelPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    @pytest.fixture(autouse=True)
    def setup_tmp_projects_directory(self, tmp_path: pathlib.Path):
        """Fixture to create a mock ProjectsSelection object in a temporary projects_directory

        This is scoped per test to ensure the mock projects directory is reset between tests"""

        # Store and crete a temporary projects directory
        self.tmp_projects_dir = tmp_path / "projects"
        self.tmp_projects_dir.mkdir()

        # Create a ProjectSelection object with 1 project foo, containing 1 model bar
        self.project_selection = ProjectSelection(tmp_path / "projects")
        foo = self.project_selection.projects_directory.get_or_create_project("foo")
        foo.create_model("bar")
        foo.create_model("baz")

        # Yeild control to the tests
        yield

        # post-test cleanup. tmp_path_factory automatically temporary directory/file deletion
        self.tmp_projects_dir = None
        self.project_selection = None

    @patch("polychron.presenters.ModelPresenter.ModelPresenter.update_view")
    def test_init(self, mock_update_view):
        """Tests the __init__ method of the ModelPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that the presenter properties are initialsed as expected
        assert not presenter.strat_check
        assert not presenter.date_check
        assert not presenter.phase_check
        assert not presenter.phase_rel_check
        assert presenter.node == "no node"
        assert presenter.edge_nodes == []
        assert presenter.comb_nodes == []
        assert presenter.display_data_var == "hidden"

        # Assert tab callback functions were bound
        mock_view.bind_sasd_tab_button.assert_called_once()
        assert len(mock_view.bind_sasd_tab_button.call_args.args) == 1
        assert callable(mock_view.bind_sasd_tab_button.call_args.args[0])

        mock_view.bind_dr_tab_button.assert_called_once()
        assert len(mock_view.bind_dr_tab_button.call_args.args) == 1
        assert callable(mock_view.bind_dr_tab_button.call_args.args[0])

        # Assert that menu bars were setup

        # Assert that build_file_menu was called on the view and passed the correct types of value
        mock_view.build_file_menu.assert_called_once()
        # Assert that build_file_menu was passed a list containing the expected 2 items
        assert len(mock_view.build_file_menu.call_args.args) == 1
        menu_items = mock_view.build_file_menu.call_args.args[0]
        assert isinstance(menu_items, list)
        assert len(menu_items) == 13
        for entry in menu_items:
            assert entry is None or (isinstance(entry, tuple) and len(entry) == 2 and callable(entry[1]))

        # Assert that build_view_menu was called on the view and passed the correct types of value
        mock_view.build_view_menu.assert_called_once()
        # Assert that build_view_menu was passed a list containing the expected 2 items
        assert len(mock_view.build_view_menu.call_args.args) == 1
        menu_items = mock_view.build_view_menu.call_args.args[0]
        assert isinstance(menu_items, list)
        assert len(menu_items) == 1
        for entry in menu_items:
            assert entry is None or (isinstance(entry, tuple) and len(entry) == 2 and callable(entry[1]))

        # Assert that build_tool_menu was called on the view and passed the correct types of value
        mock_view.build_tool_menu.assert_called_once()
        # Assert that build_tool_menu was passed a list containing the expected 2 items
        assert len(mock_view.build_tool_menu.call_args.args) == 1
        menu_items = mock_view.build_tool_menu.call_args.args[0]
        assert isinstance(menu_items, list)
        assert len(menu_items) == 3
        for entry in menu_items:
            assert entry is None or (isinstance(entry, tuple) and len(entry) == 2 and callable(entry[1]))

        # Assert that button callbacks were bound
        mock_view.bind_testmenu_commands.assert_called_once()
        assert len(mock_view.bind_testmenu_commands.call_args.args) == 1
        assert callable(mock_view.bind_testmenu_commands.call_args.args[0])

        # Assert that the right click menu was set up
        mock_view.bind_testmenu_commands.assert_called_once()
        assert len(mock_view.bind_testmenu_commands.call_args.args) == 1
        assert callable(mock_view.bind_testmenu_commands.call_args.args[0])

        # Assert that mouse and keyboard events were bound
        mock_view.bind_littlecanvas_callback.assert_called_once()
        assert len(mock_view.bind_littlecanvas_callback.call_args.args) == 2
        # expected button is platofrm specific
        expected_button = "<Button-3>" if platform.system() != "Darwin" else "<Button-2>"
        assert mock_view.bind_littlecanvas_callback.call_args.args[0] in expected_button
        assert callable(mock_view.bind_littlecanvas_callback.call_args.args[1])

        mock_view.bind_littlecanvas_events.assert_called_once()
        assert len(mock_view.bind_littlecanvas_events.call_args.args) == 3
        assert all([callable(x) for x in mock_view.bind_littlecanvas_events.call_args.args])

        mock_view.bind_littlecanvas2_events.assert_called_once()
        assert len(mock_view.bind_littlecanvas2_events.call_args.args) == 3
        assert all([callable(x) for x in mock_view.bind_littlecanvas2_events.call_args.args])

        # update_view should have been called.
        mock_update_view.assert_called()

    @pytest.mark.skip(reason="test_update_view not implemented")
    def test_update_view(self):
        """Tests ModelPresenter.update_view, ensuring it calls the expected method (via patching to avoid explicitly testing chronograph_render_post twice)"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Update the view
        presenter.update_view()

        # todo

    def test_get_window_title_suffix(self):
        """Test get_window_title_suffix returns None if there is no current project/model, or a valid string if one is set"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # There should be no current project or presenter, so assert get_window_title_suffix returns None
        assert presenter.model.current_project_name is None
        assert presenter.model.current_model_name is None
        assert presenter.get_window_title_suffix() is None

        # Set a (valid) current Project & Model, and assert the suffix is as expected
        model.switch_to("foo", "bar", load_ok=True, create_ok=False)
        assert presenter.get_window_title_suffix() == "foo - bar"

    @pytest.mark.skip(reason="test_Model incomplete.")
    def test_Model(self):
        pass
