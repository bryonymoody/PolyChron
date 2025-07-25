# Installation

PolyChron is a GUI application written in `python` using `tkinter`.
If you are familiar with python, `polychron` can be installed using `pip`, and [Graphviz](https://graphviz.org/)  must be installed on your system.

## Installing dependencies

`polychron` is a [Python package](https://pypi.org/project/polychron/) which uses [Graphviz](https://graphviz.org/) for graph rendering.
Before you install polychron, you should ensure a compatible version of python is available (with `pip`, `tkinter` and ideally `venv`) and should install `graphviz`.

### graphviz

Graphviz can be downloaded and installed from the [graphviz website](https://graphviz.org/download/), or using a package manager:

=== "Linux"

    ```sh
    # debian, ubuntu, etc.
    sudo apt install graphviz
    # fedora, RHEL, Rocky, etc.
    sudo dnf install graphviz
    ```

=== "macOS"

    ```sh
    # using brew (if installed)
    brew install graphviz
    ```

=== "Windows"

    ```pwsh
    # using chocolatey (if installed)
    choco install graphviz --no-progress -y
    ```

### python

`polychron` `{{ polychron_version }}` supports the following python versions:

{{ supported_python_versions }}

Newer python versions may be usable, but have not been tested.

A suitable python may be installed on your system, otherwise you will need to install `python` with `pip`, `tkinter` (and ideally `venv`) from:

- Your operating systems package manager (i.e. `apt`, `dnf`, `brew`)
- From the [Official Python Downloads](https://www.python.org/downloads/)
- Using a tool such as [`pyenv`](https://github.com/pyenv/pyenv).

    > [!WARNING]
    > `uv` managed installations of python are not currently usable with `polychron`. See [bryonymoody/PolyChron#104](https://github.com/bryonymoody/PolyChron/issues/104) for more information.

In some cases, `pip`, `tkinter` or `venv` may not be installed with the operating system's python installation and may need to be installed.

=== "Linux"

    ```sh
    # e.g. for Ubuntu/Debian
    apt-get install python3-pip python3-tk python3-venv
    ```

=== "macOS"

    ```sh
    # using brew (if python was installed with brew)
    brew install python-tk
    ```

## Installing `polychron`

### with pip <small>recommended</small> { data-toc-label="with pip" }

`polychron` is a [Python package](https://pypi.org/project/polychron/) and released versions of `polychron` can be installed from PyPI using `pip`, ideally in a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

```bash
python3 -m pip install polychron
```

### with `git`

`polychron` can be installed from source using `pip`, using the latest development version or specific releases.

=== "main"

    ```bash
    python3 -m pip install git+https://github.com/bryonymoody/PolyChron.git
    ```

=== "v0.2.0"

    ```bash
    python3 -m pip install git+https://github.com/bryonymoody/PolyChron.git@v0.2.0
    ```

Or by cloning the `git` repository from [GitHub](https://github.com/bryonymoody/PolyChron) and installing into the current python environment.

```bash
git clone https://github.com/bryonymoody/PolyChron
cd PolyChron
python3 -m pip install .
```

> [!TIP]
> If you are installing PolyChron from source as a developer, consider using an editable installation (`-e` / `--editable`) and installing the `dev`, `doc` and `test` extras.
>
> ```bash
> python3 -m pip install -e .[dev,doc,test]
> ```

## Launching `polychron`

Once installed, `polychron` can be launched from the command line.

```bash
# via the executable script
polychron
# or by running the installed polychron module
python3 -m polychron
```

For full command line options, see `-h` / `--help`, and refer to the [Using PolyChron documentation](./using/index.md) 

```bash
polychron --help
```