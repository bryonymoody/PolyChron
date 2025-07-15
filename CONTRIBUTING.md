# Contributing to PolyChron

## Reporting Bugs and Requesting Features

Please use [GitHub Issues](https://github.com/bryonmoody/PolyChron/issues) for any bug reports, feature requests or questions about PolyChron.

Before opening an issue, please search the [existing issues](https://github.com/bryonmoody/PolyChron/issues) to see if the bug or feature request has already been reported, or fixed in the `main` branch or a more recent release.

If you are reporting a bug, please provide as much detail as possible to help identify and resolve the issue.

## Submitting changes

If you wish to contribute to PolyChron, please create a [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) of the [PolyChron repository](https://github.com/bryonmoody/PolyChron/), push your changes to a non-default branch (i.e. not `main`) and open a [Pull Request](https://github.com/bryonymoody/PolyChron/pulls).

By contributing your code to PolyChron, you agree to license your contribution under the [GPLv3 license](./LICENSE).

Your changes should adhere to the coding conventions detailed below, should be covered by the test suite (where appropriate), and CI checks should all succeed.

### Coding conventions

- PolyChron roughly follows a Model-View-Presenter architecture
    - `models` own and manage data
    - Passive `views` represent the GUI elements (i.e. almost all `tkinter` code)
    - `presenters` connect the `models` and `views` together, transforming data for presentation, and handling events from the GUI.
- `ruff check` is used for linting, with rules configured in `pyproject.toml`. See [README.md](./README.md) for more information
- `ruff format` is used for code formatting, with rules configured in `pyproject.toml`. See [README.md](./README.md) for more information
- Documentation is generated using `mkdocs` and `mkdocstrings-python`, with [`Google-style` docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
- Automated testing is implemented as a `pytest` test suite, mirroring the structure of the package in `tests/polychron`.
    - Input files used for testing IO should be stored in `tests/data`
    - `views` are not fully tested currently, due to complexities of having meaningful unit tests for `tkinter` GUIs. `unittest.mock` is heavily relied upon to provide a reasonable level of test coverage.
    - The test suite is not distributed as part of the installable package
- PolyChron is not currently compatibly with `uv` installed versions of Python (see [#104](https://github.com/bryonymoody/PolyChron/issues/104)). Consider using [`pyenv`](https://github.com/pyenv/pyenv) if you wish to use a non-default python installation.

## Notes for Maintainers

> [!IMPORTANT]
> This section is for project maintainers, who have write access to the [`bryonymoody/PolyChron`](https://github.com/bryonymoody/PolyChron) repository

### Creating PolyChron releases

To create a new PolyChron release:

1. Ensure that the `HEAD` of `main` is in a good working state, ready for wider release. This should include making sure that package metadata in `pyproject.toml` is correct and all CI checks pass.
    - PolyChron is following [Semantic Versioning](https://semver.org/) and as the version number should comply with [PEP 440](https://peps.python.org/pep-0440/)
2. Tag the commit which is intended for release, using the version included in `pyproject.toml` prefixed with `v` (e.g. `v0.2.0`, `v1.2.3rc1`).
3. [Create a Release](https://github.com/bryonymoody/PolyChron/releases/new) in GitHub, using the newly pushed tag, providing some Release Notes.
  - On tag push, starting with `v`, `.github/workflows/publish.yml` should upload the new version to [PyPI](https://pypi.org/)

### Python Version support

Python is on a roughly yearly release cycle, with python versions receiving 5 years of support ([docs](https://devguide.python.org/versions/)).

PolyChron aims to support officially supported python distributions, but this may require annual effort to add support for new versions, if breaking changes have occurred or required dependencies are not (yet) compatible.

When new versions of Python are released (and old versions reach end of life):

- Update the python versions used in CI workflows (`.github/workflows/*.yml`)
    - EoL versions (the oldest) can be removed, or replaced with the current oldest supported version
    - New versions should be added to the `python` version matrix
- Update package dependencies in `pyproject.toml` if required
    - Conditional versions could be removed for older python versions
    - Dependencies may need updating if binary packages such as `numpy` or `pandas` are not available or cause issues
- Update package metadata in `pyproject.toml`
- Update python versions listed in `readme.md`
- Consider updating the package source code to reflect the minimum supported python (i.e. newer features can be used, and workarounds for older versions could be removed)
