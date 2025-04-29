from typing import Any, Literal, Optional

from ..interfaces import Mediator
from ..presenters.ManageIntrusiveOrResidualContextsPresenter import ManageIntrusiveOrResidualContextsPresenter
from ..views.ManageIntrusiveOrResidualContextsView import ManageIntrusiveOrResidualContextsView
from ..views.ResidualOrIntrusiveView import ResidualOrIntrusiveView
from .BasePopupPresenter import BasePopupPresenter


# @todo - this needs to be closable by child popups, may need Mediator changes (or just in mediater.close call the parents mediator close based on the reason?)
class ResidualOrIntrusivePresenter(BasePopupPresenter, Mediator):
    """Presenter for managing the MCMC progress bar popup view.

    When MCMC calibration has completed, and the popup closes, the mediator should change to the DatingResults tab
    """

    def __init__(self, mediator: Mediator, view: ResidualOrIntrusiveView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        self.mode: Optional[Literal["resid", "intru"]] = None  # @todo propper enum

        # Bind enabling residual mode
        self.view.bind_residual_mode_button(lambda: self.on_resid_button())

        # Bind enabling intrusive
        self.view.bind_intrusive_mode_button(lambda: self.on_intru_button())

        # Bind the proceed button, which should open another popup for the next stage
        self.view.bind_proceed_button(self.on_proceed)

        # @todo bind graph interaction
        # self.view.bind_graphcanvas_events()

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        # Update button colours depending ont the mode.
        if self.mode == "resid":
            self.view.set_residual_mode_button_background("orange")
            self.view.set_intrusive_mode_button_background("light gray")
        elif self.mode == "intru":
            self.view.set_residual_mode_button_background("light gray")
            self.view.set_intrusive_mode_button_background("lightgreen")
        else:
            self.view.set_residual_mode_button_background("light gray")
            self.view.set_intrusive_mode_button_background("light gray")

        # Update lists @todo
        # self.view.set_resid_label_text
        # self.view.set_intru_label_text

    def set_mode(self, mode: Literal["resid", "intru"]) -> None:
        self.mode = mode
        self.update_view()

    def on_resid_button(self) -> None:
        """Enable resid mode for user interaction"""
        self.set_mode("resid")
        self.update_view()

    def on_intru_button(self) -> None:
        """Enable intrusive mode for user interaction"""
        self.set_mode("intru")
        self.update_view()

    def on_proceed(self) -> None:
        """When the proceed button is pressed, open the next popup window for managing intrusive or residual contexts (formerly popup4_wrapper)"""

        popup_presenter = ManageIntrusiveOrResidualContextsPresenter(
            self.mediator, ManageIntrusiveOrResidualContextsView(self.view), self.model
        )
        popup_presenter.view.deiconify()
        popup_presenter.view.lift()  # @todo - not sure these are neccesary
