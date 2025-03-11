"""Global variables which need to be accessed in multiple independent files.

Eventually these will be refactored to method parameters / part of other data structures.

Due to how module evaluation works, we cannot `from globals import foo`, as each consumer will have it's own copy of foo.
Instead we must import globals and then access via globals.foo

Use of globals is still not ideal, and will be refactored away, but for now this is the simplest solution.

This is almost certainly going to break saving/loading of due to pickling...

"""

import pathlib

import pandas as pd

phase_true = 0
load_check = "not_loaded"
mcmc_check = "mcmc_notloaded"
proj_dir = ""
FILE_INPUT = None
SCRIPT_DIR = pathlib.Path(__file__).parent  # Path to directory containing this script
CALIBRATION = pd.read_csv(SCRIPT_DIR / "linear_interpolation.txt")
POLYCHRON_PROJECTS_DIR = (pathlib.Path.home() / "Documents/Pythonapp_tests/projects").resolve()
node_df = None
