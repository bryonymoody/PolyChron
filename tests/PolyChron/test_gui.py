# @note - this will currently cause a window to open and require working tkinter.
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
