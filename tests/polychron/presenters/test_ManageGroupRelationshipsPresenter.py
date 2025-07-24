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

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that ManageGroupRelationshipsView.create_phase_boxes was called with expected data
        mock_view.create_phase_boxes.assert_called()

        # The order is currently non-deterministic, so we must compare as sets
        assert mock_view.create_phase_boxes.call_args.args[0] == ["2", "1"]

        # Assert that instance members were set as expected.

        assert presenter.prev_dict == {}
        assert presenter.post_dict == {}
        assert presenter.group_relationship_dict == {}
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

        mock_view.bind_phase_box_on_move.assert_called()
        assert len(mock_view.bind_phase_box_on_move.call_args.args) == 1
        assert callable(mock_view.bind_phase_box_on_move.call_args.args[0])

    def test_update_view(self, test_data_model_demo: Model):
        """Test update_view behaves as intended with the Demo model"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Assert update_view can be called wihtout raising any exceptions, it currently does nothing.
        presenter.update_view()

    @pytest.mark.skip(reason="test_on_move not implemented due to tkinter calls in on_move")
    def test_on_move(self, test_data_model_demo: Model):
        """Test on_move behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Call the on_move method
        presenter.on_move()

    def test_on_back(self, test_data_model_demo: Model):
        """Test on_back behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Call the on_confirm method
        presenter.on_back()

        # Assert that the view.on_back method was called
        mock_view.on_back.assert_called()
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
                {"1": (5, 228), "2": (307, 194.0)},
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
                {"1": (5, 228), "2": (231.5, 194.0)},
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
                {"1": (5, 228), "2": (382.5, 194.0)},
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
                {"1": (0, 400), "2": (100, 350.0), "3": (225.0, 300.0), "4": (325.0, 250.0)},
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
            mock_view.update_box_coords.assert_called_once_with(update_xy)
        else:
            mock_view.update_box_coords.assert_not_called()

        mock_view.on_confirm.assert_called_once()
        mock_view.update_relationships_table.assert_called_once_with(presenter.group_relationship_dict)

    @pytest.mark.skip(reason="test_full_chronograph_func not yet implemented, as it relies on values set by get_coords")
    def test_full_chronograph_func(self, test_data_model_demo: Model):
        """Test full_chronograph_func behaves as intended with the Demo model

        Todo:
            full_chronograph_func needs a check that get_coords has been called (i.e. prev_dict and post_dict are in the correct order).
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)

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
