import sys
import tkinter as tk
import tkinter.ttk as ttk
from unittest.mock import MagicMock, patch

import pytest

from polychron.interfaces import Mediator
from polychron.models.Model import Model
from polychron.presenters.MCMCProgressPresenter import MCMCProgressPresenter, StdoutRedirector
from polychron.views.MCMCProgressView import MCMCProgressView


class TestStdoutRedirector:
    """Tests for the StdoutRedirector class"""

    def test_init(self):
        """Test construction behaves as expected, using mocked versions of tk.Label and ttk.ProgressBar. This will be deleted eventually"""
        mock_label = MagicMock(spec=tk.Label)
        mock_progress_bar = MagicMock(spec=ttk.Progressbar)
        redirector = StdoutRedirector(mock_label, mock_progress_bar)
        assert redirector.text_area == mock_label
        assert redirector.pb1 == mock_progress_bar

    def test_write(self):
        """Test write calls the appropriate members"""
        mock_label = MagicMock(spec=tk.Label)
        mock_progress_bar = MagicMock(spec=ttk.Progressbar)
        redirector = StdoutRedirector(mock_label, mock_progress_bar)

        # Test a non-numeric value
        test_str = "foo"
        redirector.write(test_str)
        mock_progress_bar.update_idletasks.assert_called()
        # Assert that no "text" or "value" were set.
        mock_label.__setitem__.assert_not_called()
        mock_progress_bar.__setitem__.assert_not_called()

        # Test a numeric value
        test_str = "12"
        redirector.write(test_str)
        mock_progress_bar.update_idletasks.assert_called()
        # Assert that no "text" or "value" were set.
        mock_label.__setitem__.assert_called_with("text", f"{test_str}% complete")
        mock_progress_bar.__setitem__.assert_called_with("value", f"{test_str}")
        mock_label.update_idletasks.assert_called()

    def test_flush(self):
        """Test flush is implemented"""
        mock_label = MagicMock(spec=tk.Label)
        mock_progress_bar = MagicMock(spec=ttk.Progressbar)
        redirector = StdoutRedirector(mock_label, mock_progress_bar)
        # This should not throw
        redirector.flush()

    def test_capture(self, capsys: pytest.CaptureFixture):
        """Test that it can be used to redirect stdout"""
        mock_label = MagicMock(spec=tk.Label)
        mock_progress_bar = MagicMock(spec=ttk.Progressbar)

        # Check that printing is output to stdout currently
        capsys.readouterr()
        print("test")
        assert capsys.readouterr().out == "test\n"

        # Re-assign sys.stdout
        old_stdout = sys.stdout
        sys.stdout = StdoutRedirector(mock_label, mock_progress_bar)
        # Print, ensuring it was not output to stdout
        capsys.readouterr()
        print("12")
        assert len(capsys.readouterr().out) == 0
        # And check that the progress bar was updated
        mock_progress_bar.__setitem__.assert_called_with("value", "12")

        # And check it can be resumed
        sys.stdout = old_stdout
        capsys.readouterr()
        print("test")
        assert capsys.readouterr().out == "test\n"


class TestMCMCProgressPresenter:
    """Unit tests for the MCMCProgressPresenter class.

    The Mediator and View are Mocked to avoid creation of tkinter UI components during test execution.
    """

    def test_init(self, test_data_model_demo: Model):
        """Tests the __init__ method of the MCMCProgressPresenter class.

        Checks that the presenter has the expected values after initialisation, and that any view methods were called as expected

        Todo:
            - Test with more than one Model instance, to cover additional branches / edge cases.
                - Not all datafiles opened/loaded
                - Test with model.residual_contexts set
                - Test with model.intrusive_contexts set
                - Test with removed edges/nodes
        """
        # Create mocked objects
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=MCMCProgressView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = MCMCProgressPresenter(mock_mediator, mock_view, model)

        # Assert that presenter attributes are set as intended
        assert presenter.mediator == mock_mediator
        assert presenter.view == mock_view
        assert presenter.model == model

        # update_view should have been called, but that is currently a noop

    def test_update_view(self, test_data_model_demo: Model):
        """Test update_view behaves as intended with the Demo model"""
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=MCMCProgressView)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = MCMCProgressPresenter(mock_mediator, mock_view, model)

        # Assert update_view can be called without raising any exceptions, it currently does nothing.
        presenter.update_view()

    def test_run(self, test_data_model_demo: Model, capsys: pytest.CaptureFixture):
        """Test run behaves as intended with the Demo model

        Todo:
            - This test should actually test a real model, rather than mocking the MCMC_func ou ideally.
        """
        # Create mocked objects with autospec=True
        mock_mediator = MagicMock(spec=Mediator)
        mock_view = MagicMock(spec=MCMCProgressView)
        # Ensure that the view has the output_label and progress_bar which are directly accessed by StdoutRedirector
        mock_view.output_label = MagicMock(spec=tk.Label)
        mock_view.progress_bar = MagicMock(spec=ttk.Progressbar)

        # Gets a Model instance via a fixture in conftest.py
        model = test_data_model_demo

        # Instantiate the Presenter
        presenter = MCMCProgressPresenter(mock_mediator, mock_view, model)

        # Todo: This should only actually execute if the model meets the load_check requirements

        # Ensure no previous output is in the capture region
        capsys.readouterr()

        # Patch out Model.MCMC_func & MCMCData.save methods to avoid expensive ops
        with (
            patch("polychron.models.Model.Model.MCMC_func") as mock_model_mcmc_func,
            patch("polychron.models.MCMCData.MCMCData.save") as mock_mcmcdata_save,
        ):
            # Define a fake mcmc func which prints several times before returning some fake data of the correct type and assign it as the MagicMock side_effect
            def fake_mcmc_func():
                print(12)
                print(50)
                print(100)
                return tuple([[], [[i for i in range(50000)]], [], [], 12, 12, [], [], {}, {}])

            mock_model_mcmc_func.side_effect = fake_mcmc_func

            # Call the run method
            presenter.run()

            # Assert that view.update_progress was called, this will eventually be used in-place of direct manipulation within the stdout redirector
            mock_view.update_progress.assert_called_with(0)

            # Assert that the MCMC_Func was called at least once
            mock_model_mcmc_func.assert_called()
            # Assert that mcmc_check was set
            assert presenter.model.mcmc_check
            # Assert that MCMCData.save was called
            mock_mcmcdata_save.assert_called_once()
            # Assert that nothing was output to regular stdout, it should have been captured
            captured = capsys.readouterr()
            assert len(captured.out) == 0
            assert len(captured.err) == 0
