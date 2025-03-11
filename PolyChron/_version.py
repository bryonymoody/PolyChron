import json
import subprocess
import importlib.metadata
from pathlib import Path

__version__ = "0.1.0"

def is_editable_install():
    """Check if the package has been installed in editable mode or not using importlib."""
    try:
        # Get metadata for the installed package and read direct_url.json to check if an editable install
        distribution = importlib.metadata.distribution("PolyChron")
        direct_url = json.loads(distribution.read_text("direct_url.json"))
        is_editable = direct_url.get("dir_info", {}).get("editable", False)
        return is_editable
    except importlib.metadata.PackageNotFoundError:
        pass
    return False


def get_local_install_git_hash():
    """Get the short git commit hash for the package, if git is installed and the repository is a local install."""
    try:
        # Query package distribution info, to check if editable and find local path
        distribution = importlib.metadata.distribution("PolyChron")
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
            git_hash += "-dirty"

        return git_hash

    except subprocess.CalledProcessError:
        return None


if is_editable_install():
    __version__ = f"{__version__}-dev"
    git_hash = get_local_install_git_hash()
    if git_hash is not None:
        __version__ = f"{__version__}+{git_hash}"
else:
    __version__ = __version__
