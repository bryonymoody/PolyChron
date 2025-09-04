from unittest.mock import MagicMock, patch

from polychron.interfaces import Mediator
from polychron.models.ProjectSelection import ProjectSelection
from polychron.presenters.ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter
from polychron.presenters.SplashPresenter import SplashPresenter
from polychron.views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from polychron.views.SplashView import SplashView


class TestSplashPresenter:
    """Unit tests for the SplashPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    def test_init(self, tmp_path):
        """Tests the __init__ method of the SplashPresenter class.

        Checks that the presenter has the expected values after initialisation, and that SplashView.view.build_file_menu was called with compatible paramters.
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=SplashView)

        # Create an actual model instance of the correct type
        model = ProjectSelection(tmp_path / "projects")

        # Instantiate the SplashPresenter
        presenter = SplashPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # Assert that build_file_menu was called on the view
        mock_view.build_file_menu.assert_called_once()

        # Assert that build_file_menu was passed 1 arguments
        args, _ = mock_view.build_file_menu.call_args
        assert len(args) == 1

        # Assert that the 0th argument recieved a list of 2 items. This may be more specific than required.
        menu_items = args[0]
        assert isinstance(menu_items, list)
        assert len(menu_items) == 2
        # Assert that each menu item is None or is a tuple of a str and a callable
        for menu_item in menu_items:
            assert menu_item is None or (
                isinstance(menu_item, tuple)
                and len(menu_item) == 2
                and isinstance(menu_item[0], str)
                and callable(menu_item[1])
            )

    def test_update_view(self, tmp_path):
        """Test the update view method can be called

        In this case it has no impact, to assert for, but must be defined.
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=SplashView)

        # Create an actual model instance of the correct type
        model = ProjectSelection(tmp_path / "projects")

        # Instantiate the SplashPresenter
        presenter = SplashPresenter(mock_mediator, mock_view, model)

        # Call update_view, which should not raise
        presenter.update_view()
        # No view methods to check for calls to for this Presenter

    @patch("polychron.presenters.SplashPresenter.ProjectSelectProcessPopupPresenter")
    @patch("polychron.presenters.SplashPresenter.ProjectSelectProcessPopupView")
    def test_on_select_project(
        self, MockProjectSelectProcessPopupView, MockProjectSelectProcessPopupPresenter, tmp_path
    ):
        """Test the on_select_project callback function

        This instantiates a separate presenter and makes it visible, however created Presenter is not accessible outside of the method, so we can only check that the patched and mocked constructors were called.
        """

        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=SplashView)

        # Create an actual model instance of the correct type
        model = ProjectSelection(tmp_path / "projects")

        # Instantiate the SplashPresenter
        presenter = SplashPresenter(mock_mediator, mock_view, model)

        # Prepare the Mocked View
        mock_child_view_instance = MagicMock(spec=ProjectSelectProcessPopupView)
        MockProjectSelectProcessPopupView.return_value = mock_child_view_instance

        # Prepare the Mocked Presenter, including explicit setting of a mocked view member
        mock_child_presenter_instance = MagicMock(spec=ProjectSelectProcessPopupPresenter)
        mock_child_presenter_instance.view = mock_child_view_instance
        MockProjectSelectProcessPopupPresenter.return_value = mock_child_presenter_instance

        # Call the callback function with the additional classes mocked and patched
        presenter.on_select_project()

        # Assert that the patched and mocked Presenter was constructed once
        MockProjectSelectProcessPopupPresenter.assert_called_once()
        # Assert that the patched and mocked View was constructed once
        MockProjectSelectProcessPopupView.assert_called_once()

        # Assert that the mocked view was lifted (made visible and on top)
        mock_child_presenter_instance.display_view.assert_called_with(wait=True)
