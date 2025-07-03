from __future__ import annotations

import pathlib
import platform
from unittest.mock import MagicMock, patch

import networkx as nx
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
        pd.testing.assert_frame_equal(MockDatafilePreviewPresenter.call_args.args[2]["df"], df)
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
        pd.testing.assert_frame_equal(MockDatafilePreviewPresenter.call_args.args[2]["df"], df)
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

    @pytest.mark.skip(reason="test_open_strat_csv_file not implemented, includes tkinter")
    def test_open_strat_csv_file(self):
        pass

    @pytest.mark.skip(reason="test_open_scientific_dating_file not implemented, includes tkinter")
    def test_open_scientific_dating_file(self):
        pass

    @pytest.mark.skip(reason="test_open_context_grouping_file not implemented, includes tkinter")
    def test_open_context_grouping_file(self):
        pass

    @pytest.mark.skip(reason="test_open_group_relationship_file not implemented, includes tkinter")
    def test_open_group_relationship_file(self):
        pass

    @pytest.mark.skip(reason="test_open_context_equalities_file not implemented, includes tkinter")
    def test_open_context_equalities_file(self):
        pass

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

    @pytest.mark.skip(reason="test_on_testmenu not yet implemented")
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

    @pytest.mark.skip(reason="test_testmenu_delete_stratigraphic_prep not implemented")
    def test_testmenu_delete_stratigraphic_prep(self):
        pass

    @pytest.mark.skip(reason="test_testmenu_equate_context_with not implemented, calls tkinter")
    def test_testmenu_equate_context_with(self):
        pass

    @pytest.mark.skip(reason="test_testmenu_equate_context_prep not implemented")
    def test_testmenu_equate_context_prep(self):
        pass

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

    @pytest.mark.skip(reason="test_on_resize not implemented")
    def test_on_resize(self):
        pass

    @pytest.mark.skip(reason="test_on_resize_2 not implemented")
    def test_on_resize_2(self):
        pass

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

    @pytest.mark.skip(reason="test_stratfunc not implemented")
    def test_stratfunc(self):
        pass

    @pytest.mark.skip(reason="test_nodecheck not implemented")
    def test_nodecheck(self):
        pass

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
