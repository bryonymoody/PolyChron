"""Main methnods / cli parsing

@todo find this a more permanent positon once the refactor has progressed enough to remove the original gui.py
"""

import argparse
from importlib.metadata import version

from .Config import Config, get_config


def parse_cli(argv=None) -> argparse.Namespace:
    """Parse and return command line arguments

    Args:
        argv (list[str] or None): optional list of command line parameters to parse. If None, sys.argv is used by `argparse.ArgumentParser.parse_args`

    Returns:
        (argparse.Namespace): Namespace object with arguments set as attributes, as returned by `argparse.ArgumentParser.parse_args()`
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true", help="Show version information and exit")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    # @todo - consider using a 2 element --load instead of -p <p> -m <m>
    parser.add_argument(
        "-p",
        "--project",
        type=str,
        help="Specify a project to create or load, within the polychron projects directory",
    )
    parser.add_argument(
        "-m", "--model", type=str, help="Specify the model to create or load, within -p/--project PROJECT"
    )

    args = parser.parse_args(argv)
    return args


def print_version() -> None:
    """Print the version of PolyChron to stdout

    Note:
        For editable installs the printed value may be incorrect
    """
    print(f"PolyChron {version('polychron')}")


def main() -> None:
    """Main method as the entry point for launching the GUI"""
    args = parse_cli()

    # if the versbose flag was set, ensure it is reflected in the config object
    if args.verbose:
        config = get_config()
        config.verbose = True
        print(f"Config path: {Config._get_config_filepath()}")

    # If version requested on the command line, provide it
    if args.version:
        print_version()
    else:
        # Import and lauch the GUI via an instance of the GUIApp class
        from .GUIApp import GUIApp

        app = GUIApp()
        app.launch(project_name=args.project, model_name=args.model)
