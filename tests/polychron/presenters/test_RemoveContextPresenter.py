from unittest.mock import MagicMock, patch

from polychron.interfaces import Mediator
from polychron.presenters.RemoveContextPresenter import RemoveContextPresenter
from polychron.views.RemoveContextView import RemoveContextView


class TestRemoveContextPresenter:
    """Unit tests for the RemoveContextPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    def test_init(self):
        """Tests the __init__ method of the RemoveContextPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=RemoveContextView)

        # Create an actual model instance of the correct type
        model = {"context": "foo", "reason": None}

        # Instantiate the Presenter
        presenter = RemoveContextPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that bind_ok_button was called on the view
        mock_view.bind_ok_button.assert_called_once()

        # Assert that bind_ok_button was passed 1 argument and it was callable
        assert len(mock_view.bind_ok_button.call_args.args) == 1
        # Assert that the single argument was a callable (i.e. a function)
        assert callable(mock_view.bind_ok_button.call_args.args[0])

        # Assert that the view.update_label should have been called with the model's "context" value (via the update_view method)
        mock_view.update_label.assert_called_with(model["context"])

    def test_update_view(self):
        """Test the update view method can be called"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=RemoveContextView)

        # Create an actual model instance of the correct type
        model = {"context": "foo", "reason": None}

        # Instantiate the Presenter
        presenter = RemoveContextPresenter(mock_mediator, mock_view, model)

        # Call update_view, which should not raise
        presenter.update_view()

        # Assert that the view.update_label should have been called with the model's "context" value
        mock_view.update_label.assert_called_with(model["context"])

    def test_on_ok_button(self):
        """Test the on_ok_button callback function

        This mocks out RemoveContextView.get_reason to return a value, and checks the model is updated before close_view is called.
        """

        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=RemoveContextView)

        # Create an actual model instance of the correct type
        model = {"context": "foo", "reason": None}

        # Instantiate the Presenter
        presenter = RemoveContextPresenter(mock_mediator, mock_view, model)

        # Mock out the view.get_reason method to return an expected value
        reason_value = "bar"
        mock_view.get_reason.return_value = reason_value

        # Patch out PopupPresenter.close_view
        with patch("polychron.presenters.PopupPresenter.PopupPresenter.close_view") as mock_close_view:
            # Call the on_ok_button method
            presenter.on_ok_button()

            # Assert that the view's get_reason method was called once
            mock_view.get_reason.assert_called_once()

            # Assert that the model has been updated with the mocked get_reason value
            assert presenter.model["reason"] == reason_value

            # Assert that close_view was called.
            mock_close_view.assert_called_once()
