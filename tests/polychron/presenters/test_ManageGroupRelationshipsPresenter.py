from unittest.mock import MagicMock

import networkx as nx
import pytest

from polychron.interfaces import Mediator
from polychron.models.Model import Model
from polychron.presenters.ManageGroupRelationshipsPresenter import ManageGroupRelationshipsPresenter
from polychron.views.ManageGroupRelationshipsView import ManageGroupRelationshipsView


class TestManageGroupRelationshipsPresenter:
    """Unit tests for the ManageGroupRelationshipsPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    def test_init(self, test_data_model_demo: Model):
        """Tests the __init__ method of the ManageGroupRelationshipsPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected

        Todo:
            - Test with more than one Model instance, to cover additional branches / edge cases.
                - Not all datafiles opened/loaded
                - Test with model.residual_contexts set
                - Test with model.intrusive_contexts set
                - Test with removed edges/nodes
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)
        mock_view.get_group_canvas_dimensions.return_value = (1000, 1000)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that ManageGroupRelationshipsView.create_group_boxes was called with expected data
        mock_view.create_group_boxes.assert_called()
        assert isinstance(mock_view.create_group_boxes.call_args.args[0], dict)
        assert "2" in mock_view.create_group_boxes.call_args.args[0]
        assert "1" in mock_view.create_group_boxes.call_args.args[0]

        # Assert that instance members were set as expected.

        assert presenter.prev_dict == {}
        assert presenter.post_dict == {}
        assert presenter.group_relationship_dict == {("2", "1"): None}
        # Just check the dag is an instance of the right type for now.
        assert isinstance(presenter.dag, nx.DiGraph)
        # context_no_unordered is ordered based on nx.DiGraph.nodes, which appears non-deterministic even for the same inputs (it is documented as being set-like, not list-like), so the comparison must be as sets
        assert set(presenter.context_no_unordered) == set(["a", "b", "c = d", "e", "f", "g"])
        # There are no residual or intrusive nodes at this point
        assert presenter.context_types == ["normal" for _ in presenter.context_no_unordered]
        assert presenter.removed_nodes_tracker == []

        # Assert that the table was updated.
        mock_view.update_relationships_table.assert_called_once()

        # Assert that button callbacks were bound with callables
        mock_view.bind_confirm_button.assert_called()
        assert len(mock_view.bind_confirm_button.call_args.args) == 1
        assert callable(mock_view.bind_confirm_button.call_args.args[0])

        mock_view.bind_render_button.assert_called()
        assert len(mock_view.bind_render_button.call_args.args) == 1
        assert callable(mock_view.bind_render_button.call_args.args[0])

        mock_view.bind_change_button.assert_called()
        assert len(mock_view.bind_change_button.call_args.args) == 1
        assert callable(mock_view.bind_change_button.call_args.args[0])

        mock_view.bind_group_box_mouse_events.assert_called()
        assert len(mock_view.bind_group_box_mouse_events.call_args.args) == 3
        assert callable(mock_view.bind_group_box_mouse_events.call_args.args[0])
        assert callable(mock_view.bind_group_box_mouse_events.call_args.args[1])
        assert callable(mock_view.bind_group_box_mouse_events.call_args.args[2])

    def test_update_view(self, test_data_model_demo: Model):
        """Test update_view behaves as intended with the Demo model"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)
        mock_view.get_group_canvas_dimensions.return_value = (1000, 1000)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Assert update_view can be called wihtout raising any exceptions, it currently does nothing.
        presenter.update_view()

    def test_compute_box_placement(self, test_data_model_demo: Model):
        """Test compute_box_placement produces expected results for the demo model

        Todo:
            - Expand test coverage to include a wider range of models
        """
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)
        mock_view.get_group_canvas_dimensions.return_value = (1000, 1000)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Call the compute_box_placement method
        boxes = presenter.compute_box_placement()

        # Given the fixed/mocked dimensions, we can check for exact box placement
        expected_boxes = {"1": (50.0, 500.0, 400.0, 48), "2": (550.0, 452.0, 400.0, 48)}
        for group in boxes:
            assert group in expected_boxes
            assert boxes[group] == pytest.approx(expected_boxes[group])

    def test_on_box_mouse_press(self, test_data_model_demo: Model):
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)
        mock_view.get_group_canvas_dimensions.return_value = (1000, 1000)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Call the on_box_mouse_press method
        mock_event = MagicMock()
        mock_event.x = 12
        mock_event.y = 24
        mock_event.widget = object()
        presenter.on_box_mouse_press(mock_event)

        # Assert private members have been reset
        assert presenter._ManageGroupRelationshipsPresenter__group_box_drag_x == 12
        assert presenter._ManageGroupRelationshipsPresenter__group_box_drag_y == 24
        assert isinstance(presenter._ManageGroupRelationshipsPresenter__group_box_widget, object)

    @pytest.mark.skip(reason="test_on_box_mouse_move not implemented due to tkinter calls in on_box_mouse_move")
    def test_on_box_mouse_move(self, test_data_model_demo: Model):
        pass

    def test_on_box_mouse_release(self, test_data_model_demo: Model):
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)
        mock_view.get_group_canvas_dimensions.return_value = (1000, 1000)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Call the on_box_mouse_release method
        mock_event = MagicMock()
        presenter.on_box_mouse_release(mock_event)

        # Assert private members have been reset
        assert presenter._ManageGroupRelationshipsPresenter__group_box_drag_x is None
        assert presenter._ManageGroupRelationshipsPresenter__group_box_drag_y is None
        assert presenter._ManageGroupRelationshipsPresenter__group_box_widget is None

    def test_on_back(self, test_data_model_demo: Model):
        """Test on_back behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)
        mock_view.get_group_canvas_dimensions.return_value = (1000, 1000)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Call the on_back method
        presenter.on_back()

        # Assert that the view.on_back method was called
        mock_view.layout_step_one.assert_called()
        # Assert that the view.update_relationships_table method was called
        mock_view.update_relationships_table.assert_called()

    @pytest.mark.parametrize(
        ("mock_box_properties", "update_xy", "expect_prev", "expect_post", "expect_group_relationships"),
        [
            # demo, with abutting group placement
            (
                {
                    "2": (308, 189, 302, 34),
                    "1": (5, 228, 302, 34),
                },
                {"1": (5, 228), "2": (307, 194)},
                {"2": "abutting"},
                {"1": "abutting"},
                {("2", "1"): "abutting"},
            ),
            # demo, with overlapping group placement
            (
                {
                    "2": (179, 187, 302, 34),
                    "1": (5, 228, 302, 34),
                },
                {"1": (5, 228), "2": (231.5, 194)},
                {"2": "overlap"},
                {"1": "overlap"},
                {("2", "1"): "overlap"},
            ),
            # demo, with gap group placement
            (
                {
                    "2": (410, 189, 302, 34),
                    "1": (5, 228, 302, 34),
                },
                {"1": (5, 228), "2": (382.5, 194)},
                {"2": "gap"},
                {"1": "gap"},
                {("2", "1"): "gap"},
            ),
            # Manual values, 4 groups. 1 oldest, 4 youngest. abutting, gap, overlap
            (
                {
                    "4": (300, 100, 100, 50),
                    "3": (250, 200, 100, 50),
                    "2": (100, 300, 100, 50),
                    "1": (0, 400, 100, 50),
                },
                {"1": (0, 400), "2": (100, 350), "3": (225.0, 300), "4": (300.0, 250)},
                {"2": "abutting", "3": "gap", "4": "overlap"},
                {"1": "abutting", "2": "gap", "3": "overlap"},
                {("2", "1"): "abutting", ("3", "2"): "gap", ("4", "3"): "overlap"},
            ),
            # Manual values, single group.
            (
                {
                    "1": (5, 228, 302, 34),
                },
                {"1": (5, 228)},
                {},
                {},
                {},
            ),
            # Manual values, 0 groups
            (
                {},
                {},
                {},
                {},
                {},
            ),
        ],
    )
    def test_get_coords(
        self,
        mock_box_properties: dict[str, tuple[float, float, float, float]],
        update_xy: dict[str, tuple[float, float]],
        expect_prev: dict[str, str],
        expect_post: dict[str, str],
        expect_group_relationships: dict[tuple[str, str], str],
        test_data_model_demo: Model,
    ):
        """Test get_coords behaves as intended with the Demo model

        Relies on mocking/patching `ManageGroupRelationshipsView.get_group_box_properties` to return an expected set of coordinates without requiring a displayed tkinter window for valid coordinates to be produced

        Todo:
            - Test/handle exactly matching y coordinates
            - Test/handle exactly matching x coordinates
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)
        mock_view.get_group_canvas_dimensions.return_value = (1000, 1000)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Mock out view get_group_box_properties to include the groups in the Model at arbitrary coordinates / dimensions for a specific case
        mock_view.reset_mock()
        mock_view.get_group_box_properties.return_value = mock_box_properties

        # Call the get_coords method
        presenter.get_coords()

        # Check that the prev, post and group relationships dicts are now as expected
        assert presenter.prev_dict == expect_prev
        assert presenter.post_dict == expect_post
        assert presenter.group_relationship_dict == expect_group_relationships

        # Assert that the view was updated, if more than one group box was expected to be present
        if len(mock_box_properties) > 1:
            mock_view.update_box_coords.assert_called_once()
            arg = mock_view.update_box_coords.call_args.args[0]
            assert len(arg) == len(update_xy)
            assert arg.keys() == update_xy.keys()
            for k in arg:
                assert arg[k] == pytest.approx(update_xy[k])
        else:
            mock_view.update_box_coords.assert_not_called()

        mock_view.layout_step_two.assert_called_once()
        mock_view.update_relationships_table.assert_called_once_with(presenter.group_relationship_dict)

    @pytest.mark.skip(reason="test_full_chronograph_func not yet implemented")
    def test_full_chronograph_func(self, test_data_model_demo: Model):
        """Test full_chronograph_func behaves as intended with the Demo model

        Todo:
            full_chronograph_func needs a check that get_coords has been called (i.e. prev_dict and post_dict are in the correct order).
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)
        mock_view.get_group_canvas_dimensions.return_value = (1000, 1000)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Call the full_chronograph_func
        presenter.full_chronograph_func()

        # @todo assertions

    def test_close_window(self, test_data_model_demo: Model):
        """Test close_window behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)
        mock_view.get_group_canvas_dimensions.return_value = (1000, 1000)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Assert that close_window calls the mocked view.destroy
        # The reason parameter is optional, but required for duck-typing as this can also be used as a Mediator
        # destroy is inherrited from tk.TopLevel, via PopupView
        presenter.close_window()
        assert mock_view.destroy.call_count == 1
        presenter.close_window("foo")
        assert mock_view.destroy.call_count == 2
