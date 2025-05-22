from typing import Optional

from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from ..views.SplashView import SplashView
from .BaseFramePresenter import BaseFramePresenter
from .ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter


class SplashPresenter(BaseFramePresenter[ProjectSelection]):
    def __init__(self, mediator: Mediator, view: SplashView, model: ProjectSelection) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        self.child_presenter: Optional[ProjectSelectProcessPopupPresenter] = None

        self.view.bind_menu_callbacks(lambda: self.on_select_project())

    def update_view(self) -> None:
        # Does not display anything, i.e model is always None
        pass

    def on_select_project(self) -> None:
        """Function which is called when File > Select Project is selected. I.e. open the popup preesnter for selecting a project.

        @todo - this allows multiple open project windows to be created, which is not ideal
        """

        # Instantiate the child presenter and view
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self.mediator, ProjectSelectProcessPopupView(self.view), self.model
        )
        # Ensure it is visible and on top
        popup_presenter.view.lift()
