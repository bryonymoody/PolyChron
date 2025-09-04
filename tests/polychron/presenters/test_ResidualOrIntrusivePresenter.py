from unittest.mock import MagicMock, patch

import pytest

from polychron.interfaces import Mediator
from polychron.models.Model import Model
from polychron.presenters.ManageIntrusiveOrResidualContextsPresenter import ManageIntrusiveOrResidualContextsPresenter
from polychron.presenters.ResidualOrIntrusivePresenter import ResidualOrIntrusivePresenter
from polychron.views.ManageIntrusiveOrResidualContextsView import ManageIntrusiveOrResidualContextsView
from polychron.views.ResidualOrIntrusiveView import ResidualOrIntrusiveView


class TestResidualOrIntrusivePresenter:
    """Unit tests for the ResidualOrIntrusivePresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.

    Tests use the test_data_model_demo fixture which provides a semi-populated Model instance

    Todo:
        - Expand tests to operate on a range of Model instances in various states (loaded / not loaded files etc)
        - load_graph is patched out and skipped from testing for now due to tkinter/view leakage.
    """

    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_init(self, mock_load_graph, test_data_model_demo: Model):
        """Tests the __init__ method of the ResidualOrIntrusivePresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert the current mode of the presenter is the expected default value
        assert presenter.mode is None

        # Assert that view.bind_residual_mode_button was called with a callable
        mock_view.bind_residual_mode_button.assert_called_once()
        assert len(mock_view.bind_residual_mode_button.call_args.args) == 1
        assert callable(mock_view.bind_residual_mode_button.call_args.args[0])

        # Assert that view.bind_intrusive_mode_button was called with a callable
        mock_view.bind_intrusive_mode_button.assert_called_once()
        assert len(mock_view.bind_intrusive_mode_button.call_args.args) == 1
        assert callable(mock_view.bind_intrusive_mode_button.call_args.args[0])

        # Assert that view.bind_proceed_button was called with a callable
        mock_view.bind_proceed_button.assert_called_once()
        assert len(mock_view.bind_proceed_button.call_args.args) == 1
        assert callable(mock_view.bind_proceed_button.call_args.args[0])

        # Assert that view.bind_graphcanvas_events was called with 4 callables
        mock_view.bind_graphcanvas_events.assert_called_once()
        assert len(mock_view.bind_graphcanvas_events.call_args.args) == 4
        for arg in mock_view.bind_graphcanvas_events.call_args.args:
            assert callable(arg)

        # Todo: In this case the model includes a stratigraphic_dag, so check some variables
        # assert model.stratigraphic_dag is not None
        # mock_view.show_image2.assert_called()

        # Assert that update_view was called, via it's side-effects
        mock_view.set_residual_mode_button_background.assert_called()
        mock_view.set_intrusive_mode_button_background.assert_called()
        mock_view.set_intru_label_text.assert_called()
        mock_view.set_resid_label_text.assert_called()

    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_update_view(self, mock_load_graph, test_data_model_demo: Model):
        """Test update_view behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Call update_view with default values, check it calls the expected methods on teh view
        presenter.update_view()
        mock_view.set_residual_mode_button_background.assert_called_with("light gray")
        mock_view.set_intrusive_mode_button_background.assert_called_with("light gray")
        mock_view.set_intru_label_text.assert_called_with([])
        mock_view.set_resid_label_text.assert_called_with([])
        mock_view.reset_mock()

        # Call update_view with mode="resid" values, check it calls the expected methods on teh view
        presenter.mode = "resid"
        presenter.update_view()
        mock_view.set_residual_mode_button_background.assert_called_with("orange")
        mock_view.set_intrusive_mode_button_background.assert_called_with("light gray")
        mock_view.set_intru_label_text.assert_called()
        mock_view.set_resid_label_text.assert_called()
        mock_view.reset_mock()

        # Call update_view with mode = "intru", check it calls the expected methods on teh view
        presenter.mode = "intru"
        presenter.update_view()
        mock_view.set_residual_mode_button_background.assert_called_with("light gray")
        mock_view.set_intrusive_mode_button_background.assert_called_with("lightblue")
        mock_view.set_intru_label_text.assert_called()
        mock_view.set_resid_label_text.assert_called()
        mock_view.reset_mock()

        # Call update_view with a model containing some intrusive and residual contexts
        intrusives = ["c", "d"]
        model.intrusive_contexts = intrusives
        residuals = ["a", "b"]
        model.residual_contexts = residuals
        presenter.update_view()
        mock_view.set_residual_mode_button_background.assert_called()
        mock_view.set_intrusive_mode_button_background.assert_called()
        mock_view.set_intru_label_text.assert_called_with(intrusives)
        mock_view.set_resid_label_text.assert_called_with(residuals)
        mock_view.reset_mock()

    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_set_mode(self, mock_load_graph, test_data_model_demo: Model):
        """Test set_mode behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Assert the presenter mode is updated correctly for all accepted values
        presenter.set_mode("resid")
        assert presenter.mode == "resid"
        presenter.set_mode("intru")
        assert presenter.mode == "intru"
        presenter.set_mode(None)
        assert presenter.mode is None

        # Assert a ValueError is raised if an invalid mode is used
        with pytest.raises(ValueError, match="invalid set_mode value 'invalid_mode'"):
            presenter.set_mode("invalid_mode")

    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_on_resid_button(self, mock_load_graph, test_data_model_demo: Model):
        """Test on_resid_button behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Assert the presenter mode is updated correctly by on_resid_button
        presenter.on_resid_button()
        assert presenter.mode == "resid"

    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_on_intru_button(self, mock_load_graph, test_data_model_demo: Model):
        """Test on_intru_button behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Assert the presenter mode is updated correctly by on_intru_button
        presenter.on_intru_button()
        assert presenter.mode == "intru"

    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    @patch("polychron.presenters.ResidualOrIntrusivePresenter.ManageIntrusiveOrResidualContextsPresenter")
    @patch("polychron.presenters.ResidualOrIntrusivePresenter.ManageIntrusiveOrResidualContextsView")
    def test_on_proceed(
        self,
        MockManageIntrusiveOrResidualContextsView,
        MockManageIntrusiveOrResidualContextsPresenter,
        mock_load_graph,
        test_data_model_demo: Model,
    ):
        """Test on_proceed behaves as intended with the Demo model

        This instantiates a separate presenter and makes it visible, however created Presenter is not accessible outside of the method, so we can only check that the patched and moccked constructors were called.
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Patch mock_view to have a parent member, which is accessed directly.
        mock_view.parent = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked child/popup View
        mock_child_view_instance = MagicMock(spec=ManageIntrusiveOrResidualContextsView)
        MockManageIntrusiveOrResidualContextsView.return_value = mock_child_view_instance

        # Prepare the Mocked child/popup Presenter, including explicit setting of a mocked view member
        mock_child_presenter_instance = MagicMock(spec=ManageIntrusiveOrResidualContextsPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockManageIntrusiveOrResidualContextsPresenter.return_value = mock_child_presenter_instance

        # Call the on_proceed method
        presenter.on_proceed()

        # Assert that the patched/mocked child/popup presenter and view were created
        MockManageIntrusiveOrResidualContextsView.assert_called_once()
        MockManageIntrusiveOrResidualContextsPresenter.assert_called_once()

        # Assert that the mocked child view was lifted (made visible and on top) and a wait was triggered
        mock_child_presenter_instance.display_view.assert_called_with(wait=True)

    @pytest.mark.skip(reason="test_move_from2 not implemented due to tkinter leak")
    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_move_from2(self, mock_load_graph, test_data_model_demo: Model):
        """Test move_from2 behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Assert move_from2 behaves as expected when called
        presenter.move_from2()

    @pytest.mark.skip(reason="test_move_to2 not implemented due to tkinter leak")
    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_move_to2(self, mock_load_graph, test_data_model_demo: Model):
        """Test move_to2 behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Assert move_to2 behaves as expected when called
        presenter.move_to2()

    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_on_wheel2(self, mock_load_graph, test_data_model_demo: Model):
        """Test on_wheel2 behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Assert on_wheel2 behaves as expected when called
        event = None
        presenter.on_wheel2(event)
        mock_view.wheel2.assert_called_with(event)

    @pytest.mark.skip(reason="test_resid_node_click not implemented due to tkinter leak")
    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_resid_node_click(self, mock_load_graph, test_data_model_demo: Model):
        """Test resid_node_click behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Test the resid_node_click behaves as expected
        event = None
        presenter.resid_node_click(event)

    @pytest.mark.skip(reason="test_nodecheck not implemented due to tkinter leak")
    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_nodecheck(self, mock_load_graph, test_data_model_demo: Model):
        """Test nodecheck behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Test the nodecheck behaves as expected
        event = None
        presenter.nodecheck(event)

    @pytest.mark.skip(reason="test_loadgraph not implemented due to tkinter leak")
    @patch(__name__ + ".ResidualOrIntrusivePresenter.load_graph")  # todo remove this temporary patch
    def test_loadgraph(self, mock_load_graph, test_data_model_demo: Model):
        """Test loadgraph behaves as intended with the Demo model"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ResidualOrIntrusiveView)
        # MagicMock with spec= does not set member variables, which need explicit mocking
        mock_view.graphcanvas = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Todo/temp: force the stratigraphic_dag to be None, to avoid mocking issues
        model.stratigraphic_dag = None

        # Instantiate the Presenter
        presenter = ResidualOrIntrusivePresenter(mock_mediator, mock_view, model)

        # Test the loadgraph behaves as expected
        event = None
        presenter.loadgraph(event)
