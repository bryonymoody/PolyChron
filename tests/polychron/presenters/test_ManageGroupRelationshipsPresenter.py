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
        assert set(mock_view.create_phase_boxes.call_args.args[0]) == set(["1", "2"])

        # Assert that instance members were set as expected.

        assert presenter.prev_dict == {}
        assert presenter.post_dict == {}
        assert presenter.menudict == {}
        # Just check the graphcopy is an instance of the right type for now.
        assert isinstance(presenter.graphcopy, nx.DiGraph)
        assert presenter.prev_group == []
        assert presenter.post_group == []
        assert presenter.phi_ref == []
        # context_no_unordered is ordered based on nx.DiGraph.nodes, which appears non-deterministic even for the same inputs (it is documented as being set-like, not list-like), so the comparison must be as sets
        assert set(presenter.context_no_unordered) == set(["a", "b", "c = d", "e", "f", "g"])
        # There are no residual or intrusive nodes at this point
        assert presenter.context_types == ["normal" for _ in presenter.context_no_unordered]
        assert presenter.removed_nodes_tracker == []

        # Assert that the table was updated.
        mock_view.update_tree_2col.assert_called_with(model.group_relationships)

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

    @pytest.mark.skip(reason="test_on_confirm not implemented due to tkinter calls in get_coords")
    def test_on_confirm(self, test_data_model_demo: Model):
        """Test on_confirm behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Call the on_confirm method
        presenter.on_confirm()

        # Assert that the view.on_confirm method was called
        mock_view.on_confirm.assert_called()
        # Assert that the view.update_tree_3col method was called
        mock_view.update_tree_3col.assert_called()

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

        # Call the on_confirm method
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
        # Assert that the view.update_tree_2col method was called
        mock_view.update_tree_2col.assert_called()

    @pytest.mark.skip(reason="test_get_coords not implemented due to tkinter calls in get_coords")
    def test_get_coords(self, test_data_model_demo: Model):
        """Test get_coords behaves as intended with the Demo model

        Todo:
            - ManageGroupRelationshipsPresenter.get_phase_boxes should be modified to return custom data strucures rather than tkinter objects, so that tkinter methods are not required in the Presenter, especially when the coordinates returned would  be incorrect in tkinter without a visible window.
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageGroupRelationshipsView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageGroupRelationshipsPresenter(mock_mediator, mock_view, model)

        # Call the get_coords method
        presenter.get_coords()

        # @todo

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
