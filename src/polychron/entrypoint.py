"""Main methnods / cli parsing

@todo find this a more permanent positon once the refactor has progressed enough to remove the original gui.py
"""

import argparse
from importlib.metadata import version


def parse_cli(argv=None):
    """Parse and return command line arguments

    Args:
        argv (list[str] or None): optional list of command line parameters to parse. If None, sys.argv is used by `argparse.ArgumentParser.parse_args`

    Returns:
        (argparse.Namespace): Namespace object with arguments set as attributes, as returned by `argparse.ArgumentParser.parse_args()`
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true", help="show version information and exit")
    parser.add_argument("--view", type=str, help="Temporary: select which view to demo during development") #  @todo remove this
    parser.add_argument("--viewidx", type=int, help="Temporary: select which view to demo during development by index") #  @todo remove this

    args = parser.parse_args(argv)
    return args


def print_version():
    """Print the version of PolyChron to stdout

    Note:
        For editable installs the printed value may be incorrect
    """
    print(f"PolyChron {version('polychron')}")


def main():
    """Main method as the entry point for launching the GUI"""
    args = parse_cli()
    # If version requested on the command line, provide it
    if args.version:
        print_version()
    else:
        # Import and lauch the GUI via an instance of the GUIApp class
        from .GUIApp import GUIApp

        app = GUIApp()
        # app.launch()
        app.launch(args.view, args.viewidx) # @todo remove args.view
