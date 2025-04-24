from typing import Any, Optional

from ..interfaces import Navigator
from ..presenters.MCMCProgressPresenter import MCMCProgressPresenter
from ..views.MCMCProgressView import MCMCProgressView
from ..views.ModelView import ModelView
from .BaseFramePresenter import BaseFramePresenter


class ModelPresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: ModelView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind callback functions for switching between the main view tabs
        view.bind_sasd_tab_button(lambda: self.navigator.switch_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.navigator.switch_presenter("DatingResults"))

        # Bind menu callbacks
        # @todo
        self.view.bind_tool_menu_callbacks({"Calibrate model": lambda: self.popup_calibrate_model()})

        # Bind button clicks
        # @todo

        # Bind mouse & keyboard events
        # @todo

        # Update data

    def update_view(self) -> None:
        pass  # @todo

    def popup_calibrate_model(self) -> None:
        """Callback function for when Tools -> Calibrate model is selected

        @todo - this allows multiple open project windows to be created, which is not ideal
        """
        # Create the popup presenter and view
        popup_presenter = MCMCProgressPresenter(self.navigator, MCMCProgressView(self.view), self.model)
        # Ensure it is visible and on top
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()
        # Run the calibration
        # @todo - gracefully handle errors during calibration
        popup_presenter.run()
        # Ensure model data is correct / updated in memory
        # @todo
        # Close the popup
        popup_presenter.close_view()
        # Change to the DatingResults tab (assuming the calibration ran successfully @todo)
        self.navigator.switch_presenter("DatingResults")

        # @todo - esnure the presenter is destroyed
