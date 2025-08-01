from ..Config import get_config
from ..interfaces import Mediator
from ..models.Model import Model
from ..views.MCMCProgressView import MCMCProgressView
from .PopupPresenter import PopupPresenter


class MCMCProgressPresenter(PopupPresenter[MCMCProgressView, Model]):
    """Presenter for managing the MCMC progress bar popup view.

    When MCMC calibration has completed, and the popup closes, change to the DatingResults tab
    """

    def __init__(self, mediator: Mediator, view: MCMCProgressView, model: Model) -> None:
        # Call the parent class' constructor
        super().__init__(mediator, view, model)

        # Update view information to reflect the current state of the model
        self.update_view()

    def update_view(self) -> None:
        pass

    def run(self) -> None:
        """Runs model calibration for the current model"""
        # Set progress to none
        self.view.update_progress(0)
        # Use the view as the writable object for progress updates
        progress_io = self.view
        # Run the MCMC calibration
        self.model.mcmc_data.accept_samples_context = [[]]
        while min([len(i) for i in self.model.mcmc_data.accept_samples_context]) < 50000:
            (
                self.model.mcmc_data.contexts,
                self.model.mcmc_data.accept_samples_context,
                self.model.mcmc_data.accept_samples_phi,
                self.model.phi_ref,
                self.model.mcmc_data.A,
                self.model.mcmc_data.P,
                self.model.mcmc_data.all_samples_context,
                self.model.mcmc_data.all_samples_phi,
                self.model.mcmc_data.accept_group_limits,
                self.model.mcmc_data.all_group_limits,
            ) = self.model.MCMC_func(progress_io)

        # Update the model state to show it as having been calibrated
        self.model.mcmc_check = True
        # Save the mcmc data to disk
        self.model.mcmc_data.save(self.model.get_working_directory(), self.model.group_df, get_config().verbose)
