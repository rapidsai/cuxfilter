import param
from bokeh import palettes
from panel.theme.fast import FastDefaultTheme
from panel.template import FastGridTemplate
from ..charts.constants import STATIC_DIR_THEMES


class LightTheme(FastDefaultTheme):
    map_style = "mapbox://styles/mapbox/light-v9"
    map_style_without_token = (
        "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )
    color_palette = list(palettes.Blues[9])
    chart_color = "#4292c6"
    css = param.Filename(default=STATIC_DIR_THEMES / "rapids-light.css")

    # Custom React Template
    _template = FastGridTemplate
    datasize_indicator_class = "#4292c6"
