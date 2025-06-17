from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pytest

from polychron.Config import Config
from polychron.entrypoint import main, parse_cli, print_version


class TestEntrypoint:
    """Unit tests for the entrypoint.py module"""

    def test_parse_cli_no_args(self) -> None:
        """Test the CLI argument parsing with no arguments provided"""
        args = parse_cli(argv=[])  # Must provide an argv to avoid using the real argv
        assert not args.version
        assert not args.verbose
        assert args.project is None
        assert args.model is None

    def test_parse_cli_version(self) -> None:
        """Test the CLI argument parsing with the version flag provided"""
        args = parse_cli(["--version"])
        assert args.version
        assert not args.verbose
        assert args.project is None
        assert args.model is None

    def test_parse_cli_verbose(self) -> None:
        """Test the CLI argument parsing with the verbose flag provided"""
        args = parse_cli(["--verbose"])
        assert not args.version
        assert args.verbose
        assert args.project is None
        assert args.model is None

    def test_parse_cli_project(self) -> None:
        """Test the CLI argument parsing with the project argument provided"""
        # long
        args = parse_cli(["--project", "foo"])
        assert not args.version
        assert not args.verbose
        assert args.project == "foo"
        assert args.model is None
        # short
        args = parse_cli(["-p", "foo"])
        assert not args.version
        assert not args.verbose
        assert args.project == "foo"
        assert args.model is None

    def test_parse_cli_model(self) -> None:
        """Test the CLI argument parsing with the model argument but no project. This should trigger an exit"""
        # long
        with pytest.raises(SystemExit):
            parse_cli(["--model", "bar"])
        # short
        with pytest.raises(SystemExit):
            parse_cli(["-m", "bar"])

    def test_parse_cli_project_model(self) -> None:
        """Test the CLI argument parsing with the project and argument flags provided"""
        # long
        args = parse_cli(["--project", "foo", "--model", "bar"])
        assert not args.version
        assert not args.verbose
        assert args.project == "foo"
        assert args.model == "bar"
        # short
        args = parse_cli(["--p", "foo", "--m", "bar"])
        assert not args.version
        assert not args.verbose
        assert args.project == "foo"
        assert args.model == "bar"

    def test_parse_cli_project_invalid(self) -> None:
        """Test the CLI argument parsing with invalid CLI arguments provided

        This would raise a SystemExit exception, which we can intercept / expect"""
        with pytest.raises(SystemExit):
            _ = parse_cli(argv=["--made", "--up", "--flags"])

    def test_print_version(self, capsys: pytest.CaptureFixture) -> None:
        """Test the print_version method, capturing stdout via capsys

        Note:
            The returned version is the most recently installed version, so we just test that a version is returned not the correct version.

            This will need changing if/when https://github.com/bryonymoody/PolyChron/pull/60 is merged"""

        # Call the method, printing to stdout
        print_version()
        # Get the captured stdout/err
        captured = capsys.readouterr()
        # Assert there is no stderr
        assert len(captured.err) == 0
        # Assert there is some stdout
        assert len(captured.out) > 0
        # Assert that the stdout string matches a regular expression
        pattern = r"^PolyChron ([0-9]+.[0-9]+.[0-9]+.*)$"  # flexible semver detection
        assert re.match(pattern, captured.out) is not None

    @patch("polychron.GUIApp.GUIApp")
    @patch(
        "sys.argv",
        [
            __file__,
        ],
    )  # mock the cli args argparse will see
    def test_main_no_args(self, MockGUIApp, capsys: pytest.CaptureFixture) -> None:
        """Test the main() method with no CLI args provided.

        Uses mocking to prevent actual launch of the GUI / manipulation of the global Config object"""

        # Use MagicMock combined with @patch above to prevent a real GUIApp from being created and launched, but allow detection of the attempted launch
        mock_GUIApp_instance = MockGUIApp()
        mock_GUIApp_instance.launch = MagicMock()

        # Call the main method
        main()

        # Assert that the GUIApp would have been launched, via the mocked object
        mock_GUIApp_instance.launch.assert_called_once()

        # Assert that nothing was printed (as verbose is false)
        captured = capsys.readouterr()
        assert len(captured.out) == 0
        assert len(captured.err) == 0

    @patch("polychron.entrypoint.get_config", return_value=Config())
    @patch("polychron.GUIApp.GUIApp")
    @patch("sys.argv", [__file__, "--verbose"])  # mock the cli args argparse will see
    def test_main_verbose(self, MockGUIApp, mock_get_config, capsys: pytest.CaptureFixture) -> None:
        """Test the main() method with --verbose provided

        This should mutate the global config (mocked) and print some information to stdout.

        Uses mocking to prevent actual launch of the GUI / manipulation of the global Config object"""

        # Use MagicMock combined with @patch above to prevent a real GUIApp from being created and launched, but allow detection of the attempted launch
        mock_GUIApp_instance = MockGUIApp()
        mock_GUIApp_instance.launch = MagicMock()

        # Call the main method
        main()

        # Assert that the GUIApp would have been launched, via the mocked object
        mock_GUIApp_instance.launch.assert_called_once()
        # Assert that the config was accessed
        mock_get_config.assert_called()

        # Assert that something was printed to stdout, and nothing to stderr
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert len(captured.err) == 0

    @patch("polychron.GUIApp.GUIApp")
    @patch("sys.argv", [__file__, "--version"])  # mock the cli args argparse will see
    def test_main_version(self, MockGUIApp, capsys: pytest.CaptureFixture) -> None:
        """Test the main() method with --version passed, which shoul dprint to stdout and not call GUIApp.launch

        Uses mocking to prevent actual launch of the GUI / manipulation of the global Config object"""

        # Use MagicMock combined with @patch above to prevent a real GUIApp from being created and launched, but allow detection of the attempted launch
        mock_GUIApp_instance = MockGUIApp()
        mock_GUIApp_instance.launch = MagicMock()

        # Call the main method
        main()

        # Assert that the GUIApp was not launched
        mock_GUIApp_instance.launch.assert_not_called()

        # Assert that something was printed to stdout, and nothign to stderr
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert len(captured.err) == 0
