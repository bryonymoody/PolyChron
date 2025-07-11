from typing import Any
from unittest.mock import MagicMock

from polychron.interfaces import Mediator
from polychron.presenters.FramePresenter import FramePresenter
from polychron.views.FrameView import FrameView


class ConcreteFramePresenter(FramePresenter[FrameView, Any]):
    """A concrete subclass of FramePresenter to enable testing of non-abstract FramePresenter methods"""

    def update_view(self):
        """Concrete implementation of FramePresenter.update_view, which does nothing"""
        return super().update_view()


class TestFramePresenter:
    """Unit tests for the FramePresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    def test_init(self):
        """Test the __init__ method sets member variables as expected"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=FrameView)

        # Construct a model instance with test data, this can be Any type
        model = None

        # Instantiate the concrete Presenter
        presenter = ConcreteFramePresenter(mock_mediator, mock_view, model)

        # Assert the properties are correctly set
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

    def test_update_view(self):
        """Test that update_view exists and can be called without raising any exceptions"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=FrameView)

        # Construct a model instance with test data, this can be Any type
        model = None

        # Instantiate the concrete Presenter
        presenter = ConcreteFramePresenter(mock_mediator, mock_view, model)

        # Call update_view, which should not raise any exceptions, but also has no side-effects to detect
        presenter.update_view()

    def test_get_window_title_suffix(self):
        """Test the get_window_title_suffix method. This is non-abstract and the default implementation just returns None"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=FrameView)

        # Construct a model instance with test data, this can be Any type
        model = None

        # Instantiate the concrete Presenter
        presenter = ConcreteFramePresenter(mock_mediator, mock_view, model)

        assert presenter.get_window_title_suffix() is None
