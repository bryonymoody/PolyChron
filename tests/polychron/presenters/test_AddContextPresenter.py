from unittest.mock import MagicMock, patch

from polychron.interfaces import Mediator
from polychron.models.AddContextModel import AddContextModel
from polychron.presenters.AddContextPresenter import AddContextPresenter
from polychron.views.AddContextView import AddContextView


class TestAddContextPresenter:
    """Unit tests for the AddContextPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    def test_init(self):
        """Tests the __init__ method of the AddContextPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=AddContextView)

        # Create an actual model instance of the correct type
        model = AddContextModel

        # Instantiate the Presenter
        presenter = AddContextPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that bind_ok_button was called on the view
        mock_view.bind_ok_button.assert_called_once()

        # Assert that bind_ok_button was passed 1 arguments
        args, _ = mock_view.bind_ok_button.call_args
        assert len(args) == 1

        # Assert that the single argument was a callable (i.e. a function)
        assert callable(args[0])

    def test_update_view(self):
        """Test the update view method can be called

        In this case it has no impact, to assert for, but must be defined.
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=AddContextView)

        # Create an actual model instance of the correct type
        model = AddContextModel

        # Instantiate the Presenter
        presenter = AddContextPresenter(mock_mediator, mock_view, model)

        # Call update_view, which should not raise
        presenter.update_view()
        # No view methods to check for calls to for this Presenter

    def test_on_ok(self):
        """Test the on_ok callback function

        This mocks out AddContextView.get_input to return a value, and checks the model is updated before close_view is called.
        """

        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=AddContextView)

        # Create an actual model instance of the correct type
        model = AddContextModel

        # Instantiate the Presenter
        presenter = AddContextPresenter(mock_mediator, mock_view, model)

        # Mock out the view.get_input method to return an expected value
        context_value = "foo"
        mock_view.get_input.return_value = context_value

        # Patch out PopupPresenter.close_view
        with patch("polychron.presenters.PopupPresenter.PopupPresenter.close_view") as mock_close_view:
            # Call the on_ok method
            presenter.on_ok()

            # Assert that the view's get_input method was called once
            mock_view.get_input.assert_called_once()

            # Assert that the model has been updated with the mocked get_input value
            assert presenter.model.label == context_value

            # Assert that close_view was called.
            mock_close_view.assert_called_once()
