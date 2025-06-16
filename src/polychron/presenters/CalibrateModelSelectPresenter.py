from ..interfaces import Mediator
from ..models.ProjectSelection import ProjectSelection
from ..views.CalibrateModelSelectView import CalibrateModelSelectView
from .PopupPresenter import PopupPresenter


class CalibrateModelSelectPresenter(PopupPresenter[CalibrateModelSelectView, ProjectSelection]):
    """Presenter for selecting which models to calibrate, when multiple models are to be calibrated at once.

    Formerly `popupWindow8`, used from "tool > Calibrate multiple projects from project"
    """

    def __init__(self, mediator: Mediator, view: CalibrateModelSelectView, model: ProjectSelection) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Bind buttons
        self.view.bind_ok_button(self.on_ok_button)
        self.view.bind_select_all_button(self.on_select_all)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        # For each model in the project which has required input files, add an entry to the list to choose from
        model_list = []
        if self.model is not None:
            project = self.model.current_project
            if project is not None:
                # Build a list of just models which are ready for simualtion.
                # As this will load each model from disk within the project, it may take a while.
                model_list = [name for name, model in project.models.items() if model is not None and model.load_check]

        self.view.update_model_list(model_list)

    def on_ok_button(self) -> None:
        """When the load button is pressed, validate user input, update the model and perform the appropraite action

        Formerly `popupWindow8.cleanup`
        """

        if self.model is not None:
            project = self.model.current_project
            if project is not None:
                selected_models = self.view.get_selected_models()
                # For each selected model, calibrate and save
                for model_name in selected_models:
                    if project.has_model(model_name):
                        model = project.get_model(model_name)
                        if model is not None:
                            (
                                model.mcmc_data.contexts,
                                model.mcmc_data.accept_samples_context,
                                model.mcmc_data.accept_samples_phi,
                                model.phi_ref,
                                model.mcmc_data.A,
                                model.mcmc_data.P,
                                model.mcmc_data.all_samples_context,
                                model.mcmc_data.all_samples_phi,
                                model.mcmc_data.accept_group_limits,
                                model.mcmc_data.all_group_limits,
                            ) = model.MCMC_func()
                            # Update the model state to show it as having been calibrated
                            model.mcmc_check = True
                            # Save the mcmc data to disk
                            model.mcmc_data.save(model.get_working_directory(), model.group_df)
                            model.save()
        # Close the popup
        self.close_view()

    def on_select_all(self) -> None:
        """When the OK button is pressed, select all rows in the list"""
        self.view.select_all_models()
