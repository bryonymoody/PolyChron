import tkinter as tk
import tkinter.messagebox
from tkinter.filedialog import askopenfile
from typing import Any, Optional

import pandas as pd

from ..interfaces import Navigator
from ..presenters.CalibrateModelSelectPresenter import CalibrateModelSelectPresenter
from ..presenters.DatafilePreviewPresenter import DatafilePreviewPresenter
from ..presenters.MCMCProgressPresenter import MCMCProgressPresenter
from ..presenters.ResidualCheckPopupPresenter import ResidualCheckPopupPresenter
from ..presenters.ResidualOrIntrusivePresenter import ResidualOrIntrusivePresenter
from ..views.CalibrateModelSelectView import CalibrateModelSelectView
from ..views.DatafilePreviewView import DatafilePreviewView
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

        self.view.bind_file_menu_callbacks(
            {
                "Load stratigraphic diagram file (.dot)": lambda: print("@todo"),
                "Load stratigraphic relationship file (.csv)": lambda: self.open_strat_csv_file(),
                "Load scientific dating file (.csv)": lambda: print("@todo"),
                "Load context grouping file (.csv)": lambda: print("@todo"),
                "Load group relationship file (.csv)": lambda: print("@todo"),
                "Load context equalities file (.csv)": lambda: print("@todo"),
                "Load new project": lambda: print("@todo"),
                "Load existing model": lambda: print("@todo"),
                "Save changes as current model": lambda: print("@todo"),
                "Save changes as new model": lambda: print("@todo"),
                "Exit": lambda: print("@todo"),
            }
        )

        self.view.bind_view_menu_callbacks(
            {
                "Display Stratigraphic diagram in phases": lambda: print("@todo"),
            }
        )

        self.view.bind_tool_menu_callbacks(
            {
                "Render chronological graph": lambda: self.chronograph_render_wrap(),
                "Calibrate model": lambda: self.popup_calibrate_model(),
                "Calibrate multiple projects from project": lambda: self.popup_calibrate_multiple(),
                "Calibrate node delete variations (alpha)": lambda: print("@todo"),
                "Calibrate important variations (alpha)": lambda: print("@todo"),
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

    def popup_calibrate_multiple(self) -> None:
        """Callback function for when Tools -> Calibrate multiple projects from project is selected

        Opens a new popup box allowing the user to select which models from a list to calibrate as a batch.
        On close, depending on if any models were selected or not, the models are subsequently calibrated

        @todo - this allows multiple open project windows to be created, which is not ideal
        """
        popup_presenter = CalibrateModelSelectPresenter(self.navigator, CalibrateModelSelectView(self.view), self.model)
        # Ensure it is visible and on top
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()

        # Calibrate the selected models
        # see popupwindow8::cleanup
        pass  # @todo

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

    def file_popup(self, df: Any) -> str:
        """For a gien dataframe, preview the data to the user. Returns the users decision

        @todo - make this return a bool instead of 'load' or 'cancel'
        """
        # @todo set and get model data appropriately
        temp_model = {"df": df, "result": "cancel"}
        popup_presenter = DatafilePreviewPresenter(self.navigator, DatafilePreviewView(self.view), temp_model)
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()  # @todo - not sure these are neccesary

        # Prevent the view's canvas element from being interacted with?
        self.view.canvas["state"] = "disabled"  # @todo
        self.view.parent.wait_window(popup_presenter.view)  # @todo - view.parent mignt not have wiat_window?
        self.view.canvas["state"] = "normal"  # @todo
        print(f"temp_model {temp_model}")
        return temp_model["result"]

    def open_strat_csv_file(self) -> None:
        """Callback function when File > Load stratigraphic relationship file (.csv) is selected, opening a plain text strat file

        Formerly StartPage.open_file2

        @todo - abstract askfileopen somewhere else to limit importing tkinter?

        @todo - finish implementing this with the actual model

        @todo - Column and value validation (within the data model, with exceptions handeled here?)
        """
        file = askopenfile(mode="r", filetypes=[("CSV Files", "*.csv")])

        if file is not None:
            try:
                # @todo finish this.
                # self.littlecanvas.delete('all')
                self.stratfile = pd.read_csv(file, dtype=str)
                load_it = self.file_popup(self.stratfile)
                if load_it == "load":
                    # @todo rest of open_file2
                    tk.messagebox.showinfo("Success", "Stratigraphic data loaded")
                    # self.check_list_gen() # @todo
                else:
                    pass  # @todo this case.
            except ValueError:
                tk.messagebox.showerror("showerror", "Data not loaded, please try again")
