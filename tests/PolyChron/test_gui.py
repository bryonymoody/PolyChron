# @note - this will currently cause a window to open and require working tkinter.
import pytest
import PolyChron.gui
import pathlib


class TestGUI:
    def test_POLYCHRON_PROJECTS_DIR(self):
        """Ensure that the global variable containing the path to the users' projects directory is at the expected location.

        @note - this is mostly an example test for now, and will likely be removed / moved during refactoring.
        """
        # Check that the projects dir global scoped variable is in the correct location
        expected_path = (pathlib.Path.home() / "Documents/Pythonapp_tests/projects").resolve()
        assert PolyChron.gui.POLYCHRON_PROJECTS_DIR == expected_path

    def test_parse_cli_noargs(self):
        """Ensure that parse_cli with no cli arguments sets expected values and does not call sys.exit"""
        try:
            args = PolyChron.gui.parse_cli([])
            # args.version should be false by default
            assert not args.version
        except SystemExit:
            pytest.fail("SystemExit exception raised")

    def test_parse_cli_version(self):
        """Ensure that parse_cli with --version prints something and does not call sys.exit"""
        try:
            args = PolyChron.gui.parse_cli(["--version"])
            # args.version should now be True
            assert args.version
        except SystemExit:
            pytest.fail("SystemExit exception raised")

    def test_parse_cli_version_h(self, capsys):
        """Ensure that parse_cli with -h prints something and then would trigger a sys.exit with a 0 error code (success)"""
        with pytest.raises(SystemExit) as e:
            _ = PolyChron.gui.parse_cli(["-h"])
        assert e.type is SystemExit
        assert e.value.code == 0
        assert len(capsys.readouterr()) != 0

    def test_parse_cli_version_help(self, capsys):
        """Ensure that parse_cli with -h assert len  something and then would trigger a sys.exit with a 0 error code (success)"""
        with pytest.raises(SystemExit) as e:
            _ = PolyChron.gui.parse_cli(["--help"])
        assert e.type is SystemExit
        assert e.value.code == 0
        assert len(capsys.readouterr()) != 0

    def test_print_Version(self, capsys):
        """Ensure that calls to print_version succeed and print something to stdout.

        @note print statement content is not explicitly checked for now.
        """
        PolyChron.gui.print_version()
        assert len(capsys.readouterr()) != 0
