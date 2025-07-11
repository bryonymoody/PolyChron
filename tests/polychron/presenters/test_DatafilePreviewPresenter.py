from unittest.mock import MagicMock, patch

import pandas as pd

from polychron.interfaces import Mediator
from polychron.presenters.DatafilePreviewPresenter import DatafilePreviewPresenter
from polychron.views.DatafilePreviewView import DatafilePreviewView


class TestDatafilePreviewPresenter:
    """Unit tests for the DatafilePreviewPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    def test_init(self):
        """Tests the __init__ method of the DatafilePreviewPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatafilePreviewView)

        # Construct a model instance with test data
        model = {"df": pd.DataFrame({"one": ["a", "b", "c"], "two": ["A", "B", "C"]})}

        # Instantiate the Presenter
        presenter = DatafilePreviewPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that bind_load_button was called on the view, and provided a single callable argument
        mock_view.bind_load_button.assert_called_once()
        args, _ = mock_view.bind_load_button.call_args
        assert len(args) == 1
        assert callable(args[0])

        # Assert that bind_cancel_button was called on the view, and provided a single callable argument
        mock_view.bind_cancel_button.assert_called_once()
        args, _ = mock_view.bind_cancel_button.call_args
        assert len(args) == 1
        assert callable(args[0])

    def test_update_view(self):
        """Test that update_view calls appropriate methods on the view with expected data"""

        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatafilePreviewView)

        # Construct a model instance with test data
        model = {"df": pd.DataFrame({"one": ["a", "b", "c"], "two": ["A", "B", "C"]}), "result": None}

        # Instantiate the Presenter
        presenter = DatafilePreviewPresenter(mock_mediator, mock_view, model)

        # Assert that the view's set_tree_data method gets called with the correct values
        presenter.update_view()
        mock_view.set_tree_data.assert_called_with(
            ["one", "two"], [tuple([0, ["a", "A"]]), tuple([1, ["b", "B"]]), tuple([2, ["c", "C"]])]
        )

        # If the model df is empty, assert set_tree_data was called with appropriate values
        mock_view.reset_mock()
        presenter.model = {"df": pd.DataFrame(), "result": None}
        presenter.update_view()
        mock_view.set_tree_data.assert_called_with([], [])

        # If the model has a "df" which is not a dataframe, set_tree_data should not be called.
        # This check can be removed when a specialised Model class is implemented.
        mock_view.reset_mock()
        presenter.model = {"df": {"one": ["a", "b", "c"], "two": ["A", "B", "C"]}, "result": None}
        presenter.update_view()
        mock_view.set_tree_data.assert_not_called()

        # If the model does not include a df, the method should not be called
        mock_view.reset_mock()
        presenter.model = {"result": None}
        presenter.update_view()
        mock_view.set_tree_data.assert_not_called()

    def test_on_load_button(self):
        """Test that the on_load button callback sets the correct result value in the model and closes the view."""

        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatafilePreviewView)

        # Construct a model instance with test data
        model = {"df": pd.DataFrame({"one": ["a", "b", "c"], "two": ["A", "B", "C"]}), "result": None}

        # Instantiate the Presenter
        presenter = DatafilePreviewPresenter(mock_mediator, mock_view, model)

        # Call on_load_button, which should set the model["result"] to "load" and close the view
        with patch(
            "polychron.presenters.DatafilePreviewPresenter.DatafilePreviewPresenter.close_view"
        ) as mock_close_view:
            presenter.on_load_button()
            mock_close_view.assert_called_once()
            assert "result" in presenter.model
            assert presenter.model["result"] == "load"

    def test_on_cancel_button(self):
        """Test that the on_cancel button callback sets the correct result value in the model and closes the view."""

        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=DatafilePreviewView)

        # Construct a model instance with test data
        model = {"df": pd.DataFrame({"one": ["a", "b", "c"], "two": ["A", "B", "C"]}), "result": None}

        # Instantiate the Presenter
        presenter = DatafilePreviewPresenter(mock_mediator, mock_view, model)

        # Call on_cancel_button, which should set the model["result"] to "cancel" and close the view
        with patch(
            "polychron.presenters.DatafilePreviewPresenter.DatafilePreviewPresenter.close_view"
        ) as mock_close_view:
            presenter.on_cancel_button()
            mock_close_view.assert_called_once()
            assert "result" in presenter.model
            assert presenter.model["result"] == "cancel"
