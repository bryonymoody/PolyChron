# PolyChron

![PolyChron Logo](./src/polychron/resources/logo.png)

[![Tests](https://github.com/bryonymoody/PolyChron/actions/workflows/tests.yml/badge.svg)](https://github.com/bryonymoody/PolyChron/actions/workflows/tests.yml)
[![Docs](https://github.com/bryonymoody/PolyChron/actions/workflows/docs.yml/badge.svg)](https://github.com/bryonymoody/PolyChron/actions/workflows/docs.yml)
[![Lint](https://github.com/bryonymoody/PolyChron/actions/workflows/lint.yml/badge.svg)](https://github.com/bryonymoody/PolyChron/actions/workflows/lint.yml)
[![Format](https://github.com/bryonymoody/PolyChron/actions/workflows/format.yml/badge.svg)](https://github.com/bryonymoody/PolyChron/actions/workflows/format.yml)

PolyChron is a GUI application designed to facilitate the analysis and archiving of archaeological dating evidence. 
It supports the management of both relative and absolute dating evidence, enabling users to build multiple chronological models within a Bayesian modelling framework.

Key features include:

- Graph-theoretic representations of stratigraphic sequences, which users can explore and edit via an intuitive point-and-click interface.

- The ability to input prior knowledge, such as:

    - Groupings of archaeological contexts

    - Identification of residual or intrusive samples

    - Relationships between different groups

Using this information, PolyChron constructs a hierarchical Bayesian model and uses an MCMC (Markov Chain Monte Carlo) algorithm to estimate the posterior calendar ages of samples.

All outputs, including raw digital data (as input by the user), model representations, results, and supplementary notes are saved locally.
This ensures the full site archive is preserved for future use and long-term archiving with the Archaeology Data Service.

## Documentation

For full documentation including a userguide and developer reference, please see [bryonymoody.github.io/PolyChron](https://bryonymoody.github.io/PolyChron)

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

If you are installing PolyChron from source as a developer, consider using an editable installation (`-e` / `--editable`) and installing the `dev`, `doc` and `test` extras.

```bash
python3 -m pip install -e .[dev,doc,test]
```

## Usage

With PolyChron installed in the current python environment, it can be launched using any of the following:

```bash
# via the executable script
polychron
# or by running the installed polychron module
python3 -m polychron
```

## Building Documentation

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

## Testing

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

## Contributing

If you would like to contribute towards PolyChron, please see the [contributing guidelines](./CONTRIBUTING.md).

## License

PolyChron is released under the [GPLv3 license](LICENSE)
