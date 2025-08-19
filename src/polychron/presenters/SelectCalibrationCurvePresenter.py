from ..interfaces import Mediator
from ..models.InterpolatedRCDCalibrationCurve import InterpolatedRCDCalibrationCurve
from ..views.SelectCalibrationCurveView import SelectCalibrationCurveView
from .PopupPresenter import PopupPresenter


class SelectCalibrationCurvePresenter(PopupPresenter[SelectCalibrationCurveView, object]):
    """Presenter for selecting a calibration curve."""

    def __init__(self, mediator: Mediator, view: SelectCalibrationCurveView, model: object) -> None:
        super().__init__(mediator, view, model)

        # Load calibration curves directly in the presenter
        self.curves = {
            "intcal20": InterpolatedRCDCalibrationCurve("intcal20_interpolated"),
            "marine20": InterpolatedRCDCalibrationCurve("marine20_interpolated"),
            "shcal20": InterpolatedRCDCalibrationCurve("shcal20_interpolated"),
        }
        self.selected_curve_name = None

        # Bind the buttons
        self.view.bind_ok_button(self.on_ok)
        self.view.bind_cancel_button(self.on_cancel)

        # Populate the dropdown
        self.update_view()

    def update_view(self) -> None:
        self.view.set_curve_options(list(self.curves.keys()))

    def on_ok(self) -> None:
        """Apply the selected curve to the main model"""
        selected_curve = self.view.get_selection()
        selected_curve_object = self.curves[selected_curve]

        target_model = getattr(self.model, "current_model", self.model)

        # Store on the model so all presenters can read it later
        if hasattr(target_model, "set_calibration_curve"):
            target_model.set_calibration_curve(selected_curve_object)
            target_model.calibration_curve_name = selected_curve_object.curve_name

        self.close_view()

    def on_cancel(self) -> None:
        self.close_view()
