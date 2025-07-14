# PolyChron

![PolyChron Logo](./src/polychron/resources/logo.png)

PolyChron is prototype software required to be installed locally on a user’s machine, allowing users to produce multiple chronological models.

In addition, it allows the user to obtain graph theoretic representations
of their stratigraphic sequences and prior knowledge within a given hierarchical Bayesian chronological model and save the raw digital data (as collected on-site) along with graph theoretic representations of their models, resulting outputs and supplementary notes produced during such modelling on their machine, thus facilitating future archiving of a complete site archive.

## Installation

PolyChron is not yet available from [PyPI](https://pypi.org/) and must be installed from source.

### Requirements

Before installing PolyChron, the following non-python requirements must be installed:

- [Python](https://www.python.org/)
    - `3.9` - `3.13`

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

## Installing PolyChron from Source

It is recommended to use a Python virtual environment (`venv`) or similar for installations of PolyChron, for example:

```bash
# Create and activate a venv
python3 -m venv .venv
source .venv/bin/activate
```

You can then install the latest version of PolyChron into your Python environment using pip:

```bash
python3 -m pip install git+https://github.com/bryonymoody/PolyChron.git
```

Alternatively, you can clone the PolyChron repository and install it locally:

```bash
git clone https://github.com/bryonymoody/PolyChron.git
cd PolyChron
python3 -m pip install .
```

If you are installing PolyChron from source for as a developer, consider using an editable installation (`-e` / `--editable`) and installing the `dev`, `doc` and `test` extras.

```bash
python3 -m pip install -e .[dev,doc,test]
```

## Usage

With PolyChron installed in the current python environment, it can be launched using any of the following:

```bash
# via the executable script
polychron
# By running the installed polychron module
python3 -m polychron
```

## Documentation

Documentation is built using [mkdocs](https://github.com/mkdocs/mkdocs) and some extensions.

Documentation building dependencies are included in the `doc` optional dependencies group.
They can be installed into the current python environment along with `polychron` using `pip`:

```bash
python3 -m pip install -e .[doc]
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

## Tests

Tests are implemented using `pytest`, which can be installed as part of the `test` optional dependencies via:

```bash
python3 -m pip install .[test]
```

Once installed, unit tests can be executed via `pytest` from the root directory

```bash
python3 -m pytest
# or
pytest
```

## Linting

Linting is handled using [`ruff`](https://github.com/astral-sh/ruff) which can be installed as part of the `dev` extras.

> [!NOTE]  
> `automated_mcmc_ordering_coupling.py` is currently excluded from linting

Ruff can then be invoked using:

```bash
python3 -m ruff check
# or
ruff check
```

## Formatting

Automatic code formatting is handled using [`ruff`](https://github.com/astral-sh/ruff) which can be installed as part of the `dev` extras.

> [!NOTE]  
> `automated_mcmc_ordering_coupling.py` is currently excluded from formatting

Ruff can then be invoked using:

```bash
python3 -m ruff fromat
# or
ruff format
```

This can be automatically applied on commit through [pre-commit hooks](https://docs.astral.sh/ruff/integrations/#pre-commit)


## License

PolyChron is released under the [GPLv3 license](LICENSE)
