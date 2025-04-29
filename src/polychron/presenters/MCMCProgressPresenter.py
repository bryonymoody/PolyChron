import re
import sys
import time
from typing import Any, Optional

from ..interfaces import Mediator
from ..views.MCMCProgressView import MCMCProgressView
from .BasePopupPresenter import BasePopupPresenter


# @todo - refactor this, should be doable without a stdrediector
class StdoutRedirector(object):
    def __init__(self, text_area, pb1):
        """allows us to rimedirect
        output to the app canvases"""
        self.text_area = text_area
        self.pb1 = pb1

    def write(self, str):
        """writes to canvas"""
        self.pb1.update_idletasks
        str1 = re.findall(r"\d+", str)
        if len(str1) != 0:
            self.text_area["text"] = f"{str1[0]}% complete"
            self.pb1["value"] = f"{str1[0]}"
            self.text_area.update_idletasks()

    def flush(self):
        pass


def mock_mcmc():
    """Method which mocks the running of the mcmc simulation prior to full model implementation.

    @todo This will be removed once the data model is fully setup and real calibration can be used instead.
    """
    for i in range(0, 100, 12):
        print(i)
        time.sleep(0.5)
    print(100)
    time.sleep(1)


class MCMCProgressPresenter(BasePopupPresenter):
    """Presenter for managing the MCMC progress bar popup view.

    When MCMC calibration has completed, and the popup closes, change to the DatingResults tab
    """

    def __init__(self, mediator: Mediator, view: MCMCProgressView, model: Optional[Any] = None):
        # Call the parent class' consturctor
        super().__init__(mediator, view, model)

        # Prevent the window from being closed with a noop lambda
        # @todo - do something cleaner about cancelling an in-progress calibration
        self.view.bind("<Control-w>", lambda *Args: None)
        self.view.protocol("WM_DELETE_WINDOW", lambda: None)

        # Update view information to reflect the current state of the model
        self.update_view()

    def run(self):
        self.view.update_progress(0)
        # @todo - instead of redirecting stdout, pass a file descriptor to the mcmc function for progress writing, or just store a value in this presenters model?
        # Save the old stdout
        old_stdout = sys.stdout
        # Redirect stdout
        sys.stdout = StdoutRedirector(self.view.output_label, self.view.progress_bar)

        # Run the MCMC calibration
        # @todo replace with the actual method
        mock_mcmc()
        # Restore the old stdout
        sys.stdout = old_stdout

        # Mark the model as having been calibrated
        # @todo

    def update_view(self) -> None:
        pass
        # self.view.update_progress(10)
