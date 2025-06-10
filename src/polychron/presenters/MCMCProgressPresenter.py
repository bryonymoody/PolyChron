import re
import sys
import tkinter as tk
from tkinter import ttk

from ..interfaces import Mediator
from ..models.Model import Model
from ..views.MCMCProgressView import MCMCProgressView
from .PopupPresenter import PopupPresenter


# @todo - refactor this, should be doable without a stdrediector
class StdoutRedirector(object):
    def __init__(self, text_area: tk.Label, pb1: ttk.Progressbar) -> None:
        """allows us to rimedirect
        output to the app canvases"""
        self.text_area = text_area
        self.pb1 = pb1

    def write(self, text: str) -> None:
        """writes to canvas"""
        self.pb1.update_idletasks
        str1 = re.findall(r"\d+", text)
        if len(str1) != 0:
            self.text_area["text"] = f"{str1[0]}% complete"
            self.pb1["value"] = f"{str1[0]}"
            self.text_area.update_idletasks()

    def flush(self) -> None:
        pass


class MCMCProgressPresenter(PopupPresenter[Model]):
    """Presenter for managing the MCMC progress bar popup view.

    When MCMC calibration has completed, and the popup closes, change to the DatingResults tab

    @todo - when calibrated, this may do multiple passes, but the progress bad is only for the current pass
    """

    def __init__(self, mediator: Mediator, view: MCMCProgressView, model: Model) -> None:
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Prevent the window from being closed with a noop lambda
        # @todo - do something cleaner about cancelling an in-progress calibration
        # self.view.bind("<Control-w>", lambda *Args: None)
        # self.view.protocol("WM_DELETE_WINDOW", lambda: None)

        # Update view information to reflect the current state of the model
        self.update_view()

    def run(self) -> None:
        """Runs model calibration for the current model

        @todo - move the actual calibration into the model
        @todo - finish the actual implemetnation
        """
        # @todo - do nothing if the model is not ready for calibration
        # Set progress to none
        self.view.update_progress(0)
        # Setup stdout redirection
        # @todo - instead of redirecting stdout, pass a file descriptor to the mcmc function for progress writing, or just store a value in this presenters model?
        old_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self.view.output_label, self.view.progress_bar)
        # Run the MCMC calibration
        self.model.mcmc_data.accept_samples_context = [[]]  # @Todo - reset the full mcmc data instance?
        while min([len(i) for i in self.model.mcmc_data.accept_samples_context]) < 50000:
            # @todo - as all of these get stored in the model, why not just make mcmc_func mutate itself?
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
            ) = self.model.MCMC_func()

        # Restore the original stdout
        sys.stdout = old_stdout

        # Update the model state to show it as having been calibrated
        self.model.mcmc_check = True
        # Save the mcmc data to disk (@todo fold this into a method which sets mcmc_check?
        self.model.mcmc_data.save(self.model.get_working_directory(), self.model.group_df)

    def update_view(self) -> None:
        pass
