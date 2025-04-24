import tkinter as tk
import tkinter.messagebox
from typing import Any, Optional

from ..interfaces import Navigator
from ..presenters.MCMCProgressPresenter import MCMCProgressPresenter
from ..presenters.ResidualCheckPopupPresenter import ResidualCheckPopupPresenter
from ..presenters.ResidualOrIntrusivePresenter import ResidualOrIntrusivePresenter
from ..views.MCMCProgressView import MCMCProgressView
from ..views.ModelView import ModelView
from ..views.ResidualCheckPopupView import ResidualCheckPopupView
from ..views.ResidualOrIntrusiveView import ResidualOrIntrusiveView
from .BaseFramePresenter import BaseFramePresenter


class ModelPresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: ModelView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind callback functions for switching between the main view tabs
        view.bind_sasd_tab_button(lambda: self.navigator.switch_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.navigator.switch_presenter("DatingResults"))

        # Bind menu callbacks
        # @todo other menus
        self.view.bind_tool_menu_callbacks(
            {
                "Render chronological graph": lambda: self.chronograph_render_wrap(),
                "Calibrate model": lambda: self.popup_calibrate_model(),
            }
        )

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

    def chronograph_render_wrap(self):
        """wraps chronograph render so we can assign a variable when runing the func using a button"""

        # @todo Implement this method with the yes/no box depedning on if a chrono dag already exists or not.

        # Render the chronograph temporarily
        self.chronograph_render()

    def chronograph_render(self):
        """initiates residual checking function then renders the graph when thats done

        @todo finish this"""

        # @todo check if loaded

        # Check for residuals
        self.resid_check()

        # @todo rest of the method

    def resid_check(self):
        """Loads a text box to check if the user thinks any samples are residual

        @todo - should the import of tk be moved into a view  / wrap tk.messagebox?
        @todo - is this the most appropraite place for this method? (think so)
        """
        MsgBox = tk.messagebox.askquestion(
            "Residual and Intrusive Contexts",
            "Do you suspect any of your samples are residual or intrusive?",
            icon="warning",
        )
        if MsgBox == "yes":
            # Create and show the residual or intrusive presetner
            popup_presenter = ResidualOrIntrusivePresenter(
                self.navigator, ResidualOrIntrusiveView(self.view), self.model
            )
            popup_presenter.view.deiconify()
            popup_presenter.view.lift()  # @todo - not sure these are neccesary
        else:
            # If not, show the residual check presenter, formerly popupWindow3
            popup_presenter = ResidualCheckPopupPresenter(self.navigator, ResidualCheckPopupView(self.view), self.model)
            popup_presenter.view.deiconify()
            popup_presenter.view.lift()  # @todo - not sure these are neccesary
