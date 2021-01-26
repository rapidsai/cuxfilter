import pathlib

from .light import LightTheme as light
from .dark import DarkTheme as dark
from .rapids import RapidsTheme as rapids

STATIC_DIR_THEMES = pathlib.Path(__file__).parent / "assets"
