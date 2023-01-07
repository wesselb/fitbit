import os
from pathlib import Path

# Get the path to the configuration file.
_path_config = str(Path(__file__).parent.parent.resolve() / "config.toml")
if not os.path.exists(_path_config):
    raise FileNotFoundError(
        "Cannot find your `config.toml`. "
        "Please carefully follow the instructions from the repository."
    )

# Get the path to the SSL certificate.
_path_key = str(Path(__file__).parent.parent.resolve() / "server.pem")
if not os.path.exists(_path_key):
    raise FileNotFoundError(
        "Cannot find your `server.pem`. "
        "Please carefully follow the instructions from the repository."
    )

from plum import Dispatcher

_dispatch = Dispatcher()

from .config import *
from .rate import *
from .auth import *
from .api import *
