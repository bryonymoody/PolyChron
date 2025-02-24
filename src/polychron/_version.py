from __future__ import annotations

import importlib.metadata
import json
import subprocess
from pathlib import Path

# Define the public version string
__version__ = "0.2.0"


def is_editable_install() -> bool:
    """Check if the package has been installed in editable mode or not using importlib.

    Returns:
        Boolean indicating if polychron was installed in editable mode
    """
    try:
        # Get metadata for the installed package and read direct_url.json to check if an editable install
        distribution = importlib.metadata.distribution("polychron")
        direct_url = json.loads(distribution.read_text("direct_url.json"))
        is_editable = direct_url.get("dir_info", {}).get("editable", False)
        return is_editable
    except importlib.metadata.PackageNotFoundError:
        return False


def get_local_install_git_hash() -> str | None:
    """Get the short git commit hash for the package, if git is installed and the repository is a local install.

    Returns:
        The short git commit hash if available, otherwise None
    """
    try:
        # Query package distribution info, to check if editable and find local path
        distribution = importlib.metadata.distribution("polychron")
        direct_url = json.loads(distribution.read_text("direct_url.json"))
        local_path = direct_url.get("url", None)
        # Return early if not a local filepath, or it does not exist.
        if not local_path.startswith("file://"):
            return None
        package_path = Path(local_path[7:])
        if not package_path.is_dir():
            return None
        # Get the short commit hash
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=package_path,
        )
        git_hash = result.stdout.strip()
        # Check if the working directory is dirty
        result = subprocess.run(
            ["git", "diff", "--shortstat"],
            capture_output=True,
            text=True,
            check=True,
            cwd=package_path,
        )
        is_dirty = bool(result.stdout.strip())
        # If the git repo is dirty (i.e. uncommitted changes) postfix the short hash local version identifier with -dirty
        if is_dirty:
            git_hash += ".dirty"

        return git_hash

    except subprocess.CalledProcessError:
        return None


# If the install is an editable install, include a local version number
if is_editable_install():
    __version__ = f"{__version__}+editable"
    if (git_hash := get_local_install_git_hash()) is not None:
        __version__ = f"{__version__}.{git_hash}"
