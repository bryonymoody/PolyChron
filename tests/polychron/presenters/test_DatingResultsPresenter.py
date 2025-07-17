import math
import pathlib
from unittest.mock import MagicMock, patch

import networkx as nx
import pytest
from networkx.drawing.nx_pydot import write_dot

from polychron.interfaces import Mediator
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.DatingResultsPresenter import DatingResultsPresenter
from polychron.views.DatingResultsView import DatingResultsView


class TestDatingResultsPresenter:
    """Unit tests for the DatingResultsPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    @pytest.fixture(autouse=True)
    def setup_tmp_projects_directory(self, tmp_path: pathlib.Path):
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

        # Yeild control to the tests
        yield

        # post-test cleanup. tmp_path_factory automatically temporary directory/file deletion
        self.tmp_projects_dir = None
        self.project_selection = None

    @patch("polychron.presenters.DatingResultsPresenter.DatingResultsPresenter.update_view")
    def test_init(self, mock_update_view):
        """Tests the __init__ method of the DatingResultsPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that the presenter properties are initialsed as expected
        assert presenter.results_list == {}
        assert presenter.node == "no node"
        assert presenter.phase_len_nodes == []
        assert presenter.fig is None

        # Assert tab callback functions were bound
        mock_view.bind_sasd_tab_button.assert_called_once()
        assert len(mock_view.bind_sasd_tab_button.call_args.args) == 1
        assert callable(mock_view.bind_sasd_tab_button.call_args.args[0])

        mock_view.bind_dr_tab_button.assert_called_once()
        assert len(mock_view.bind_dr_tab_button.call_args.args) == 1
        assert callable(mock_view.bind_dr_tab_button.call_args.args[0])

        # Assert that button callbacks were bound
        mock_view.bind_posterior_densities_button.assert_called_once()
        assert len(mock_view.bind_posterior_densities_button.call_args.args) == 1
        assert callable(mock_view.bind_posterior_densities_button.call_args.args[0])
        mock_view.bind_hpd_button.assert_called_once()
        assert len(mock_view.bind_hpd_button.call_args.args) == 1
        assert callable(mock_view.bind_hpd_button.call_args.args[0])
        mock_view.bind_clear_list_button.assert_called_once()
        assert len(mock_view.bind_clear_list_button.call_args.args) == 1
        assert callable(mock_view.bind_clear_list_button.call_args.args[0])

        # Assert that menu bars were setup

        # Assert that build_file_menu was called on the view
        mock_view.build_file_menu.assert_called_once()

        # Assert that build_file_menu was passed a list containing the expected 2 items
        assert len(mock_view.build_file_menu.call_args.args) == 1
        file_menu_items = mock_view.build_file_menu.call_args.args[0]
        assert isinstance(file_menu_items, list)
        assert len(file_menu_items) == 2
        assert file_menu_items[0] is None
        assert isinstance(file_menu_items[1], tuple)
        assert len(file_menu_items[1]) == 2
        assert file_menu_items[1][0] == "Save project progress"
        assert callable(file_menu_items[1][1])

        # Assert that the right click menu was set up
        mock_view.bind_testmenu2_commands.assert_called_once()
        assert len(mock_view.bind_testmenu2_commands.call_args.args) == 1
        assert callable(mock_view.bind_testmenu2_commands.call_args.args[0])

        # Assert that canvas events were bound (4 callable arguments)
        mock_view.bind_littlecanvas2_events.assert_called_once()
        assert len(mock_view.bind_littlecanvas2_events.call_args.args) == 4
        assert callable(mock_view.bind_littlecanvas2_events.call_args.args[0])
        assert all([callable(x) for x in mock_view.bind_littlecanvas2_events.call_args.args])

        # update_view should have been called.
        mock_update_view.assert_called()

    @patch("polychron.presenters.DatingResultsPresenter.DatingResultsPresenter.chronograph_render_post")
    def test_update_view(self, mock_chronograph_render_post):
        """Tests DatingResultsPresenter.update_view, ensuring it calls the expected method (via patching to avoid explicitly testing chronograph_render_post twice)"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # Reset the mock
        mock_chronograph_render_post.reset_mock()
        # Update the view
        presenter.update_view()
        # Ensure the expected method was called
        mock_chronograph_render_post.assert_called_once()

    def test_get_window_title_suffix(self):
        """Test get_window_title_suffix returns None if there is no current project/model, or a valid string if one is set"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # There should be no current project or presenter, so assert get_window_title_suffix returns None
        assert presenter.model.current_project_name is None
        assert presenter.model.current_model_name is None
        assert presenter.get_window_title_suffix() is None

        # Set a (valid) current Project & Model, and assert the suffix is as expected
        model.switch_to("foo", "bar", load_ok=True, create_ok=False)
        assert presenter.get_window_title_suffix() == "foo - bar"

    def test_on_file_save(self):
        """Test on_file_save behaves as expected"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # There should be no current project or presenter, so assert Model.save does not get called
        assert presenter.model.current_project_name is None
        assert presenter.model.current_model_name is None
        with patch("polychron.models.ProjectSelection.Model.save") as mock_model_save:
            presenter.on_file_save()
            mock_model_save.assert_not_called()

        # Set a (valid) current Project & Model, and assert that Model.save would have been called
        model.switch_to("foo", "bar", load_ok=True, create_ok=False)
        with patch("polychron.models.ProjectSelection.Model.save") as mock_model_save:
            presenter.on_file_save()
            mock_model_save.assert_called_once()

    def test_on_button_posterior_densities(self):
        """Test on_button_posterior_densities behaves as expected. This just calls mcmc_output, so test that would have been called."""

        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        with patch(
            "polychron.presenters.DatingResultsPresenter.DatingResultsPresenter.mcmc_output"
        ) as mock_mcmc_output:
            presenter.on_button_posterior_densities()
            mock_mcmc_output.assert_called_once()

    def test_on_button_hpd_button(self):
        """Test on_button_hpd_button behaves as expected. This just calls get_hpd_interval, so test that would have been called."""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        with patch(
            "polychron.presenters.DatingResultsPresenter.DatingResultsPresenter.get_hpd_interval"
        ) as mock_get_hpd_interval:
            presenter.on_button_hpd_button()
            mock_get_hpd_interval.assert_called_once()

    def test_on_button_clear_list_button(self):
        """Test on_button_clear_list_button behaves as expected. This just calls clear_results_list, so test that would have been called."""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        with patch(
            "polychron.presenters.DatingResultsPresenter.DatingResultsPresenter.clear_results_list"
        ) as mock_clear_results_list:
            presenter.on_button_clear_list_button()
            mock_clear_results_list.assert_called_once()

    @pytest.mark.skip(reason="test_pre_click not implemented, includes tkinter call")
    def test_pre_click(self):
        """Test pre_click behaves as expected"""
        pass

    @pytest.mark.skip(reason="test_on_left not implemented, includes tkinter call")
    def test_on_left(self):
        """Test on_left behaves as expected"""
        pass

    def test_on_right(self):
        """Test on_right behaves as expected. It should call several methods on the (mocked) view

        Todo:
            - Test with a Model which includes a chronological_image
            - Test with and without coordinates returned (and with/without a chrono image)"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # Ensure the mocked show_testmenu returns a pair of coordinates
        mock_view.show_testmenu.return_value = (12, 12)

        # Mock out nodecheck so we can check if it was called without looking for side-effects
        with patch("polychron.presenters.DatingResultsPresenter.DatingResultsPresenter.nodecheck") as mock_nodecheck:
            # Call the method
            presenter.on_right()

            # Assert that mouse 1 was rebound
            mock_view.unbind_littlecanvas2_callback.assert_called_once_with("<Button-1>")
            mock_view.bind_littlecanvas2_callback.assert_called_once()
            assert mock_view.bind_littlecanvas2_callback.call_args.args[0] == "<Button-1>"
            assert callable(mock_view.bind_littlecanvas2_callback.call_args.args[1])

            # There is no chronological image, so nodecheck should not have been called.
            mock_nodecheck.assert_not_called()

    def test_on_canvas_wheel2(self):
        """Test on_canvas_wheel2 behaves as expected, which just calls a view method"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # Call on_canvas_wheel2 providing a pretend event value
        event = None
        presenter.on_canvas_wheel2(event)
        # Assert the view method was called, with the provided event
        mock_view.wheel2.assert_called_once_with(event)

    @pytest.mark.skip(reason="test_on_canvas_move_from2 not implemented, includes tkinter")
    def test_on_canvas_move_from2(self):
        """Test on_canvas_move_from2 behaves as expected"""
        pass

    @pytest.mark.skip(reason="test_on_canvas_move_to2 not implemented, includes tkinter")
    def test_on_canvas_move_to2(self):
        """Test on_canvas_move_to2 behaves as expected"""
        pass

    def test_chronograph_render_post(self):
        """Test chronograph_render_post behaves as expected, with and without a current model

        Todo:
            - Test with a Model which would pass load_check
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # There should be no current project or presenter
        assert presenter.model.current_project_name is None
        assert presenter.model.current_model_name is None
        # Call chronograph_render_post, and assert that that Model.render_chronograph and view.update_littlecanvas2 would not have been called
        with patch("polychron.models.ProjectSelection.Model.render_chrono_graph") as mock_model_render_chrono_graph:
            presenter.chronograph_render_post()
            mock_model_render_chrono_graph.assert_not_called()
            mock_view.update_littlecanvas2.assert_not_called()
        mock_view.reset_mock()

        # ---

        # Todo: prep a Model which would pass load_check
        # # Set a (valid) current Project & Model
        # model.switch_to("foo", "bar", load_ok=True, create_ok=False)
        # # This should meet load_check
        # assert model.current_model.load_check
        # # This should result in a rendered chronograph, and so update_littlecanvas2 should have been called
        # presenter.chronograph_render_post()
        # assert model.current_model.chronological_image is not None
        # mock_view.update_littlecanvas2.assert_called_with(model.current_model.chronological_image)

    def test_nodecheck(self):
        """Test nodecheck behaves as expected.

        As node coordinates are generated via graphviz in node_coords_from_svg, and the coordinates vary on different platforms / versions, we cannot check specific coordinates without mocking

        Todo:
            - Fully implement this test with a valid Model, which has a chronological_image
            - Test with different imscale2 values
            - Properly create the test Model, rather than manually producing the DAG and image
            - This test could be simplified to cover less edge cases, now that TestUtil tests the underling methods for a lot of cases
        """

        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Ensure the mock view returns the correct imscale2 value
        mock_view.imscale2 = 1.0

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

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

        # Set the fake chronological DAG. This Model will be technically invalid.
        model.current_model.chronological_dag = g
        # Make sure chrono new image is created. Ideally this should be tested just by Model methods, rather than manually creating this here
        write_dot(model.current_model.chronological_dag, model.current_model.get_working_directory() / "fi_new_chrono")
        # Fake the load_check so the chrono dag will get rendered, which is a bit evil.
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
            [[32.85, 72.1], "box"],  # inside the corner of the box
            [[32.75, 72.0], None],  # on the corner of  box
            [[31.75, 71.0], None],  # outside corner box
            [[59.745, 18.0], "diamond"],  # mid diamond
            [[-0.20, +0.1], "diamond"],  # inside corner diamond, would be None with non-axis aligned bounding boxes
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

            # render the chronological dag, which will also set the node coordinates using the mocked method
            model.current_model.render_chrono_graph()

            # Resize the models image, as graphviz may not be making an image that matches the placement in the hard-coded svg.
            model.current_model.chronological_image = model.current_model.chronological_image.resize(
                (int(math.ceil(scale[0])), int(math.ceil(scale[1])))
            )

            # Check with several coordinate pairs, which should miss, hit boxes, hit diamonds, or hit elipses.
            for (x, y), node in tests_coords:
                # Get the node at the specified coords, checking the returned value is as expected.
                assert presenter.nodecheck(x, y) == node

    def test_clear_results_list(self):
        """Test clear_results_list behaves as expected"""
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # The results list should be empty
        assert len(presenter.results_list) == 0

        # Call clear_results_list
        presenter.clear_results_list()

        # The results list should be empty still
        assert len(presenter.results_list) == 0

        # 3 mocked view methods should have been called
        mock_view.clear_littlecanvas3.assert_called_once()
        mock_view.clear_littlecanvas3.hide_canvas_plt()
        mock_view.clear_littlecanvas3.clear_tree_phases()

        # ---

        # Add something to the results list
        presenter.node = "foo"
        presenter.testmenu_add_to_results_list()

        # Which should now not be empty
        assert len(presenter.results_list) != 0

        # Reset the mock
        mock_view.reset_mock()

        # Call clear_results_list
        presenter.clear_results_list()

        # The results list should now be empty
        assert len(presenter.results_list) == 0

        # 3 mocked view methods should have been called
        mock_view.clear_littlecanvas3.assert_called_once()
        mock_view.clear_littlecanvas3.hide_canvas_plt()
        mock_view.clear_littlecanvas3.clear_tree_phases()

    @pytest.mark.skip(reason="test_get_hpd_interval not implemented, includes tkinter")
    def test_get_hpd_interval(self):
        """Test get_hpd_interval behaves as expected"""
        pass

    @pytest.mark.skip(reason="test_on_testmenu2 not implemented, includes tkinter")
    def test_on_testmenu2(self):
        """Test on_testmenu2 behaves as expected"""
        pass

    def test_testmenu_add_to_results_list(self):
        """Test testmenu_add_to_results_list behaves as expected

        This method updates model state, but does not update the view state. Which is triggered by the caller `on_testmenu2`
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # The results list should be empty
        assert len(presenter.results_list) == 0

        # Call testmenu_add_to_results_list
        presenter.testmenu_add_to_results_list()

        # The results list should be empty still, as no node was selected
        assert len(presenter.results_list) == 0

        # view.clear_littlecanvas3 should have been called
        mock_view.clear_littlecanvas3.assert_called_once()

        # ---

        # The results list should be empty
        assert len(presenter.results_list) == 0

        # Reset the mock
        mock_view.reset_mock()

        # Call testmenu_add_to_results_list, with a node selected
        presenter.node = "foo"
        presenter.testmenu_add_to_results_list()

        # The results list should not be empty
        assert len(presenter.results_list) != 0
        assert list(presenter.results_list.keys()) == ["foo"]

        # view.clear_littlecanvas3 should have been called
        mock_view.clear_littlecanvas3.assert_called_once()

        # ---
        # The list should only contain unique elements, and as a dictionary is used the key order (in python 3.7+) is insertion order preserving.
        # So add multiple elements, including duplicates and check the contents are as expected
        insertions = ["foo", "foo", "bar", "foo", "baz", "bar", "bar", "bar"]
        for i in insertions:
            presenter.node = i
            presenter.testmenu_add_to_results_list()
        assert list(presenter.results_list.keys()) == ["foo", "bar", "baz"]

    @pytest.mark.skip(reason="test_testmenu_get_time_elapsed_between not implemented, includes tkinter")
    def test_testmenu_get_time_elapsed_between(self):
        """Test testmenu_get_time_elapsed_between behaves as expected"""
        pass

    def test_testmenu_get_time_elapsed(self):
        """Test testmenu_get_time_elapsed behaves as expected.

        - if phase_len_nodes is empty, a node should be added and menu entry created
        - if phase_len_nodes contains 1 node, remove relevent menu entrys before creating the new one

        Todo:
            - Test (and handle) the case wehre phase_len_nodes has more than 1 element. This should not be possible in normal usage, but should probably be supported by the method.
            - Test providing the same node twice
        """
        # Setup the mock mediator, mock view and fixture-provided ProjectSelection
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatingResultsView)
        model = self.project_selection

        # Instantiate the Presenter
        presenter = DatingResultsPresenter(mock_mediator, mock_view, model)

        # ---

        # With no phase_len_nodes
        assert len(presenter.phase_len_nodes) == 0

        # Call testmenu_get_time_elapsed, with no node selected
        presenter.node = "no node"
        presenter.testmenu_get_time_elapsed()

        # There should be no nodes added, and append/remove_testmenu2_entry should not haave been called
        assert presenter.phase_len_nodes == []
        mock_view.append_testmenu2_entry.assert_not_called()
        mock_view.remove_testmenu2_entry.assert_not_called()
        mock_view.reset_mock()

        # ---

        # With no phase_len_nodes
        assert len(presenter.phase_len_nodes) == 0

        # Call testmenu_get_time_elapsed, with a node selected
        presenter.node = "foo"
        presenter.testmenu_get_time_elapsed()

        # The node should have been added, and append_testmenu2_entry called
        assert presenter.phase_len_nodes == ["foo"]
        mock_view.append_testmenu2_entry.assert_called_with("Get time elapsed between foo and another context")
        mock_view.remove_testmenu2_entry.assert_not_called()
        mock_view.reset_mock()

        # ---

        # With one phase_len_nodes
        assert len(presenter.phase_len_nodes) == 1

        # Call testmenu_get_time_elapsed, with a different node selected
        presenter.node = "bar"
        presenter.testmenu_get_time_elapsed()

        # phase_len_nodes should just contain the new node, the new test menu entry should have been added, and the old entry removed.
        assert presenter.phase_len_nodes == ["bar"]
        mock_view.append_testmenu2_entry.assert_called_with("Get time elapsed between bar and another context")
        mock_view.remove_testmenu2_entry.assert_called_with("Get time elapsed between foo and another context")
        mock_view.reset_mock()

        # ---

        # With one phase_len_nodes
        assert len(presenter.phase_len_nodes) == 1

        # Call testmenu_get_time_elapsed, with no node selected
        presenter.node = "no node"
        presenter.testmenu_get_time_elapsed()

        # The old entry should have been cleared, but no new node added
        assert presenter.phase_len_nodes == []
        mock_view.append_testmenu2_entry.assert_not_called()
        mock_view.remove_testmenu2_entry.assert_called_with("Get time elapsed between bar and another context")
        mock_view.reset_mock()

    @pytest.mark.skip(reason="test_mcmc_output not implemented, calls tkinter methods")
    def test_mcmc_output(self):
        """Test mcmc_output behaves as expected"""
        pass
