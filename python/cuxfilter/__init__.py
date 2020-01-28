from .dataframe import DataFrame

from .assets import load_notebook_assets
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
