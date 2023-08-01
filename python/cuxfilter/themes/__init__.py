from .light import LightTheme as light
from .dark import CustomDarkTheme as dark
from .rapids import RapidsTheme as rapids
from panel.theme import Fast


class RapidsFastDesign(Fast):
    _themes = {"default": rapids, "dark": dark}


class DefaultFastDesign(Fast):
    _themes = {"default": light, "dark": dark}


__all__ = ["RapidsFastDesign", "DefaultFastDesign"]
