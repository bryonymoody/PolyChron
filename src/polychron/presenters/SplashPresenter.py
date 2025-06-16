from __future__ import annotations

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from ..views.SplashView import SplashView
from .FramePresenter import FramePresenter
from .ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter


class SplashPresenter(FramePresenter[SplashView, ProjectSelection]):
    """Presenter for the Splash Frame, shown in the main view before a project has been loaded.

    This exists soley to allow users who close the initial project selection page to re-open it.
    """

    def __init__(self, mediator: Mediator, view: SplashView, model: ProjectSelection) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        self.child_presenter: ProjectSelectProcessPopupPresenter | None = None

        # Build file/view/tool menus with callbacks
        self.view.build_file_menu(
            [
                None,
                ("Select Project", lambda: self.on_select_project()),
            ]
        )

    def update_view(self) -> None:
        # Does not display anything, i.e model is always None
        pass

    def on_select_project(self) -> None:
        """Function which is called when File > Select Project is selected. I.e. open the popup preesnter for selecting a project."""

        # Instantiate the child presenter and view
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self.mediator, ProjectSelectProcessPopupView(self.view), self.model
        )
        # Ensure it is visible and on top
        popup_presenter.view.lift()
