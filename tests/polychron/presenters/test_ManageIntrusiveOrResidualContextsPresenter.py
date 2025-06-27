from unittest.mock import MagicMock, patch

from polychron.interfaces import Mediator
from polychron.models.Model import Model
from polychron.presenters.ManageGroupRelationshipsPresenter import ManageGroupRelationshipsPresenter
from polychron.presenters.ManageIntrusiveOrResidualContextsPresenter import ManageIntrusiveOrResidualContextsPresenter
from polychron.views.ManageGroupRelationshipsView import ManageGroupRelationshipsView
from polychron.views.ManageIntrusiveOrResidualContextsView import ManageIntrusiveOrResidualContextsView


class TestManageIntrusiveOrResidualContextsPresenter:
    """Unit tests for the ManageIntrusiveOrResidualContextsPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.

    Tests use the test_data_model_demo fixture which provides a semi-populated Model instance

    Todo:
        - Expand tests to operate on a range of Model instances in various states (loaded / not loaded files etc)
    """

    def test_init(self, test_data_model_demo: Model):
        """Tests the __init__ method of the ManageIntrusiveOrResidualContextsPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageIntrusiveOrResidualContextsView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageIntrusiveOrResidualContextsPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that view.bind_back_button was called with a callable
        mock_view.bind_back_button.assert_called_once()
        assert len(mock_view.bind_back_button.call_args.args) == 1
        assert callable(mock_view.bind_back_button.call_args.args[0])

        # Assert that view.bind_proceed_button was called with a callable
        mock_view.bind_proceed_button.assert_called_once()
        assert len(mock_view.bind_proceed_button.call_args.args) == 1
        assert callable(mock_view.bind_proceed_button.call_args.args[0])

        # Assert that view.create_dropdowns was called with expected data
        mock_view.create_dropdowns.assert_called_with(model.residual_contexts, model.intrusive_contexts)

    def test_update_view(self, test_data_model_demo: Model):
        """Test update_view behaves as intended with the Demo model"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageIntrusiveOrResidualContextsView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageIntrusiveOrResidualContextsPresenter(mock_mediator, mock_view, model)

        # Assert update_view can be called wihtout raising any exceptions, it currently does nothing.
        presenter.update_view()

    def test_on_back(self, test_data_model_demo: Model):
        """Test on_back behaves as intended with the Demo model"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageIntrusiveOrResidualContextsView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageIntrusiveOrResidualContextsPresenter(mock_mediator, mock_view, model)

        # Patch out PopupPresenter.close_view
        with patch("polychron.presenters.PopupPresenter.PopupPresenter.close_view") as mock_close_view:
            # Call the on_back method
            presenter.on_back()

            # Assert that close_view was called.
            mock_close_view.assert_called_once()

            # This doesn't currently mutate state at all, but should probably reset/clear some Model properties?

    @patch("polychron.presenters.ManageIntrusiveOrResidualContextsPresenter.ManageGroupRelationshipsPresenter")
    @patch("polychron.presenters.ManageIntrusiveOrResidualContextsPresenter.ManageGroupRelationshipsView")
    def test_on_proceed(
        self, MockManageGroupRelationshipsView, MockManageGroupRelationshipsPresenter, test_data_model_demo: Model
    ):
        """Test on_proceed behaves as intended with the Demo model

        This instantiates a separate presenter and makes it visible, however created Presenter is not accessible outside of the method, so we can only check that the patched and moccked constructors were called.

        Todo:
            - Test with alternate values from get_resid_dropdown_selections and get_intru_dropdown_selections
        """
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=ManageIntrusiveOrResidualContextsView)

        # Patch view.get_resid_dropdown_selections view.get_intru_dropdown_selections to return specific test values
        expected_residual_context_types = {"": ""}
        expected_intru_context_types = {"": ""}
        mock_view.get_resid_dropdown_selections.return_value = expected_residual_context_types
        mock_view.get_intru_dropdown_selections.return_value = expected_intru_context_types

        # Patch mock_view to have a parent member, which is accessed directly.
        mock_view.parent = MagicMock()

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = ManageIntrusiveOrResidualContextsPresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked child/popup View
        mock_child_view_instance = MagicMock(spec=ManageGroupRelationshipsView)
        MockManageGroupRelationshipsView.return_value = mock_child_view_instance

        # Prepare the Mocked child/popup Presenter, including explicit setting of a mocked view member
        mock_child_presenter_instance = MagicMock(spec=ManageGroupRelationshipsPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockManageGroupRelationshipsPresenter.return_value = mock_child_presenter_instance

        # Patch out PopupPresenter.close_view
        with patch("polychron.presenters.PopupPresenter.PopupPresenter.close_view") as mock_close_view:
            # Call the on_proceed method
            presenter.on_proceed()

            # Assert that the Model instance was updated
            assert model.residual_context_types == expected_residual_context_types
            assert model.intrusive_context_types == expected_intru_context_types

            # Assert that the patched/mocked child/popup presenter and view were created
            MockManageGroupRelationshipsView.assert_called_once()
            MockManageGroupRelationshipsPresenter.assert_called_once()

            # Assert that the mocked child view was lifted (made visible and on top)
            mock_child_presenter_instance.view.lift.assert_called_once()

            # Assert that the parent view was made to wait
            mock_view.wait_window.assert_called_with(mock_child_presenter_instance.view)

            # Assert that close_view was called.
            mock_close_view.assert_called_once()

            # Assert that the parent popup was also closed @todo
            mock_view.parent.destroy.assert_called_once()
