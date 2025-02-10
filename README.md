# PolyChron

![PolyChron Logo](./PolyChron/logo.png)

PolyChron is prototype software required to be installed locally on a user’s machine, allowing users to produce multiple chronological models.

In addition, it allows the user to obtain graph theoretic representations
of their stratigraphic sequences and prior knowledge within a given hierarchical Bayesian chronological model and save the raw digital data (as collected on-site) along with graph theoretic representations of their models, resulting outputs and supplementary notes produced during such modelling on their machine, thus facilitating future archiving of a complete site archive.

## Installation from Source

PolyChron is not yet available via `pip` / [PyPI](https://pypi.org/), but can be installed locally from source.

It is recommended to use a python `venv` / virtual environment or similar

```bash
# Create and activate a venv
python3 -m venv .venv
source .venv/bin/activate
```

PolyChron has several non-python dependencies, which must be installed manually:

- [Graphviz](https://www.graphviz.org/)
    - which you can install manually or through your system package manager

        ```bash
        # e.g. for Ubuntu/Debian
        apt-get install graphviz
        ```

- [tkinter](https://docs.python.org/3/library/tkinter.html)
    - Although `tkinter` is part of the Python3 standard library, it is not included in all pre-compiled python distributions. If you encounter errors related to importing `tkinter`, you may need to install it.

        ```bash
        # e.g. for Ubuntu/Debian
        apt-get install python3-tk
        ```

<!-- @todo - non python dependencies? Graphviz? Tikz? -->

PolyChron can then be installed into your python environment using `pip`.
Using an editable installation (`-e` / `--editable`) is preferred for development.

```bash
python3 -m pip install -e .
```

## Usage

With PolyChron installed in the current python environment, it can be launched using any of the following:

```bash
# via the executable script
polychron
# By running the installed PolyChron module
python3 -m PolyChron
# By launching the PolyChron/__main__.py
python3 ./PolyChron/
# Or by launching the GUI module manually
python3 ./PolyChron/gui.py
```

## Documentation

Documentation is built using [mkdocs](https://github.com/mkdocs/mkdocs) and some extensions.

Documentation building dependencies are included in the `docs` optional dependencies group.
They can be installed into the current python environment along with `PolyChron` using `pip`:

```bash
python3 -m pip install -e .[docs]
```

Once installed, documentation can be generated and viewed via a local webserver using:

```bash
python3 -m mkdocs serve
# or just
mkdocs serve
```

Or a static html version can be built into `_site` using:

```bash
python3 -m mkdocs build
# pass --no-directory-urls if you wish to view local .html files without a web server
python3 -m mkdocs build --no-directory-urls
```
