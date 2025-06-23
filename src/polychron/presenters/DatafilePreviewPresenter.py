from typing import Any, Dict

from ..interfaces import Mediator
from ..views.DatafilePreviewView import DatafilePreviewView
from .PopupPresenter import PopupPresenter


class DatafilePreviewPresenter(PopupPresenter[DatafilePreviewView, Dict[str, Any]]):
    """Presenter for selecting which models to calibrate, when multiple models are to be calibrated at once.

    Formerly `popupWindow7`, used when opening a csv-like file
    """

    def __init__(self, mediator: Mediator, view: DatafilePreviewView, model: Dict[str, Any]) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind buttons
        self.view.bind_load_button(self.on_load_button)
        self.view.bind_cancel_button(self.on_cancel_button)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        # populate with dataframe contents
        if "df" not in self.model:
            return
        df = self.model["df"]

        # Pass data to the view
        cols = list(df.columns)
        rows = [tuple([index, list(row)]) for index, row in df.iterrows()]
        self.view.set_tree_data(cols, rows)

    def on_load_button(self) -> None:
        """When the load button is pressed, store the dataframe in the model and close the popup"""
        self.model["result"] = "load"
        self.close_view()

    def on_cancel_button(self) -> None:
        """When the cancel button is pressed, discard the dataframe and close the popup"""
        self.model["result"] = "cancel"
        self.close_view()
