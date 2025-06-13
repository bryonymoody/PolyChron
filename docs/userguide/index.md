# User Guide

> [!Warning]
> The PolyChron User guide is under development.

## Getting Started

PolyChron is not yet available via `pip` / [PyPI](https://pypi.org/), but can be installed locally from source.

For detailed installation instructions, please see the [PolyChron Readme for local installation instructions](https://github.com/bryonymoody/PolyChron).

## Using PolyChron

Once installed, polychron can be launched from the command line, via the execution script or as a python module.

```console
$ polychron

$ python3 -m polychron
```

PolyChron supports several command line options for additional usage, such as `--version` or `--verbose`

```console
$ polychron --version
PolyChron 0.2.0
```

```console
$ polychron --verbose
```

For more information, use the `-h` or `--help` options

```console
$ polychron --help
```

There are 4 main sections when using PolyChron.

```mermaid
graph LR
    g0[Project Loading];
    g1[Prior Elicitation];
    g2[Posterior Inference];
    g3[Post-MCMC Analysis];
    g0 --> g1;
    g1 --> g2;
    g2 --> g3;
```

>[!WARNING]
> @todo -  improve the user guide with additional sections

### Configuration

PolyChron can be configured through a yaml file, stored in an appropriate location for your operating system.

- Linux: `$XDG_CONFIG_HOME/polychron/config.yaml`
    - Or `$HOME/.config/polychron/config.yaml` if `XDG_CONFIG_HOME` is not set
- Windows: `%LOCALAPPDATA%/polychron/config.yaml`
<!-- - MacOs: @todo -->

This can be used to control several configuration options, such as the location of the polychron projects directory, which otherwise defaults to `polychron/projects` within your `Documents` directory.

```yaml
projects_directory: $HOME/Documents/polychron/projects
```

> [!WARNING]
> @todo - fully document the configuration options.
