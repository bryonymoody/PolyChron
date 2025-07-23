"""Python module of functions for `mkdocs-macros-plugin` to dynamically extract information for the markdown files in the docs. This cannot be used for html file configuration"""

import pathlib

from packaging.version import Version

from polychron import __version__

# Try and import tomllib (python >= 3.11), otherwise import tomli as tomllib
try:
    import tomllib
except ImportError:
    import tomli as tomllib


def get_python_versions() -> list[str]:
    """Extract and store the supported versions of python from pyproject.toml"""
    versions = []
    with open(pathlib.Path(__file__).parent / "../pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
        if "project" in pyproject:
            project = pyproject["project"]
            if "classifiers" in project:
                for c in project["classifiers"]:
                    if c.startswith("Programming Language :: Python ::"):
                        python_version = c.split(" :: ")[2]
                        if len(python_version) > 1:
                            versions.append(python_version)
            if len(versions) == 0 and "requires-python" in project:
                versions.append(project["requires-python"])
    return versions


def define_env(env):
    """Hook for mkdocs-macros-plugin to update the mkdocs environment"""

    # Store the polychron version, with and without the local version number if present in the env and in config extra
    env.variables["polychron_version"] = __version__
    env.variables["polychron_version_public"] = Version(__version__).public

    # Extract and store the supported versions of python from pyproject.toml
    env.variables["supported_python_versions"] = "\n".join([f"- `{v}`" for v in get_python_versions()])
