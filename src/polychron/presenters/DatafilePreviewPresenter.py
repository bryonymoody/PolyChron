from typing import Any, Dict

from ..interfaces import Mediator
from ..views.DatafilePreviewView import DatafilePreviewView
from .PopupPresenter import PopupPresenter


class DatafilePreviewPresenter(PopupPresenter[Dict[str, Any]]):
    """Presenter for selecting which models to calibrate, when multiple models are to be calibrated at once.

    Formerly `popupWindow7`, used when opening a csv-like file

    Todo:
        @todo - Better model typehint / don't just use a Dict
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
        # @todo - make this work with an actual "model" class.
        if "df" not in self.model:
            return
        df = self.model["df"]
        # abstract view detials into a method in the view class?
        cols = list(df.columns)
        self.view.tree["columns"] = cols
        for i in cols:
            self.view.tree.column(i, anchor="w")
            self.view.tree.heading(i, text=i, anchor="w")
        # @todo - this previews the datafile in reverse order?
        for index, row in df.iterrows():
            self.view.tree.insert("", 00, text=index, values=list(row))

    def on_load_button(self) -> None:
        """When the load button is pressed, store the dataframe in the model and close the popup"""
        # @todo - validate input and if ok update the model / trigger follow on actions.
        self.model["result"] = "load"  # @todo propper
        self.close_view()
        # @todo - this is prolly a memory leak.

    def on_cancel_button(self) -> None:
        """When the cancel button is pressed, discard the dataframe and close the popup"""
        # @todo - validate input and if ok update the model / trigger follow on actions.
        self.model["result"] = "cancel"  # @todo propper
        self.close_view()
        # @todo - this is prolly a memory leak.
