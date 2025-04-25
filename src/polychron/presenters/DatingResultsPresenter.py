from typing import Any, Optional

from ..interfaces import Navigator
from ..views.DatingResultsView import DatingResultsView
from .BaseFramePresenter import BaseFramePresenter


class DatingResultsPresenter(BaseFramePresenter):
    def __init__(self, navigator: Navigator, view: DatingResultsView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(navigator, view, model)

        # Bind callback functions for switching between the main view tabs
        view.bind_sasd_tab_button(lambda: self.navigator.switch_presenter("Model"))
        view.bind_dr_tab_button(lambda: self.navigator.switch_presenter("DatingResults"))

        # Bind button callbacks
        self.view.bind_posterior_densities_button(lambda: self.on_button_posterior_densities())
        self.view.bind_hpd_button(lambda: self.on_button_hpd_button())
        self.view.bind_clear_list_button(lambda: self.on_button_clear_list_button())

        # Bind menu callbacks
        self.view.bind_file_menu_callbacks(
            {
                "Save project progress": lambda: self.on_file_save(),
            }
        )

        # Bind canvas events
        self.view.bind_littlecanvas_events(
            self.on_canvas_wheel, self.on_canvas_rightclick, self.on_canvas_move_from, self.on_canvas_move_to
        )

        self.view.bind_littlecanvas2_events(
            self.on_canvas_wheel2, self.on_canvas_rightclick2, self.on_canvas_move_from2, self.on_canvas_move_to2
        )

    def update_view(self) -> None:
        pass  # @todo

    def on_file_save(self) -> None:
        """Callback for the File > Save project progress menu command

        Formerly startpage::save_state_1
        """
        pass  # @todo

    def on_button_posterior_densities(self) -> None:
        """Callback for when the "Posterior densities" button is pressed

        Formerly startpage::mcmc_output"""
        pass  # @todo

    def on_button_hpd_button(self) -> None:
        """Callback for when the "HPD intervals" button is pressed

        Formerly startpage::get_hpd_interval"""
        pass  # @todo

    def on_button_clear_list_button(self) -> None:
        """Callback for when the "Clear list" button is pressed

        Formerly clear_results_list"""
        pass  # @todo

    def on_canvas_wheel(self, event: Any) -> None:
        """Callback for mouse wheel events on the littlecanvas canvas"""
        pass  # @todo

    def on_canvas_rightclick(self, event: Any) -> None:
        """Callback for mouse right click events on the littlecanvas canvas"""
        pass  # @todo

    def on_canvas_move_from(self, event: Any) -> None:
        """Callback for mouse move from  events on the littlecanvas canvas"""
        pass  # @todo

    def on_canvas_move_to(self, event: Any) -> None:
        """Callback for mouse move to events on the littlecanvas canvas"""
        pass  # @todo

    def on_canvas_wheel2(self, event: Any) -> None:
        """Callback for mouse wheel events on littlecanvas2 canvas"""
        pass  # @todo

    def on_canvas_rightclick2(self, event: Any) -> None:
        """Callback for mouse right click events on littlecanvas2 canvas"""
        pass  # @todo

    def on_canvas_move_from2(self, event: Any) -> None:
        """Callback for mouse move from  events on littlecanvas2 canvas"""
        pass  # @todo

    def on_canvas_move_to2(self, event: Any) -> None:
        """Callback for mouse move to events on littlecanvas2 canvas"""
        pass  # @todo
