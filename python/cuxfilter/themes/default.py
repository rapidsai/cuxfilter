import param
from bokeh import palettes
from panel.theme.fast import FastDefaultTheme, FastDarkTheme, FastStyle


class LightTheme(FastDefaultTheme):
    map_style = "mapbox://styles/mapbox/light-v9"
    map_style_without_token = (
        "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )
    color_palette = list(palettes.Blues[9])
    chart_color = "#4292c6"
    datasize_indicator_class = "#4292c6"


class CustomDarkTheme(FastDarkTheme):
    style = FastStyle(
        background_color="#181818",
        color="#ffffff",
        header_background="#1c1c1c",
        luminance=0.1,
        neutral_fill_card_rest="#212121",
        neutral_focus="#717171",
        neutral_foreground_rest="#e5e5e5",
    )
    map_style = "mapbox://styles/mapbox/dark-v9"
    map_style_without_token = (
        "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
    )
    color_palette = list(palettes.Blues[9])
    chart_color = "#4292c6"
    datasize_indicator_class = "#4292c6"
