"""A 'regular' mkdocs hook python file"""

from polychron import __version__


# Modify the mkdocs config object, overriding an 'extra' value. New values cannot be created.
def on_config(config):
    config.extra["polychron_footer_version"] = __version__
    return config
