#!/usr/bin/env python3

"""Generate dynamic pages, including API reference for the polychron package and navigation structure"""

import os
from pathlib import Path
from typing import Iterator

import mkdocs_gen_files


def iterate_py_files(path: Path) -> Iterator[Path]:
    """Recursive case-insensitive-sorted depth-first iteration of .py files within a directory"""

    if not path.is_dir():
        return

    # Iterate subdirs, sorted by lowercase name
    for entry in sorted(path.iterdir(), key=lambda p: str(p).lower()):
        if os.path.isdir(entry):
            yield from iterate_py_files(entry)

    # Then iterate files, sorted by lowercase name
    for entry in sorted(path.iterdir(), key=lambda p: str(p).lower()):
        if os.path.isfile(entry) and entry.name.endswith(".py"):
            yield entry


# Relative locaiton of the src dir
src_dir = Path(__file__).parent.parent / "src"

# Get the mkdocs navigation structure object
nav = mkdocs_gen_files.Nav()

# Add the index.md to the literate nav
nav["reference"] = "index.md"

# Iterate through all Python files in the source directory
for path in iterate_py_files(src_dir):
    # Skip files like __init__.py
    if path.name.startswith("__"):
        continue

    # Calculate the module path/name (e.g. package.module.submodule)
    module_path = path.relative_to(src_dir).with_suffix("")
    module_name = ".".join(module_path.parts)

    # Build the path to the markdown file for the modules
    doc_path = Path(module_path).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    # Add to the navigation object
    nav[module_path.parts] = doc_path

    # Create the markdown file stub.
    with mkdocs_gen_files.open(full_doc_path, "w") as f:
        print(f"# `{module_name}` Module\n", file=f)
        print(f"::: {module_name}\n", file=f)
        print("\n", file=f)


# Write the dynamic navigation to SUMMARY.md
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as f:
    f.writelines(nav.build_literate_nav())
