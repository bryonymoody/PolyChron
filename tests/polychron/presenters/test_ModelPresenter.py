from __future__ import annotations

import math
import pathlib
import platform
from unittest.mock import MagicMock, patch

import networkx as nx
import packaging
import pandas as pd
import pytest
from networkx.drawing.nx_pydot import write_dot

from polychron.interfaces import Mediator
from polychron.models.Model import Model
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.DatafilePreviewPresenter import DatafilePreviewPresenter
from polychron.presenters.MCMCProgressPresenter import MCMCProgressPresenter
from polychron.presenters.ModelPresenter import ModelPresenter
from polychron.presenters.ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter
from polychron.presenters.RemoveContextPresenter import RemoveContextPresenter
from polychron.presenters.RemoveStratigraphicRelationshipPresenter import RemoveStratigraphicRelationshipPresenter
from polychron.util import remove_invalid_attributes_networkx_lt_3_4
from polychron.views.DatafilePreviewView import DatafilePreviewView
from polychron.views.MCMCProgressView import MCMCProgressView
from polychron.views.ModelView import ModelView
from polychron.views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from polychron.views.RemoveContextView import RemoveContextView
from polychron.views.RemoveStratigraphicRelationshipView import RemoveStratigraphicRelationshipView


class TestModelPresenter:
    """Unit tests for the ModelPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    @pytest.fixture(autouse=True)
    def setup_tmp_projects_directory(self, tmp_path: pathlib.Path, test_data_model_demo: Model):
        """Fixture to create a mock ProjectsSelection object in a temporary projects_directory

        This is scoped per test to ensure the mock projects directory is reset between tests"""

        # Store and crete a temporary projects directory
        self.tmp_projects_dir = tmp_path / "projects"
        self.tmp_projects_dir.mkdir(exist_ok=True, parents=True)

        # Create a ProjectSelection object with 1 project foo, containing 1 model bar
        self.project_selection = ProjectSelection(tmp_path / "projects")
        foo = self.project_selection.projects_directory.get_or_create_project("foo")
        foo.create_model("bar")
        foo.create_model("baz")

        demo = self.project_selection.projects_directory.get_or_create_project("demo")
        demo.models["demo"] = test_data_model_demo

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

    def test_update_view(self):
        """Tests ModelPresenter.update_view, ensuring it calls the expected methods

        Todo:
            - Test with multiple Models in different states to get full branch coverage.
            - Should update_view call set_deleted_nodes/set_deleted_edges even if there are none?
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)
        # Reset the view mock
        mock_view.reset_mock()

        # Update the view when no current model is selected
        assert presenter.model.current_model is None
        presenter.update_view()
        # This should have not called any view methods
        assert len(mock_view.mock_calls) == 0

        # Reset the view mock
        mock_view.reset_mock()

        # ---

        # Specify a model, and assert that data has been updated accordingly after calling update_view
        presenter.model.switch_to("empty", "empty")
        presenter.update_view()
        assert presenter.model.current_model is not None
        m: Model = presenter.model.current_model

        # The empty model should only has a name and a path, most view methods should not have been called.
        assert m.stratigraphic_df is None
        assert m.stratigraphic_image is None
        mock_view.update_littlecanvas.assert_not_called()
        mock_view.bind_littlecanvas_callback.assert_not_called()

        # if the model has a chrono_dag, it should have been rendered and 3 view methods should have been called
        assert m.chronological_dag is None
        assert m.chronological_image is None
        mock_view.update_littlecanvas.assert_not_called()
        mock_view.bind_littlecanvas_callback.assert_not_called()
        mock_view.show_image2.assert_not_called()

        # _check variables should still all be false
        assert not presenter.strat_check
        assert not presenter.date_check
        assert not presenter.phase_check
        assert not presenter.phase_rel_check

        # there should have been no deleted nodes or edges, so no need to update
        mock_view.set_deleted_nodes.assert_not_called()
        mock_view.set_deleted_edges.assert_not_called()

        # ---

        # For a more-complete model, more view methoids should have been triggered.
        presenter.model.switch_to("foo", "bar")
        assert presenter.model.current_model is not None
        m: Model = presenter.model.current_model

        # add some deleted nodes/edges
        m.record_deleted_node("foo", "reason")
        m.record_deleted_edge("foo", "bar", "reason")

        presenter.update_view()

        # @todo

        # # If the model has a strat df, 3 view methods should have been called.
        # assert m.stratigraphic_df is not None
        # assert m.stratigraphic_image is not None
        # mock_view.update_littlecanvas.assert_called_with(m.stratigraphic_image)
        # mock_view.bind_littlecanvas_callback.assert_called()
        # assert mock_view.bind_littlecanvas_callback.call_count == 2

        # # if the model has a chrono_dag, it should have been rendered and 3 view methods should have been called
        # assert m.chronological_dag is not None
        # assert m.chronological_image is not None
        # mock_view.update_littlecanvas.assert_called_with(m.chronological_image)
        # mock_view.bind_littlecanvas_callback.assert_called()
        # mock_view.show_image2.assert_called()

        # # _check variables should still all be false
        # assert presenter.strat_check
        # assert presenter.date_check
        # assert presenter.phase_check
        # assert presenter.phase_rel_check

        # nodes and edges were deleted, so may have been removed
        mock_view.set_deleted_nodes.assert_called()
        mock_view.set_deleted_edges.assert_called()

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

    @patch("polychron.presenters.ModelPresenter.MCMCProgressPresenter")
    @patch("polychron.presenters.ModelPresenter.MCMCProgressView")
    def test_popup_calibrate_model(self, MockMCMCProgressView, MockMCMCProgressPresenter):
        """Test that popup_calibrate_model opens the correct (mocked) popup and switches to the DatingResults presenter (if there is a current model)"""

        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked View and presenter
        mock_child_view_instance = MagicMock(spec=MCMCProgressView)
        MockMCMCProgressView.return_value = mock_child_view_instance
        mock_child_presenter_instance = MagicMock(spec=MCMCProgressPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockMCMCProgressPresenter.return_value = mock_child_presenter_instance

        # Call the callback function with the additional classes mocked and patched
        presenter.popup_calibrate_model()
        # As there is no current model, the Mock should not have been instanciated
        MockMCMCProgressPresenter.assert_not_called()
        MockMCMCProgressView.assert_not_called()
        mock_mediator.switch_presenter.assert_not_called()

        # Set a valid current model, and try again. This should create the popup and call several methods on the popup and the mediator.
        presenter.model.switch_to("foo", "bar")
        presenter.popup_calibrate_model()
        MockMCMCProgressPresenter.assert_called_once()
        MockMCMCProgressView.assert_called_once()
        mock_child_presenter_instance.view.lift.assert_called_once()
        mock_child_presenter_instance.run.assert_called_once()
        mock_child_presenter_instance.close_view.assert_called_once()
        mock_mediator.switch_presenter.assert_called_with("DatingResults")

    @pytest.mark.skip(reason="test_chronograph_render_wrap not implemented, includes tkinter")
    def test_chronograph_render_wrap(self):
        pass

    def test_chronograph_render(self):
        """Test chronograph_render would call resid_check, render the graph and update the view if there is a current model

        resid_check is patched out as it uses a popup presenter to allow users to specify residual/intrusive contexts and group relationships before rendering the graph.

        Todo:
            - Test a case which would trigger an exception during view updating
            - Remove manual fi_new_chrono rendering, call a Model method instead (which does some of ManageGroupRelationshipsPresenter.full_chronograph_func)
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Construct the Model Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)
        mock_view.reset_mock()

        # Do not select a model, which should not result in other methods being called
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.resid_check") as mock_resid_check:
            dag = presenter.chronograph_render()
            assert presenter.model.current_model is None
            mock_resid_check.assert_not_called()
            mock_view.update_littlecanvas2.assert_not_called()
            mock_view.bind_littlecanvas2_callback.assert_not_called()
            mock_view.show_image2.assert_not_called()
            assert dag is None
        mock_view.reset_mock()

        # select a model, and call chronograph render, checking expected state changes and mocked method calls
        presenter.model.switch_to("demo", "demo")
        # Make sure the chronograph exists. Todo: this should be handled by a method on the Model instance. Currently in ManageGroupRelationshipsPresenter.full_chronograph_func
        presenter.model.current_model.create_dirs()
        presenter.model.current_model.chronological_dag = remove_invalid_attributes_networkx_lt_3_4(
            presenter.model.current_model.stratigraphic_dag
        )
        write_dot(
            presenter.model.current_model.chronological_dag,
            presenter.model.current_model.get_working_directory() / "fi_new_chrono",
        )

        assert not presenter.model.current_model.load_check
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.resid_check") as mock_resid_check:
            dag = presenter.chronograph_render()
            assert presenter.model.current_model is not None
            assert presenter.model.current_model.load_check
            mock_resid_check.assert_called()
            mock_view.update_littlecanvas2.assert_called()
            mock_view.bind_littlecanvas2_callback.assert_called()
            mock_view.show_image2.assert_called()
            assert dag == presenter.model.current_model.chronological_dag
        mock_view.reset_mock()

        # Call the method once again, which should not trigger a re-render due to load_check
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.resid_check") as mock_resid_check:
            dag = presenter.chronograph_render()
            assert presenter.model.current_model is not None
            assert presenter.model.current_model.load_check
            mock_resid_check.assert_not_called()
            mock_view.update_littlecanvas2.assert_not_called()
            mock_view.bind_littlecanvas2_callback.assert_not_called()
            mock_view.show_image2.assert_not_called()
            assert dag == presenter.model.current_model.chronological_dag

    @pytest.mark.skip(reason="test_resid_check not implemented, includes tkinter")
    def test_resid_check(self):
        pass

    @patch("polychron.presenters.ModelPresenter.DatafilePreviewPresenter")
    @patch("polychron.presenters.ModelPresenter.DatafilePreviewView")
    def test_file_popup(self, MockDatafilePreviewView, MockDatafilePreviewPresenter):
        """Test that file_popup opens the (mocked) file previeew popup"""

        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Ensure the mock ModelView has required directly accessed properties
        mock_view.canvas = MagicMock()
        mock_view.parent = MagicMock()

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked View and presenter
        mock_child_view_instance = MagicMock(spec=DatafilePreviewView)
        MockDatafilePreviewView.return_value = mock_child_view_instance
        mock_child_presenter_instance = MagicMock(spec=DatafilePreviewPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockDatafilePreviewPresenter.return_value = mock_child_presenter_instance

        # Prepare a dataframe to preview, there are no restrictions on shape/contents.
        df = pd.DataFrame()
        # Call the file_popup method
        result = presenter.file_popup(df)
        # Assert that the mock popup presenter and preview were instanciated
        MockDatafilePreviewPresenter.assert_called_once()
        MockDatafilePreviewView.assert_called_once()
        # Assert the df was provided in the temp_model.
        pd.testing.assert_frame_equal(MockDatafilePreviewPresenter.call_args.args[2].df, df)
        # Assert the child view had expected methods called
        mock_child_presenter_instance.view.lift.assert_called_once()
        # Assert the ModelView had expected calls made
        mock_view.canvas.__setitem__.assert_called()
        assert mock_view.canvas.__setitem__.call_count == 2
        mock_view.parent.wait_window.assert_called()
        # As we have mocked out the popup, the result should still be cancel.
        assert result == "cancel"

        # ----

        # Reset the mocks and try again with a dataframe with several columns and rows
        # Try again
        mock_view.reset_mock()
        MockDatafilePreviewPresenter.reset_mock()
        MockDatafilePreviewView.reset_mock()
        df = pd.DataFrame({"foo": [1, 2, 3], "bar": ["a", "b", "c"]})
        # Call the file_popup method
        result = presenter.file_popup(df)
        # Assert that the mock popup presenter and preview were instanciated
        MockDatafilePreviewPresenter.assert_called_once()
        MockDatafilePreviewView.assert_called_once()
        # Assert the df was provided in the temp_model.
        pd.testing.assert_frame_equal(MockDatafilePreviewPresenter.call_args.args[2].df, df)
        # Assert the child view had expected methods called
        mock_child_presenter_instance.view.lift.assert_called_once()
        # Assert the ModelView had expected calls made
        mock_view.canvas.__setitem__.assert_called()
        assert mock_view.canvas.__setitem__.call_count == 2
        mock_view.parent.wait_window.assert_called()
        # As we have mocked out the popup, the result should still be cancel.
        assert result == "cancel"

    @pytest.mark.xfail(
        reason="open_strat_dot_file not currently implemented due to lack of valid input for polychron 0.1"
    )
    def test_open_strat_dot_file(self):
        """Test that open_strat_dot_file behaves as intended.

        This is not currently implemented, so raises a NotImplementedError which is not the real intended behaviour, so is marked as an xfail test.

        See https://github.com/bryonymoody/PolyChron/issues/112
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)
        presenter.open_strat_dot_file()

    @pytest.mark.parametrize(
        (
            "input_path",
            "file_popup_result",
            "expect_model_change",
            "expect_error",
            "expect_node_count",
            "expect_edge_count",
        ),
        [
            # No input, silently do nothing (i.e. if the popup was closed.)
            (None, "cancel", False, False, 0, 0),
            # A valid csv file, but it the user did not select "load"
            ("demo/1-strat.csv", "cancel", False, False, 0, 0),
            # Valid csv files, which are loaded
            ("demo/1-strat.csv", "load", True, False, 7, 6),
            ("thesis/thesis-b1-strat.csv", "load", True, False, 10, 9),
            ("strat-csv/unconnected.csv", "load", True, False, 3, 1),
            ("strat-csv/simple.csv", "load", True, False, 4, 4),
            # A completely empty csv
            ("strat-csv/empty.csv", "load", False, True, 0, 0),
            # A csv with an invalid context label
            pytest.param(
                "strat-csv/invalid-context-label.csv",
                "load",
                False,
                True,
                0,
                0,
                marks=pytest.mark.xfail(
                    packaging.version.parse(nx.__version__) >= packaging.version.parse("3.4.0"),
                    reason=": is only currently detected as an invalid context label by networkx < 3.4.",
                ),
            ),
            # A csv file with no rows. This is currently accepted but should not be.
            ("strat-csv/header-only.csv", "load", True, False, 0, 0),
            # A csv with the incorrect column names. This is currently accepted but column names should be validated and used accordingly
            ("strat-csv/bad-column-names.csv", "load", True, False, 4, 2),
            # A csv with extra columns. Should the extra data be kept as node attributes?
            ("strat-csv/extra-columns.csv", "load", True, False, 7, 6),
        ],
    )
    def test_open_strat_csv_file(
        self,
        input_path: str | None,
        file_popup_result: str,
        expect_model_change: bool,
        expect_error: bool,
        expect_node_count: int,
        expect_edge_count: int,
        test_data_path: pathlib.Path,
    ):
        """Test that open_strat_dot_file behaves as intended for a range of csv files.

        Parameters:
            input_path: The (partial) path to a csv file to open
            file_popup_result: the value returned by the mocked out file_popup (i.e. did the user press load?)
            expect_model_change: If we expect the model to have been updated for these inputs
            expect_error: If we expect an error messagebox to have occurred
            expect_node_count: the expected number of nodes in the stratigraphic graph
            expect_edge_count: the expected number of edges in the stratigraphic graph

        Todo:
            - A csv with no context relationships should be an error
            - Correct column names, but in a different order
            - The messagebox_error should be specialised with a reason and asserted against (via call_args).
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Reset the mock to ensure methods which were triggered by the ctor are not re-triggered.
        mock_view.reset_mock()

        # Switch to a newly created model
        presenter.model.switch_to("test", "test")

        # Mock out the value returened by view.askopenfile to be either a valid file descriptor or None, depending on the model parameter
        mock_view.askopenfile.return_value = open(test_data_path / input_path, "r") if input_path is not None else None

        # Patch out file_popup to return the parametrised value
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result

            # Call open_strat_csv_file
            presenter.open_strat_csv_file()

            # If we expect an error message, check one should have been called
            if expect_error:
                mock_view.messagebox_error.assert_called_once()
            # Otherwise, if we expcted a change to the Model instance, check the values
            elif expect_model_change:
                assert model.current_model is not None
                assert model.current_model.stratigraphic_df is not None
                assert model.current_model.stratigraphic_dag is not None
                assert model.current_model.stratigraphic_dag.number_of_nodes() == expect_node_count
                assert model.current_model.stratigraphic_dag.number_of_edges() == expect_edge_count
                assert presenter.strat_check
                assert model.current_model.deleted_nodes == []
                assert model.current_model.deleted_edges == []
                mock_view.messagebox_info.assert_called()
                mock_view.update_littlecanvas.assert_called()
                mock_view.bind_littlecanvas_callback.assert_called()
                mock_view.bind_littlecanvas_callback.assert_called()
            # Otherwise, the model should not have stratigraphic_data set or view methods called.
            else:
                assert model.current_model is not None
                assert model.current_model.stratigraphic_df is None
                assert model.current_model.stratigraphic_dag is None
                assert not presenter.strat_check
                mock_view.messagebox_info.assert_not_called()
                mock_view.update_littlecanvas.assert_not_called()
                mock_view.bind_littlecanvas_callback.assert_not_called()
                mock_view.bind_littlecanvas_callback.assert_not_called()

    @pytest.mark.parametrize(
        (
            "stratigrapic_csv",
            "input_path",
            "file_popup_result",
            "expect_model_change",
            "expect_error",
            "expect_nodes_with_determiniation",
        ),
        [
            # No input, silently do nothing (i.e. if the popup was closed.)
            (None, None, "cancel", False, False, 0),
            # A valid csv file, but it the user did not select "load"
            ("demo/1-strat.csv", "demo/2-dates.csv", "cancel", False, False, 0),
            # Valid csv files, which are loaded
            ("demo/1-strat.csv", "demo/2-dates.csv", "load", True, False, 7),
            ("thesis/thesis-b1-strat.csv", "thesis/thesis-b2-radiocarbon.csv", "load", True, False, 10),
            ("strat-csv/simple.csv", "rcd-csv/simple.csv", "load", True, False, 4),
            # A completely empty csv
            ("strat-csv/simple.csv", "rcd-csv/empty.csv", "load", False, True, 0),
            # A csv file with no rows. This is currently accepted but should not be.
            ("strat-csv/simple.csv", "rcd-csv/header-only.csv", "load", True, False, 0),
            # A csv with the incorrect column names. This currently raises an uncaught exception
            pytest.param(
                "strat-csv/simple.csv",
                "rcd-csv/bad-column-names.csv",
                "load",
                False,
                True,
                0,
                marks=pytest.mark.xfail(reason="bad column names are not handled gracefully in set_radiocarbon_df"),
            ),
            # A csv with extra columns, which are not used
            ("strat-csv/simple.csv", "rcd-csv/extra-columns.csv", "load", True, False, 4),
        ],
    )
    def test_open_scientific_dating_file(
        self,
        stratigrapic_csv: str | None,
        input_path: str | None,
        file_popup_result: str,
        expect_model_change: bool,
        expect_error: bool,
        expect_nodes_with_determiniation: int,
        test_data_path: pathlib.Path,
    ):
        """Test that open_scientific_dating_file behaves as intended for a range of csv files.

        Stratigraphic data must first be loaded, as each node in the scientific dating file must exist in the stratigraphic_dag

        Parameters:
            stratigrapic_csv: The (partial) path to a stratigraphic csv file to open
            input_path: The (partial) path to a radiocarbon dating csv file to open
            file_popup_result: the value returned by the mocked out file_popup (i.e. did the user press load?)
            expect_model_change: If we expect the model to have been updated for these inputs
            expect_error: If we expect an error messagebox to have occurred
            expect_nodes_with_determiniation: the number of nodes in the graph which should have been modified to include radiocarbon dating information.
        Todo:
            - Tests with invalid data values (i.e non numeric radiocarbon dates)
            - Correct column names, but in a different order
            - The messagebox_error should be specialised with a reason and asserted against (via call_args).
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Reset the mock to ensure methods which were triggered by the ctor are not re-triggered.
        mock_view.reset_mock()

        # Switch to a newly created model
        presenter.model.switch_to("test", "test")

        # Ensure the strat csv file has been parsed (through the presenter for now, but just on the Model would be preferable)
        mock_view.askopenfile.return_value = (
            open(test_data_path / stratigrapic_csv, "r") if stratigrapic_csv is not None else None
        )
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result
            presenter.open_strat_csv_file()

        # Mock out the value returened by view.askopenfile to be either a valid file descriptor or None, depending on the model parameter
        mock_view.askopenfile.return_value = open(test_data_path / input_path, "r") if input_path is not None else None

        # Patch out file_popup to return the parametrised value
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result

            # Call open_scientific_dating_file
            presenter.open_scientific_dating_file()

            # If we expect an error message, check one should have been called
            if expect_error:
                mock_view.messagebox_error.assert_called_once()
            # Otherwise, if we expcted a change to the Model instance, check the values
            elif expect_model_change:
                assert model.current_model is not None
                assert model.current_model.radiocarbon_df is not None
                pd.testing.assert_frame_equal(
                    model.current_model.radiocarbon_df, pd.read_csv(test_data_path / input_path, dtype="str")
                )
                assert model.current_model.stratigraphic_dag is not None
                # Check the number of nodes with the Determination set is correct
                node_determinations = [
                    d
                    for n, d in model.current_model.stratigraphic_dag.nodes("Determination")
                    if d[0] is not None and d[1] is not None
                ]
                assert len(node_determinations) == expect_nodes_with_determiniation
                assert presenter.date_check
                mock_view.messagebox_info.assert_called()
            # Otherwise, the model should not have radiocarbon_df set or view methods called.
            else:
                assert model.current_model is not None
                assert model.current_model.radiocarbon_df is None
                assert not presenter.date_check
                mock_view.messagebox_info.assert_not_called()

    @pytest.mark.parametrize(
        (
            "stratigrapic_csv",
            "input_path",
            "file_popup_result",
            "expect_model_change",
            "expect_error",
            "expected_nodes_with_group",
        ),
        [
            # No input, silently do nothing (i.e. if the popup was closed.)
            (None, None, "cancel", False, False, 0),
            # A valid csv file, but it the user did not select "load"
            ("demo/1-strat.csv", "demo/3-context-grouping.csv", "cancel", False, False, 0),
            # Valid csv files, which are loaded
            ("demo/1-strat.csv", "demo/3-context-grouping.csv", "load", True, False, 7),
            ("thesis/thesis-b1-strat.csv", "thesis/thesis-b3-context-grouping.csv", "load", True, False, 10),
            ("strat-csv/simple.csv", "context-grouping-csv/simple.csv", "load", True, False, 4),
            # A completely empty csv
            ("strat-csv/simple.csv", "context-grouping-csv/empty.csv", "load", False, True, 0),
            # A csv file with no rows. This is currently accepted but should not be.
            ("strat-csv/simple.csv", "context-grouping-csv/header-only.csv", "load", True, False, 0),
            # A csv with the incorrect column names. This currently raises an uncaught exception
            pytest.param(
                "strat-csv/simple.csv",
                "context-grouping-csv/bad-column-names.csv",
                "load",
                False,
                True,
                0,
                marks=pytest.mark.xfail(reason="bad column names are not handled gracefully in set_group_df"),
            ),
            # A csv with extra columns, which are not used
            ("strat-csv/simple.csv", "context-grouping-csv/extra-columns.csv", "load", True, False, 4),
        ],
    )
    def test_open_context_grouping_file(
        self,
        stratigrapic_csv: str | None,
        input_path: str | None,
        file_popup_result: str,
        expect_model_change: bool,
        expect_error: bool,
        expected_nodes_with_group: int,
        test_data_path: pathlib.Path,
    ):
        """Test that open_context_grouping_file behaves as intended for a range of csv files.

        Stratigraphic data must first be loaded, as each node in the context grouping file must exist in the stratigraphic_dag

        Parameters:
            stratigrapic_csv: The (partial) path to a stratigraphic csv file to open
            input_path: The (partial) path to a context grouping csv file to open
            file_popup_result: the value returned by the mocked out file_popup (i.e. did the user press load?)
            expect_model_change: If we expect the model to have been updated for these inputs
            expect_error: If we expect an error messagebox to have occurred
            expected_nodes_with_group: the number of nodes in the graph which should have been modified to include a group
        Todo:
            - Tests with invalid data values
            - Correct column names, but in a different order
            - Check with contexts that are not assigned a group (and what that should do)
            - Check with a context grouping file that has too many rows
            - Check with duplicate entries
            - The messagebox_error should be specialised with a reason and asserted against (via call_args).
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Reset the mock to ensure methods which were triggered by the ctor are not re-triggered.
        mock_view.reset_mock()

        # Switch to a newly created model
        presenter.model.switch_to("test", "test")

        # Ensure the strat csv file has been parsed (through the presenter for now, but just on the Model would be preferable)
        mock_view.askopenfile.return_value = (
            open(test_data_path / stratigrapic_csv, "r") if stratigrapic_csv is not None else None
        )
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result
            presenter.open_strat_csv_file()

        # Mock out the value returened by view.askopenfile to be either a valid file descriptor or None, depending on the model parameter
        mock_view.askopenfile.return_value = open(test_data_path / input_path, "r") if input_path is not None else None

        # Patch out file_popup to return the parametrised value
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result

            # Call open_context_grouping_file
            presenter.open_context_grouping_file()

            # If we expect an error message, check one should have been called
            if expect_error:
                mock_view.messagebox_error.assert_called_once()
            # Otherwise, if we expcted a change to the Model instance, check the values
            elif expect_model_change:
                assert model.current_model is not None
                assert model.current_model.group_df is not None
                pd.testing.assert_frame_equal(
                    model.current_model.group_df, pd.read_csv(test_data_path / input_path, dtype="str")
                )
                assert model.current_model.stratigraphic_dag is not None
                # Check the number of nodes with the Group attribute set to not None
                node_groups = [g for _, g in model.current_model.stratigraphic_dag.nodes("Group") if g is not None]
                assert len(node_groups) == expected_nodes_with_group
                assert presenter.phase_check
                mock_view.messagebox_info.assert_called()
            # Otherwise, the model should not have group_relationship set or view methods called.
            else:
                assert model.current_model is not None
                assert model.current_model.group_df is None
                assert not presenter.phase_check
                mock_view.messagebox_info.assert_not_called()

    @pytest.mark.parametrize(
        (
            "stratigrapic_csv",
            "context_grouping_csv",
            "input_path",
            "file_popup_result",
            "expect_model_change",
            "expect_error",
            "expect_num_group_rels",
        ),
        [
            # No input, silently do nothing (i.e. if the popup was closed.)
            (None, None, None, "cancel", False, False, 0),
            # A valid csv file, but it the user did not select "load"
            ("demo/1-strat.csv", "demo/3-context-grouping.csv", "demo/4-group-ordering.csv", "cancel", False, False, 0),
            # Valid csv files, which are loaded
            ("demo/1-strat.csv", "demo/3-context-grouping.csv", "demo/4-group-ordering.csv", "load", True, False, 1),
            (
                "thesis/thesis-b1-strat.csv",
                "thesis/thesis-b3-context-grouping.csv",
                "thesis/thesis-b4-group-ordering.csv",
                "load",
                True,
                False,
                1,
            ),
            (
                "strat-csv/simple.csv",
                "context-grouping-csv/simple.csv",
                "group-relationships-csv/simple.csv",
                "load",
                True,
                False,
                2,
            ),
            # A completely empty csv
            (
                "strat-csv/simple.csv",
                "context-grouping-csv/simple.csv",
                "group-relationships-csv/empty.csv",
                "load",
                False,
                True,
                0,
            ),
            # A csv file with no rows. This is currently accepted but should not be.
            (
                "strat-csv/simple.csv",
                "context-grouping-csv/simple.csv",
                "group-relationships-csv/header-only.csv",
                "load",
                True,
                False,
                0,
            ),
            # A csv with the incorrect column names. This currently does not matter.
            pytest.param(
                "strat-csv/simple.csv",
                "context-grouping-csv/simple.csv",
                "group-relationships-csv/bad-column-names.csv",
                "load",
                False,
                True,
                0,
                marks=pytest.mark.skip(reason="Column names are not checked in open_group_relationship_file"),
            ),
            # A csv with extra columns, which are not used
            (
                "strat-csv/simple.csv",
                "context-grouping-csv/simple.csv",
                "group-relationships-csv/extra-columns.csv",
                "load",
                True,
                False,
                2,
            ),
        ],
    )
    def test_open_group_relationship_file(
        self,
        stratigrapic_csv: str | None,
        context_grouping_csv: str | None,
        input_path: str | None,
        file_popup_result: str,
        expect_model_change: bool,
        expect_error: bool,
        expect_num_group_rels: int,
        test_data_path: pathlib.Path,
    ):
        """Test that open_group_relationship_file behaves as intended for a range of csv files.

        Stratigraphic data and context grouping data must first be loaded, which matches data in the incoming group relationship file

        Parameters:
            stratigrapic_csv: The (partial) path to a stratigraphic csv file to open
            context_grouping_csv: The (partial) path to a context grouping csv file to open
            input_path: The (partial) path to a group relationship csv file to open
            file_popup_result: the value returned by the mocked out file_popup (i.e. did the user press load?)
            expect_model_change: If we expect the model to have been updated for these inputs
            expect_error: If we expect an error messagebox to have occurred
            expect_num_group_rels: The expected number of group relationships

        Todo:
            - Tests with invalid data values
            - Correct column names, but in a different order
            - Check with contexts that are not assigned a group (and what that should do)
            - The messagebox_error should be specialised with a reason and asserted against (via call_args).
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Reset the mock to ensure methods which were triggered by the ctor are not re-triggered.
        mock_view.reset_mock()

        # Switch to a newly created model
        presenter.model.switch_to("test", "test")

        # Ensure the strat csv file has been loaded (through the presenter for now, but just on the Model would be preferable)
        mock_view.askopenfile.return_value = (
            open(test_data_path / stratigrapic_csv, "r") if stratigrapic_csv is not None else None
        )
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result
            presenter.open_strat_csv_file()

        # Ensure the group relationships csv file has been loaded (through the presenter for now, but just on the Model would be preferable)
        mock_view.askopenfile.return_value = (
            open(test_data_path / context_grouping_csv, "r") if context_grouping_csv is not None else None
        )
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result
            presenter.open_context_grouping_file()

        # Mock out the value returened by view.askopenfile to be either a valid file descriptor or None, depending on the model parameter
        mock_view.askopenfile.return_value = open(test_data_path / input_path, "r") if input_path is not None else None

        # Patch out file_popup to return the parametrised value
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result

            # Call open_group_relationship_file
            presenter.open_group_relationship_file()

            # If we expect an error message, check one should have been called
            if expect_error:
                mock_view.messagebox_error.assert_called_once()
            # Otherwise, if we expcted a change to the Model instance, check the values
            elif expect_model_change:
                assert model.current_model is not None
                assert model.current_model.group_relationship_df is not None
                pd.testing.assert_frame_equal(
                    model.current_model.group_relationship_df, pd.read_csv(test_data_path / input_path)
                )
                assert model.current_model.stratigraphic_dag is not None
                # Check the number of group relationships is as expected
                assert len(model.current_model.group_relationships) == expect_num_group_rels
                assert presenter.phase_check
                mock_view.messagebox_info.assert_called()
            # Otherwise, the model should not have group_relationship set or view methods called.
            else:
                assert model.current_model is not None
                assert model.current_model.group_relationship_df is None
                assert model.current_model.group_relationships is None
                assert not presenter.phase_check
                mock_view.messagebox_info.assert_not_called()

    @pytest.mark.parametrize(
        (
            "stratigrapic_csv",
            "input_path",
            "file_popup_result",
            "expect_model_change",
            "expect_error",
            "expect_node_count",
            "expect_edge_count",
        ),
        [
            # No input, silently do nothing (i.e. if the popup was closed.)
            pytest.param(None, None, "cancel", False, False, 0, 0),
            # A valid csv file, but it the user did not select "load"
            pytest.param(
                "demo/1-strat.csv",
                "demo/5-context-equality.csv",
                "cancel",
                False,
                False,
                0,
                0,
                marks=pytest.mark.xfail(reason="set_context_equality_df does not have a preview step"),
            ),
            # Valid csv files, which are loaded
            ("demo/1-strat.csv", "demo/5-context-equality.csv", "load", True, False, 6, 5),
            ("strat-csv/simple.csv", "context-equality-csv/simple.csv", "load", True, False, 3, 2),
            # A completely empty csv
            (
                "strat-csv/simple.csv",
                "context-equality-csv/empty.csv",
                "load",
                False,
                True,
                0,
                0,
            ),
            # A csv file with no rows. This is currently accepted but should not be.
            (
                "strat-csv/simple.csv",
                "context-equality-csv/header-only.csv",
                "load",
                True,
                False,
                4,
                4,
            ),
            # # A csv with the incorrect column names. This currently does not matter.
            pytest.param(
                "strat-csv/simple.csv",
                "context-equality-csv/bad-column-names.csv",
                "load",
                False,
                True,
                0,
                0,
                marks=pytest.mark.skip(reason="Column names are not checked in open_group_relationship_file"),
            ),
            # A csv with extra columns, which are not used
            (
                "strat-csv/simple.csv",
                "context-equality-csv/extra-columns.csv",
                "load",
                True,
                False,
                3,
                2,
            ),
            # A csv file which includes the same context twice. This raises an uncaught exception and mutates state.
            pytest.param(
                "strat-csv/simple.csv",
                "context-equality-csv/duplicate-row.csv",
                "load",
                True,
                False,
                3,
                2,
                marks=pytest.mark.xfail(reason="open_context_equalities_file does not gracefully handle duplcate rows"),
            ),
            # A csv file which includes the same context equality, but in both directions This raises an uncaught exception and mutates state. This could be allowed, or could be an error
            pytest.param(
                "strat-csv/simple.csv",
                "context-equality-csv/reversed.csv",
                "load",
                True,
                False,
                3,
                2,
                marks=pytest.mark.xfail(
                    reason="open_context_equalities_file does not gracefully handle duplcate (reversed) rows"
                ),
            ),
            # A csv file which combines the same node with atleast 2 others, using the pre-combined names is not handled gracefully
            pytest.param(
                "strat-csv/simple.csv",
                "context-equality-csv/multiple-combinations-original-name.csv",
                "load",
                True,
                False,
                2,
                1,
                marks=pytest.mark.xfail(
                    reason="open_context_equalities_file does not handle combining multiple context using their original labels gracefully"
                ),
            ),
            # A csv file which combines the same node with atleast 2 others, using the combined names
            pytest.param(
                "strat-csv/simple.csv",
                "context-equality-csv/multiple-combinations-combined-name.csv",
                "load",
                True,
                False,
                2,
                1,
                marks=pytest.mark.xfail(
                    reason="open_context_equalities_file combining a context with 2 others via the combined name results in a loop"
                ),
            ),
        ],
    )
    def test_open_context_equalities_file(
        self,
        stratigrapic_csv: str | None,
        input_path: str | None,
        file_popup_result: str,
        expect_model_change: bool,
        expect_error: bool,
        expect_node_count: int,
        expect_edge_count: int,
        test_data_path: pathlib.Path,
    ):
        """Test that open_context_equalities_file behaves as intended for a range of csv files.

        Stratigraphic data must be present for context to be equated to one another

        Parameters:
            stratigrapic_csv: The (partial) path to a stratigraphic csv file to open
            input_path: The (partial) path to a context eqality csv file to open
            file_popup_result: the value returned by the mocked out file_popup (i.e. did the user press load?)
            expect_model_change: If we expect the model to have been updated for these inputs
            expect_error: If we expect an error messagebox to have occurred
            expect_node_count: The expected number of nodes after contexts are combined
            expect_edge_count: The expected number of edges after contexts are combined

        Todo:
            - open_context_equalities_file does not currently respect if users press load or cancel.
            - Tests with invalid data values
            - Correct column names, but in a different order
            - Test how node attributes are handled when equating context which belong to different groups, or if they have different dates
            - Select the "real" column names. context_one, context_two?
            - The messagebox_error should be specialised with a reason and asserted against (via call_args).
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Reset the mock to ensure methods which were triggered by the ctor are not re-triggered.
        mock_view.reset_mock()

        # Switch to a newly created model
        presenter.model.switch_to("test", "test")

        # Ensure the strat csv file has been loaded (through the presenter for now, but just on the Model would be preferable)
        mock_view.askopenfile.return_value = (
            open(test_data_path / stratigrapic_csv, "r") if stratigrapic_csv is not None else None
        )
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result
            presenter.open_strat_csv_file()

        # Mock out the value returened by view.askopenfile to be either a valid file descriptor or None, depending on the model parameter
        mock_view.askopenfile.return_value = open(test_data_path / input_path, "r") if input_path is not None else None

        # Patch out file_popup to return the parametrised value
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.file_popup") as mock_file_popup:
            mock_file_popup.return_value = file_popup_result

            # Call open_context_equalities_file
            presenter.open_context_equalities_file()

            # If we expect an error message, check one should have been called
            if expect_error:
                mock_view.messagebox_error.assert_called_once()
            # Otherwise, if we expcted a change to the Model instance, check the values
            elif expect_model_change:
                assert model.current_model is not None
                assert model.current_model.context_equality_df is not None
                pd.testing.assert_frame_equal(
                    model.current_model.context_equality_df, pd.read_csv(test_data_path / input_path)
                )
                assert model.current_model.stratigraphic_dag is not None
                # Check the number of contexts and edges in the graph matches the expected values after combination
                assert model.current_model.stratigraphic_dag.number_of_nodes() == expect_node_count
                assert model.current_model.stratigraphic_dag.number_of_edges() == expect_edge_count
                mock_view.messagebox_info.assert_called()
            # Otherwise, the model should not have group_relationship set or view methods called.
            else:
                assert model.current_model is not None
                assert model.current_model.context_equality_df is None
                mock_view.messagebox_info.assert_not_called()

    def test_close_application(self):
        """Assert that close_application behaves as expected"""

        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Trigger the close_application function, as if a user selected exit from the file menu
        presenter.close_application()

        # This should have requested the mediator to close
        mock_mediator.close_window.assert_called_with("exit")

    def test_phasing(self):
        """Test the phasing method, triggered from the view toolbar, would call the expected view methods (with a current_model)"""

        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)
        # Reset the view mock
        mock_view.reset_mock()

        # With no current model, no view methods should be called.
        assert presenter.model.current_model is None
        presenter.phasing()
        assert len(mock_view.mock_calls) == 0

        # Reset the view mock
        mock_view.reset_mock()

        # Set a valid model, and the menu entry.
        presenter.model.switch_to("foo", "bar")
        # Add a strat_dag, which does not need any contents for this test but must be provided
        presenter.model.current_model.stratigraphic_dag = nx.DiGraph()
        # the grouped_rendering flag should be False
        assert not presenter.model.current_model.grouped_rendering

        # Call phasing
        presenter.phasing()

        # The grouped_rendering flag should now be true
        assert presenter.model.current_model.grouped_rendering

        # The stratigraphic graph should have also been rendered, and the view updated.
        assert presenter.model.current_model.stratigraphic_image is not None
        mock_view.update_littlecanvas.assert_called_with(presenter.model.current_model.stratigraphic_image)
        assert mock_view.bind_littlecanvas_callback.call_count == 2

        # Calling phasing once again currently does not disable grouped rendering currently (see https://github.com/bryonymoody/PolyChron/issues/135), so grouped_rendering should still be true
        presenter.phasing()
        assert presenter.model.current_model.grouped_rendering

    def test_on_data_button(self):
        """Test on_data_button, which should toggle the visibilty of a small canvas in the view"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Initially the "data loaded" panel should be hidden
        assert presenter.display_data_var == "hidden"

        # Call on_data_button which should lift the datacanvas
        presenter.on_data_button()
        mock_view.lift_datacanvas.assert_called_once()
        assert presenter.display_data_var == "onshow"
        mock_view.reset_mock()

        # Calling on_data_button again, should now lift the littelcanvas instead
        presenter.on_data_button()
        mock_view.lift_littelcanvas.assert_called_once()
        assert presenter.display_data_var == "hidden"
        mock_view.reset_mock()

    @pytest.mark.skip(reason="test_on_testmenu not yet implemented, calls tkinter")
    def test_on_testmenu(self):
        pass

    @pytest.mark.skip(reason="test_testmenu_delete_context not implemented, calls tkinter")
    def test_testmenu_delete_context(self):
        pass

    @pytest.mark.skip(reason="test_testmenu_add_new_contexts not implemented, calls tkinter")
    def test_testmenu_add_new_contexts(self):
        pass

    @pytest.mark.skip(reason="test_testmenu_delete_strat_with not implemented, calls tkinter")
    def test_testmenu_delete_strat_with(self):
        pass

    @pytest.mark.skip(reason="test_testmenu_place_above not implemented, calls tkinter")
    def test_testmenu_place_above(self):
        pass

    def test_testmenu_delete_stratigraphic_prep(self):
        """Test that testmenu_delete_stratigraphic_prep manipulates the edge_nodes list as expected and adds/removes entries in the right click menu as expected

        Todo:
            - Add a test for selecting the same node twice in a row
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # call testmenu_delete_stratigraphic_prep, as there is no current model, edge_nodes should no tbe changed and the view should not be updated
        presenter.testmenu_delete_stratigraphic_prep()
        assert presenter.edge_nodes == []
        mock_view.remove_testmenu_entry.assert_not_called()
        mock_view.append_testmenu_entry.assert_not_called()
        mock_view.reset_mock()

        # Select a current model
        presenter.model.switch_to("foo", "bar")
        # call testmenu_delete_stratigraphic_prep, as there is no selected node, it should not be added to the list
        assert presenter.node == "no node"
        presenter.testmenu_delete_stratigraphic_prep()
        assert presenter.edge_nodes == []
        mock_view.remove_testmenu_entry.assert_not_called()
        mock_view.append_testmenu_entry.assert_not_called()
        mock_view.reset_mock()

        # Set a current node
        presenter.node = "a"
        # call testmenu_delete_stratigraphic_prep, as there is a selected node, the list should be updated and view.append_testmenu_entry called
        presenter.testmenu_delete_stratigraphic_prep()
        assert presenter.edge_nodes == ["a"]
        mock_view.remove_testmenu_entry.assert_not_called()
        mock_view.append_testmenu_entry.assert_called_with("Delete stratigraphic relationship with a")
        mock_view.reset_mock()

        # Change the current node
        presenter.node = "b"
        # call testmenu_delete_stratigraphic_prep, as there is a node in edge_nodes already, there should be a remove call, followed by an append
        assert presenter.edge_nodes == ["a"]
        presenter.testmenu_delete_stratigraphic_prep()
        assert presenter.edge_nodes == ["b"]
        mock_view.remove_testmenu_entry.assert_called_with("Delete stratigraphic relationship with a")
        mock_view.append_testmenu_entry.assert_called_with("Delete stratigraphic relationship with b")
        mock_view.reset_mock()

    @pytest.mark.skip(reason="test_testmenu_equate_context_with not implemented, calls tkinter")
    def test_testmenu_equate_context_with(self):
        pass

    def test_testmenu_equate_context_prep(self):
        """Test that testmenu_equate_context_prep manipulates the comb_nodes list as expected and adds/removes entries in the right click menu as expected

        Todo:
            - Add a test for selecting the same node twice in a row
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # call testmenu_equate_context_prep, as there is no current model, comb_nodes should no tbe changed and the view should not be updated
        presenter.testmenu_equate_context_prep()
        assert presenter.comb_nodes == []
        mock_view.remove_testmenu_entry.assert_not_called()
        mock_view.append_testmenu_entry.assert_not_called()
        mock_view.reset_mock()

        # Select a current model
        presenter.model.switch_to("foo", "bar")
        # call testmenu_equate_context_prep, as there is no selected node, it should not be added to the list
        assert presenter.node == "no node"
        presenter.testmenu_equate_context_prep()
        assert presenter.comb_nodes == []
        mock_view.remove_testmenu_entry.assert_not_called()
        mock_view.append_testmenu_entry.assert_not_called()
        mock_view.reset_mock()

        # Set a current node
        presenter.node = "a"
        # call testmenu_equate_context_prep, as there is a selected node, the list should be updated and view.append_testmenu_entry called
        presenter.testmenu_equate_context_prep()
        assert presenter.comb_nodes == ["a"]
        mock_view.remove_testmenu_entry.assert_not_called()
        mock_view.append_testmenu_entry.assert_called_with("Equate context with a")
        mock_view.reset_mock()

        # Change the current node
        presenter.node = "b"
        # call testmenu_equate_context_prep, as there is a node in comb_nodes already, there should be a remove call, followed by an append
        assert presenter.comb_nodes == ["a"]
        presenter.testmenu_equate_context_prep()
        assert presenter.comb_nodes == ["b"]
        mock_view.remove_testmenu_entry.assert_called_with("Equate context with a")
        mock_view.append_testmenu_entry.assert_called_with("Equate context with b")
        mock_view.reset_mock()

    @pytest.mark.xfail(reason="testmenu_supplementary_menu not currently implemented")
    def test_testmenu_supplementary_menu(self):
        """Test that testmenu_supplementary_menu behaves as intended.

        This is not currently implemented, so raises a NotImplementedError which is not the real intended behaviour, so is marked as an xfail test.

        See https://github.com/bryonymoody/PolyChron/issues/69
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)
        presenter.testmenu_supplementary_menu()

    @pytest.mark.parametrize(
        ("project_name", "model_name", "selected_context", "expect_table_update"),
        [
            # No current model, no node,  no view calls
            (None, None, "no node", False),
            # current model, no node, no view calls
            ("foo", "bar", "no node", False),
            # # current model, valid context?, table updated
            ("foo", "bar", "a", True),
            # # current model, invalid context, table updated?
            ("foo", "bar", "", False),
        ],
    )
    def test_testmenu_get_supplementary_for_context(
        self,
        project_name: str | None,
        model_name: str | None,
        selected_context: str,
        expect_table_update: bool,
        test_data_path: pathlib.Path,
    ):
        """Test that testmenu_get_supplementary_for_context behaves as expcted if there is no current model, if no node has been selected, if valid node has been selected, or if an invalid node has been selected

        Todo:
            - Should this update to an empty table if valid data could not be extracted?
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Select the parameterised project/model
        if project_name is not None and model_name is not None:
            presenter.model.switch_to(project_name, model_name)

        # Ensure a DAG is set for the foo bar model. This should be moved to the fixture?
        if project_name == "foo" and model_name == "bar":
            presenter.model.current_model.set_stratigraphic_df(
                pd.read_csv(test_data_path / "demo" / "1-strat.csv", dtype=str)
            )

        # Select the parameterissed node, as if it were right clicked on previously
        presenter.node = selected_context

        # Call the testmenu_get_supplementary_for_context method
        presenter.testmenu_get_supplementary_for_context()

        # If a change was expected, assert that it occurred and the data was as expected
        if expect_table_update:
            mock_view.update_supplementary_data_table.assert_called_once()
            assert mock_view.update_supplementary_data_table.call_args.args[0] == selected_context
            meta_df = mock_view.update_supplementary_data_table.call_args.args[1]
            # There should be a single column?
            assert list(meta_df.columns) == ["Data"]
            # There should be 4 rows
            assert len(meta_df) == 4
            # Not currently checking exact values
        else:
            # If not expected, it should not have been called
            mock_view.update_supplementary_data_table.assert_not_called()

    @pytest.mark.parametrize(
        (
            "project_name",
            "model_name",
            "selected_context",
            "input_edge_nodes",
            "expect_remove",
            "expect_append",
            "expect_edge_nodes",
        ),
        [
            # No current model, no change
            # (None, None, "no node", None, False, False, []),
            # A current model, but no provided node. No change
            ("foo", "bar", "no node", None, False, False, []),
            # A current model, but no provided node, with an existing node No change
            ("foo", "bar", "no node", ["b"], True, False, []),
            # A current model, a selected context and no prior model. some changes.
            ("foo", "bar", "a", None, False, True, ["a"]),
            ("foo", "bar", "a", [], False, True, ["a"]),
            # A current model, a slected context, with a single existing element selected
            ("foo", "bar", "a", ["b"], True, True, ["a"]),
            # A current model, a slected context, with a an invlida number of existing edge_nodes
            ("foo", "bar", "a", ["mode", "than", "expected"], True, True, ["a"]),
        ],
    )
    def test_testmenu_place_above_prep(
        self,
        project_name: str | None,
        model_name: str | None,
        selected_context: str,
        input_edge_nodes: list[str] | None,
        expect_remove: bool,
        expect_append: bool,
        expect_edge_nodes: list[str],
    ):
        """Test that testmenu_place_above_prep adds/removes entrys from the right-click menu, depending on the selected node and the current state of the test menu"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the ModelPresenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Select the parameterised project/model
        if project_name is not None and model_name is not None:
            presenter.model.switch_to(project_name, model_name)

        # Set the selected node/context
        presenter.node = selected_context

        # Set the state of edge_nodes
        if input_edge_nodes is not None:
            presenter.edge_nodes = input_edge_nodes

        # Call testmenu_place_above_prep
        presenter.testmenu_place_above_prep()

        # If a call to the view.remove_testmenu_entry was expected, check that it was called
        if expect_remove:
            mock_view.remove_testmenu_entry.assert_called_with(f"Place {input_edge_nodes[0]} Above")
        else:
            mock_view.remove_testmenu_entry.assert_not_called()

        # If a call to the view.append_testmenu_entry was expected, check that it was called
        if expect_append:
            mock_view.append_testmenu_entry.assert_called_with(f"Place {selected_context} Above")
        else:
            mock_view.append_testmenu_entry.assert_not_called()

        # Assert that the value of edge_nodes is now as expected
        assert presenter.edge_nodes == expect_edge_nodes

    @pytest.mark.skip(reason="test_pre_click not implemented, calls tkinter")
    def test_pre_click(self):
        pass

    @pytest.mark.skip(reason="test_on_left not implemented, calls tkinter")
    def test_on_left(self):
        pass

    def test_on_right(self):
        """Test on_right behaves as expected. It should call several methods on the (mocked) view

        Todo:
            - Test with a Model which includes a chronological_image
            - Test with and without coordinates returned (and with/without a chrono image)"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Reset the view mock for correct patching
        mock_view.reset_mock()

        # Ensure the mocked show_testmenu returns a pair of coordinates
        mock_view.show_testmenu.return_value = (12, 12)

        # Mock out nodecheck so we can check if it was called without looking for side-effects
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.nodecheck") as mock_nodecheck:
            # Call the method
            presenter.on_right()

            # Assert that mouse 1 was rebound
            mock_view.unbind_littlecanvas_callback.assert_called_once_with("<Button-1>")
            mock_view.bind_littlecanvas_callback.assert_called_once()
            assert mock_view.bind_littlecanvas_callback.call_args.args[0] == "<Button-1>"
            assert callable(mock_view.bind_littlecanvas_callback.call_args.args[1])

            # There is no chronological image, so nodecheck should not have been called.
            mock_nodecheck.assert_not_called()

    def check_list_gen(self):
        """Assert that check_lsit gen calls the appropriate view method, providing the correct data for the ModelPresenter's state

        Todo:
            - Test this with an actual Model with varying input files provided
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Initial state should result in lots of crosses
        presenter.check_list_gen()
        mock_view.update_datacanvas_checklist.assert_called_with(False, False, False, False)
        mock_view.reset_mock()

        # if we simulate setting the checks, it should be called with 4* True
        presenter.strat_check = True
        presenter.date_check = True
        presenter.phase_check = True
        presenter.phase_rel_check = True
        presenter.check_list_gen()
        mock_view.update_datacanvas_checklist.assert_called_with(True, True, True, True)

    @patch("polychron.presenters.ModelPresenter.ProjectSelectProcessPopupPresenter")
    @patch("polychron.presenters.ModelPresenter.ProjectSelectProcessPopupView")
    def test_load_project(self, MockProjectSelectProcessPopupView, MockProjectSelectProcessPopupPresenter):
        """Test that load_project creates and displays the correct popup presenter/view, waits, and then calls update_view"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Ensure the mock ModelView has required directly accessed properties
        mock_view.canvas = MagicMock()

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked View and presenter
        mock_child_view_instance = MagicMock(spec=ProjectSelectProcessPopupView)
        MockProjectSelectProcessPopupView.return_value = mock_child_view_instance
        mock_child_presenter_instance = MagicMock(spec=ProjectSelectProcessPopupPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockProjectSelectProcessPopupPresenter.return_value = mock_child_presenter_instance

        # Set a current model
        presenter.model.switch_to("foo", "bar")

        # Call the load_project, with update_view patch so it can be detected
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.update_view") as mock_update_view:
            presenter.load_project()

            # Assert that the popup was created, lifted, and waited for
            MockProjectSelectProcessPopupPresenter.assert_called_once()
            MockProjectSelectProcessPopupView.assert_called_once()
            assert MockProjectSelectProcessPopupPresenter.call_args.args[2] == presenter.model
            mock_child_presenter_instance.view.lift.assert_called_once()
            mock_child_presenter_instance.view.wait_window.assert_called()
            mock_update_view.assert_called_once()

    @patch("polychron.presenters.ModelPresenter.ProjectSelectProcessPopupPresenter")
    @patch("polychron.presenters.ModelPresenter.ProjectSelectProcessPopupView")
    def test_load_existing_model(self, MockProjectSelectProcessPopupView, MockProjectSelectProcessPopupPresenter):
        """Test that load_existing_model creates and displays the correct popup presenter/view, waits, and then calls update_view. The popup presenter should also have been switched to the model_select view"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Ensure the mock ModelView has required directly accessed properties
        mock_view.canvas = MagicMock()

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked View and presenter
        mock_child_view_instance = MagicMock(spec=ProjectSelectProcessPopupView)
        MockProjectSelectProcessPopupView.return_value = mock_child_view_instance
        mock_child_presenter_instance = MagicMock(spec=ProjectSelectProcessPopupPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockProjectSelectProcessPopupPresenter.return_value = mock_child_presenter_instance

        # Set a current model
        presenter.model.switch_to("foo", "bar")

        # Call the load_existing_model, with update_view patch so it can be detected
        with patch("polychron.presenters.ModelPresenter.ModelPresenter.update_view") as mock_update_view:
            presenter.load_existing_model()

            # Assert that the popup was created, lifted, and waited for
            MockProjectSelectProcessPopupPresenter.assert_called_once()
            MockProjectSelectProcessPopupView.assert_called_once()
            assert MockProjectSelectProcessPopupPresenter.call_args.args[2] == presenter.model
            mock_child_presenter_instance.view.lift.assert_called_once()
            mock_child_presenter_instance.view.wait_window.assert_called()
            mock_child_presenter_instance.switch_presenter.assert_called_with("model_select")
            mock_update_view.assert_called_once()
            # As the popup was mocked, we can check that the model's next project was specified, but not cleared by actually switching to the next project.
            assert presenter.model.next_project_name == "foo"

    @pytest.mark.skip(reason="test_save_model not implemented, calls tkinter")
    def test_save_model(self):
        pass

    @patch("polychron.presenters.ModelPresenter.ProjectSelectProcessPopupPresenter")
    @patch("polychron.presenters.ModelPresenter.ProjectSelectProcessPopupView")
    def test_save_as_new_model(self, MockProjectSelectProcessPopupView, MockProjectSelectProcessPopupPresenter):
        """Test that save_as_new_model creates and displays the correct popup presenter/view, waits, and then calls update_view. The popup presenter should also have been switched to the model_create view

        Todo:
            - Test this when there is no current model selected
            - Test case with a change to the current_project_name or current_model_name selected
            - Test case with no change, but the the window was closed by the cross / selecting the current model. This is not currently detectable
            - Todo: Consistent use of wait_window across different methods?
        """
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Ensure the mock ModelView has required directly accessed properties
        mock_view.canvas = MagicMock()

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked View and presenter
        mock_child_view_instance = MagicMock(spec=ProjectSelectProcessPopupView)
        MockProjectSelectProcessPopupView.return_value = mock_child_view_instance
        mock_child_presenter_instance = MagicMock(spec=ProjectSelectProcessPopupPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockProjectSelectProcessPopupPresenter.return_value = mock_child_presenter_instance

        # Set a current model
        presenter.model.switch_to("foo", "bar")

        # Call the save_as_new_model, with update_view patch so it can be detected
        with (
            patch("polychron.presenters.ModelPresenter.ModelPresenter.update_view") as mock_update_view,
            patch("polychron.models.ProjectSelection.Model.save") as mock_save,
        ):
            presenter.save_as_new_model()

            # Assert that the popup was created, lifted, and waited for
            MockProjectSelectProcessPopupPresenter.assert_called_once()
            MockProjectSelectProcessPopupView.assert_called_once()
            assert MockProjectSelectProcessPopupPresenter.call_args.args[2] == presenter.model
            mock_child_presenter_instance.view.lift.assert_called_once()
            mock_view.wait_window.assert_called()
            # Assert the popup was switched to the model_create presenter
            mock_child_presenter_instance.switch_presenter.assert_called_with("model_create")

            # As the popup presenter is mocked, but does not change the ProjectSelect state to change to a different model, save and update_view should not have been called.
            mock_update_view.assert_not_called()
            mock_save.assert_not_called()

    def test_on_resize(self):
        """Test that on_resize reopens the stratigraphic graph and updates the appropriate canvas if a current model is selected"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Ensure the mock ModelView has required directly accessed properties
        mock_view.canvas = MagicMock()

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # There is no current model, so up update_littlecanvas_image_only should not have been called
        assert presenter.model.current_model is None
        presenter.on_resize(None)
        mock_view.update_littlecanvas_image_only.assert_not_called()

        # Switch to a model which exists but does not have a stratigraphic_image.
        presenter.model.switch_to("foo", "bar")
        # This should not trigger a view update
        assert presenter.model.current_model is not None
        presenter.on_resize(None)
        assert presenter.model.current_model.stratigraphic_image is None
        mock_view.update_littlecanvas_image_only.assert_not_called()

        # Switch to a model which exists and has a stratigraphic_image
        presenter.model.switch_to("demo", "demo")
        model.current_model.load_check = True
        model.current_model.render_strat_graph()

        # This should have triggered a view update
        assert presenter.model.current_model.stratigraphic_image is not None
        presenter.on_resize(None)
        mock_view.update_littlecanvas_image_only.assert_called()

    def test_on_resize_2(self):
        """Test that on_resize_2 reopens the chronological graph and updates the appropriate canvas if a current model is selected

        Todo:
            - Remove manual fi_new_chrono rendering, call a Model method instead (which does some of ManageGroupRelationshipsPresenter.full_chronograph_func)
        """
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Ensure the mock ModelView has required directly accessed properties
        mock_view.canvas = MagicMock()

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # There is no current model, so up update_littlecanvas2_image_only should not have been called
        assert presenter.model.current_model is None
        presenter.on_resize_2(None)
        mock_view.update_littlecanvas2_image_only.assert_not_called()

        # Switch to a model which exists but does not have a chronological_image.
        presenter.model.switch_to("foo", "bar")
        # This should not trigger a view update
        assert presenter.model.current_model is not None
        presenter.on_resize_2(None)
        assert presenter.model.current_model.chronological_image is None
        mock_view.update_littlecanvas2_image_only.assert_not_called()

        # Switch to a model which exists and has a chronological_image
        presenter.model.switch_to("demo", "demo")
        # Make sure the chronograph exists. Todo: this should be handled by a method on the Model instance. Currently in ManageGroupRelationshipsPresenter.full_chronograph_func
        presenter.model.current_model.create_dirs()
        presenter.model.current_model.chronological_dag = remove_invalid_attributes_networkx_lt_3_4(
            presenter.model.current_model.stratigraphic_dag
        )
        write_dot(
            presenter.model.current_model.chronological_dag,
            presenter.model.current_model.get_working_directory() / "fi_new_chrono",
        )
        presenter.model.current_model.load_check = True
        presenter.model.current_model.render_chrono_graph()

        # This should have triggered a view update
        presenter.on_resize_2(None)
        assert presenter.model.current_model.chronological_image is not None
        mock_view.update_littlecanvas2_image_only.assert_called()

    @pytest.mark.skip(reason="test_move_from not implemented, calls tkinter")
    def test_move_from(self):
        pass

    @pytest.mark.skip(reason="test_move_to not implemented, calls tkinter")
    def test_move_to(self):
        pass

    @pytest.mark.skip(reason="test_move_from2 not implemented, calls tkinter")
    def test_move_from2(self):
        pass

    @pytest.mark.skip(reason="test_move_to2 not implemented, calls tkinter")
    def test_move_to2(self):
        pass

    def test_on_wheel(self):
        """Test on_wheel behaves as expected, which just calls a view method"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Call on_wheel providing a pretend event value
        event = None
        presenter.on_wheel(event)
        # Assert the view method was called, with the provided event
        mock_view.wheel.assert_called_once_with(event)

    def test_on_wheel2(self):
        """Test on_wheel2 behaves as expected, which just calls a view method"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Call on_wheel2 providing a pretend event value
        event = None
        presenter.on_wheel2(event)
        # Assert the view method was called, with the provided event
        mock_view.wheel2.assert_called_once_with(event)

    @pytest.mark.skip(reason="test_addedge not implemented, calls tkinter")
    def test_addedge(self):
        pass

    @pytest.mark.parametrize(
        ("project_name", "model_name", "context", "expected_result"),
        [
            # No project/model, any node value, no output expected
            (None, None, "no node", None),
            # With a current model, but it does not have a stratigraphic_dag, None should be returned
            ("foo", "bar", "no node", None),
            # With a model with a DAG, but a context which is not in the dag, return None
            ("demo", "demo", "no node", None),
            # With a model with a DAG, and a valid node, expect the correct result (for multiple nodes)
            ("demo", "demo", "a", ("", "b")),
            ("demo", "demo", "b", ("a", "c = d, e")),
            ("demo", "demo", "c = d", ("b", "f")),
            ("demo", "demo", "e", ("b", "g")),
            ("demo", "demo", "f", ("c = d", "")),
            ("demo", "demo", "g", ("e", "")),
        ],
    )
    def test_stratfunc(
        self, project_name: str | None, model_name: str | None, context: str, expected_result: tuple[str] | None
    ):
        """Test that stratfunc returns the expected 2-tuple of strings or None depending on the state of the current Model"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Switch to the parameterised project/model
        if project_name is not None and model_name is not None:
            presenter.model.switch_to(project_name, model_name)
            assert presenter.model.current_model is not None

        # Call the method being tested
        retval = presenter.stratfunc(context)

        # Check that the output was as expected
        assert retval == expected_result

    def test_nodecheck(self):
        """Test nodecheck behaves as expected.

        As node coordinates are generated via graphviz in node_coords_from_svg, and the coordinates vary on different platforms / versions, we cannot check specific coordinates without mocking

        Todo:
            - Fully implement this test with a valid Model, whch has a stratigraphic_image/dag
            - Test with different imscale values
            - Propperly create the test Model, rather than manually producing the DAG and image
            - This test could be simplified to cover less edge cases, now that TestUtil tests the underling methods for a lot of cases
        """

        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Ensure the mock view returns the correct imscale value
        mock_view.imscale = 1.0

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # There should be no current project or presenter, None should be returned
        assert presenter.model.current_project_name is None
        assert presenter.model.current_model_name is None
        assert presenter.nodecheck(0, 0) is None

        # ---

        # Create a model
        model.switch_to("nodecheck", "nodecheck", load_ok=True, create_ok=True)
        # Create a stratigraphic graph, skipping other inputs for now. Nodes have custom shapes to cover test cases. Edges are not required but included to prevent all nodes being in a single line (hopefully)
        g = nx.DiGraph()
        g.add_node("box", shape="box")
        g.add_node("diamond", shape="diamond")
        g.add_node("ellipse", shape="ellipse")
        g.add_edge("box", "diamond")

        # Set the fake stratigraphic DAG. This Model will be techincally invalid.
        model.current_model.stratigraphic_dag = g
        # Make sure strat new image is created. Ideally this should be tested just by Model methods, rather than manually creating this here
        write_dot(model.current_model.stratigraphic_dag, model.current_model.get_working_directory() / "fi_new.txt")
        # Fake the load_check so the strat dag will get rendered, which is a bit evil.
        model.current_model.load_check = True

        # Prepare mock values to be returned from node_coords_from_svg to avoid graphviz non-determinsm issues.
        #  Alteranatively we could get the values returned and only test within those.
        # Use values which were emitted by manually rendering this graph
        node_coords = {
            "box": [32.75, 86.75, 72.0, 108.0],
            "diamond": [-0.25, 119.74, -0.0, 36.0],
            "ellipse": [105.15, 172.35, 72.0, 108.0],
        }
        scale = [176.54, 112.0]

        # Define the svg coordinates to check.
        tests_coords = [
            [[59.75, 90.0], "box"],  # mid box
            [[32.85, 72.5], "box"],  # inside the corner of the box.
            [[32.75, 72.0], None],  # on the corner of  box
            [[31.75, 71.0], None],  # outside corner box
            [[59.745, 18.0], "diamond"],  # mid diamond
            [[1.0, 1.0], "diamond"],  # inside corner diamond, would be None with non-axis aligned bounding boxes
            [[-0.25, -0.0], None],  # on the corner diamond
            [[-1.25, -1.0], None],  # outside corner diamond
            [[138.75, 90.0], "ellipse"],  # mid ellipse
            [[105.5, 72.2], "ellipse"],  # inside corner ellipse, would be None with non-axis aligned bounding boxes
            [[105.15, 72.0], None],  # on corner ellipse
            [[104.15, 71.0], None],  # outside corner ellipse
            [[0.0, 0.0], None],  # nothing
            [[-100.0, -100.0], None],  # negative
            [[1000.0, 1000.0], None],  # larger then scale
        ]

        # Patch  node_coords_from_svg
        with patch("polychron.models.Model.node_coords_from_svg") as mock_node_coords_from_svg:
            # Ensure the mock returns the correct values
            mock_node_coords_from_svg.return_value = (node_coords, scale)

            # render the stratigraphic dag, which will also set the node coordinates using the mocked method
            model.current_model.render_strat_graph()

            # Resize the models image, as graphviz may not be making an image that matches the placement in the hard-coded svg.
            model.current_model.stratigraphic_image = model.current_model.stratigraphic_image.resize(
                (int(math.ceil(scale[0])), int(math.ceil(scale[1])))
            )

            # Check with several coordinate pairs, which should miss, hit boxes, hit diamonds, or hit elipses.
            for (x, y), node in tests_coords:
                # Get the node at the specified coords, checking the returned value is as expected.
                assert presenter.nodecheck(x, y) == node

    @patch("polychron.presenters.ModelPresenter.RemoveContextPresenter")
    @patch("polychron.presenters.ModelPresenter.RemoveContextView")
    def test_node_del_popup(self, MockRemoveContextView, MockRemoveContextPresenter):
        """Test that node_del_popup creates and displays the correct popup presenter/view with appropriate data

        Todo:
            - Test that if the mocked out popup presenter updated the reason, it would have been updated?
            - Should the popup be opened if there is no current model?
        """
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Ensure the mock ModelView has required directly accessed properties
        mock_view.canvas = MagicMock()

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked View and presenter
        mock_child_view_instance = MagicMock(spec=RemoveContextView)
        MockRemoveContextView.return_value = mock_child_view_instance
        mock_child_presenter_instance = MagicMock(spec=RemoveContextPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockRemoveContextPresenter.return_value = mock_child_presenter_instance

        # Set a current model
        presenter.model.switch_to("foo", "bar")

        # Call the node_del_popup function with string inputs.
        reason = presenter.node_del_popup("a")

        # Assert that the popup was created, lifted, and waited for
        MockRemoveContextPresenter.assert_called_once()
        MockRemoveContextView.assert_called_once()
        mock_child_presenter_instance.view.lift.assert_called_once()
        mock_view.wait_window.assert_called()
        mock_view.canvas.__setitem__.assert_called()
        assert mock_view.canvas.__setitem__.call_count == 2
        # As we have mocked out the popup, the result should still be None.
        assert reason is None

    @patch("polychron.presenters.ModelPresenter.RemoveStratigraphicRelationshipPresenter")
    @patch("polychron.presenters.ModelPresenter.RemoveStratigraphicRelationshipView")
    def test_edge_del_popup(
        self, MockRemoveStratigraphicRelationshipView, MockRemoveStratigraphicRelationshipPresenter
    ):
        """Test that edge_del_popup creates and displays the correct popup presenter/view with appropriate data

        Todo:
            - Test that if the mocked out popup presenter updated the reason, it would have been updated?
            - Should the popup be opened if there is no current model?
        """
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ModelView)
        model = self.project_selection

        # Ensure the mock ModelView has required directly accessed properties
        mock_view.canvas = MagicMock()

        # Instantiate the Presenter
        presenter = ModelPresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked View and presenter
        mock_child_view_instance = MagicMock(spec=RemoveStratigraphicRelationshipView)
        MockRemoveStratigraphicRelationshipView.return_value = mock_child_view_instance
        mock_child_presenter_instance = MagicMock(spec=RemoveStratigraphicRelationshipPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockRemoveStratigraphicRelationshipPresenter.return_value = mock_child_presenter_instance

        # Set a current model
        presenter.model.switch_to("foo", "bar")

        # Call the edge_del_popup function with string inputs.
        reason = presenter.edge_del_popup("a", "b")

        # Assert that the popup was created, lifted, and waited for
        MockRemoveStratigraphicRelationshipPresenter.assert_called_once()
        MockRemoveStratigraphicRelationshipView.assert_called_once()
        mock_child_presenter_instance.view.lift.assert_called_once()
        mock_view.wait_window.assert_called()
        mock_view.canvas.__setitem__.assert_called()
        assert mock_view.canvas.__setitem__.call_count == 2
        # As we have mocked out the popup, the result should still be None.
        assert reason is None
