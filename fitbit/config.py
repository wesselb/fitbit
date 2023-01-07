from typing import Tuple

import toml

from . import _dispatch, _path_config

__all__ = ["config"]


class Config:
    """A TOML configuration file that is automatically written.

    You should use this object as a dictionary where the key is a tuple of the section
    name and the entry name::

        config = Config("config.toml")
        value = config["section", "entry"]  # Read a value.
        config["section", "entry"] = value   # Write a value.

    Args:
        path (str): Path to the TOML file.
    """

    def __init__(self, path):
        self.path = path
        with open(self.path, "r") as f:
            self.data = toml.loads(f.read())

    def _write(self):
        with open(self.path, "w") as f:
            f.write(toml.dumps(self.data))

    @_dispatch
    def __getitem__(self, section_item: Tuple[str, str]):
        section, item = section_item
        return self.data[section][item]

    @_dispatch
    def __setitem__(self, section_item: Tuple[str, str], value):
        section, item = section_item
        self.data[section][item] = value
        self._write()


config = Config(_path_config)
""":class:`Config`: Configuration."""
