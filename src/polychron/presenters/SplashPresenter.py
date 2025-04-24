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
        """Function which is called when File > Select Project is selected. I.e. open the popup preesnter for selecting a project."""

        # @todo - what should the navigator here actually be for a popup presenter? Do they need one? Should it just be the parent and not a navigator? some other interface?
        # Instantiate the child presenter and view
        child_presenter = ProjectSelectProcessPopupPresenter(
            self.navigator, ProjectSelectProcessPopupView(self.view), self.model
        )
        # Make the new view visible
        child_presenter.view.deiconify()
        # Ensure it is above the root/parent window
        child_presenter.view.lift()
        # @todo - this allows multiple open project windows to be created, which is not ideal
