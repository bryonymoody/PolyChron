from typing import Any, Optional

from ..interfaces import Mediator
from ..views.CalibrateModelSelectView import CalibrateModelSelectView
from .BasePopupPresenter import BasePopupPresenter


class CalibrateModelSelectPresenter(BasePopupPresenter):
    """Presenter for selecting which models to calibrate, when multiple models are to be calibrated at once.

    Formerly `popupWindow8`, used from "tool > Calibrate multiple projects from project"

    @todo - is the triggering label accurate? I.e. is it models not projects?
    """

    def __init__(self, mediator: Mediator, view: CalibrateModelSelectView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind buttons
        self.view.bind_ok_button(self.on_ok_button)
        self.view.bind_select_all_button(self.on_select_all)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        # self.view.list_box.insert("end", "foo")
        # self.view.list_box.insert("end", "bar")
        pass  # @todo

    def on_ok_button(self) -> None:
        """When the load button is pressed, validate user input, update the model and perform the appropraite action"""
        # @todo - validate input and if ok update the model / trigger follow on actions.
        self.close_view()
        # @todo - this is prolly a memory leak.

    def on_select_all(self) -> None:
        """When the OK button is pressed, select all rows in the list"""
        # @todo - validate input and if ok update the model / trigger follow on actions.
        self.view.list_box.select_set(
            0, "end"
        )  # @todo - should this be abstracted into the passive view to remove tkinter use here?
