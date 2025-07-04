from typing import Any
from unittest.mock import MagicMock

from polychron.interfaces import Mediator
from polychron.presenters.PopupPresenter import PopupPresenter
from polychron.views.PopupView import PopupView


class ConcretePopupPresenter(PopupPresenter[PopupView, Any]):
    """A concrete subclass of PopupPresenter to enable testing of non-abstract PopupPresenter methods"""

    def update_view(self):
        """Concrete implementation of PopupPresenter.update_view, which does nothing"""
        return super().update_view()


class TestPopupPresenter:
    """Unit tests for the PopupPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    def test_init(self):
        """Test the __init__ method sets member variables as expected"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=PopupView)

        # Construct a model instance with test data, this can be Any type
        model = None

        # Instantiate the concrete Presenter
        presenter = ConcretePopupPresenter(mock_mediator, mock_view, model)

        # Assert the properties are correctly set
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that the (mock) view had keybind and protocols registered.
        mock_view.register_keybinds.assert_called()
        mock_view.register_protocols.assert_called()

    def test_update_view(self):
        """Test that update_view exists and can be called without raising any exceptions"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=PopupView)

        # Construct a model instance with test data, this can be Any type
        model = None

        # Instantiate the concrete Presenter
        presenter = ConcretePopupPresenter(mock_mediator, mock_view, model)

        # Call update_view, which should not raise any exceptions, but also has no side-effects to detect
        presenter.update_view()

    def test_display_view(self):
        """Test that display_view would havce called the expeced methods on the mocked view instance"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=PopupView)

        # Construct a model instance with test data, this can be Any type
        model = None

        # Instantiate the concrete Presenter
        presenter = ConcretePopupPresenter(mock_mediator, mock_view, model)

        # Call the method being tested
        presenter.display_view()

        # Test that the appropriate tkinter methods were called. Ideally this should be abstracted away into PopupView
        mock_view.deiconify.assert_called()
        mock_view.lift.assert_called()

    def test_minimise_view(self):
        """Test that minimise_view would havce called the expeced methods on the mocked view instance"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=PopupView)

        # Construct a model instance with test data, this can be Any type
        model = None

        # Instantiate the concrete Presenter
        presenter = ConcretePopupPresenter(mock_mediator, mock_view, model)

        # Call the method being tested
        presenter.minimise_view()

        # Test that the appropriate tkinter methods were called. Ideally this should be abstracted away into PopupView
        mock_view.iconify.assert_called()

    def test_hide_view(self):
        """Test that hide_view would havce called the expeced methods on the mocked view instance"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=PopupView)

        # Construct a model instance with test data, this can be Any type
        model = None

        # Instantiate the concrete Presenter
        presenter = ConcretePopupPresenter(mock_mediator, mock_view, model)

        # Call the method being tested
        presenter.hide_view()

        # Test that the appropriate tkinter methods were called. Ideally this should be abstracted away into PopupView
        mock_view.withdraw.assert_called()

    def test_close_view(self):
        """Test that close_view would havce called the expeced methods on the mocked view instance"""
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=PopupView)

        # Construct a model instance with test data, this can be Any type
        model = None

        # Instantiate the concrete Presenter
        presenter = ConcretePopupPresenter(mock_mediator, mock_view, model)

        # Call the method being tested
        presenter.close_view()

        # Test that the appropriate tkinter methods were called. Ideally this should be abstracted away into PopupView
        mock_view.destroy.assert_called()

        # Close_View can also take an argument, so it can be directly bound via Tk.Toplevel.bind(), although a lambda could be used to discard the event in that case
        mock_view.reset_mock()
        presenter.close_view("foo")
        mock_view.destroy.assert_called()
