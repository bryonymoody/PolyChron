
# Configuration

PolyChron can be configured through an **optional** `yaml` file, stored in an appropriate location for your operating system.

- Linux: `$XDG_CONFIG_HOME/polychron/config.yaml`
    - Or `$HOME/.config/polychron/config.yaml` if `XDG_CONFIG_HOME` is not set
- Windows: `%LOCALAPPDATA%/polychron/config.yaml`
<!-- - MacOs: @todo -->

For example: 

```yaml
projects_directory: $HOME/Documents/polychron/projects
verbose: false
geometry: "1920x1080"
```


The following configuration options are available:

| name | type | description | 
|-----|-----|-----|
| `projects_directory` | `string` | The location of the polychron projects directory on disk, which defaults to `~/Documents/polychron/projects` | 
| `verbose` | `bool` | If verbose output should be printed by polychron | 
| `geometry` | `string` | The initial window geometry for the main polychron window, in the form `<width>x<height>` |
