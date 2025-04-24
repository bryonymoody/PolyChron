from typing import Any, Optional

from ..interfaces import Navigator
from ..views.ProjectSelectProcessPopupView import ProjectSelectProcessPopupView
from ..views.SplashView import SplashView
from .BaseFramePresenter import BaseFramePresenter
from .ProjectSelectProcessPopupPresenter import ProjectSelectProcessPopupPresenter


class SplashPresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: SplashView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        self.child_presenter: Optional[ProjectSelectProcessPopupPresenter] = None

        self.view.bind_menu_callbacks(lambda: self.on_select_project())

    def update_view(self) -> None:
        # Does not display anything, i.e model is always None
        pass

    def on_select_project(self):
        """Function which is called when File > Select Project is selected. I.e. open the popup preesnter for selecting a project.

        @todo - this allows multiple open project windows to be created, which is not ideal
        """

        # Instantiate the child presenter and view
        popup_presenter = ProjectSelectProcessPopupPresenter(
            self.navigator, ProjectSelectProcessPopupView(self.view), self.model
        )
        # Ensure it is visible and on top
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()
