import param
from bokeh.themes import Theme as _BkTheme
from bokeh import palettes
from panel.template.theme import Theme
from ..layouts.layouts import ReactTemplate
from ..charts.constants import DATATILE_ACTIVE_COLOR, STATIC_DIR_THEMES


class DarkTheme(Theme):
    DARK = {
        "attrs": {
            "Figure": {
                "background_fill_color": "#2f2f2f",
                "border_fill_color": "#2f2f2f",
                "outline_line_color": "#E0E0E0",
                "outline_line_alpha": 0.25,
            },
            "Grid": {
                "grid_line_color": "#a0a0a0",
                "grid_line_alpha": 0.25,
                "dimension": 1,
            },
            "Axis": {
                "major_tick_line_alpha": 0.25,
                "major_tick_line_color": "#E2E2E2",
                "minor_tick_line_alpha": 0,
                "minor_tick_line_color": "#A2A2A2",
                "axis_line_alpha": 0,
                "axis_line_color": "#E0E0E0",
                "major_label_text_color": "#E2E2E2",
                "major_label_text_font": "Helvetica",
                "major_label_text_font_size": "1.025em",
                "axis_label_standoff": 10,
                "axis_label_text_color": "#a0a0a0",
                "axis_label_text_font": "Helvetica",
                "axis_label_text_font_size": "1.25em",
                "axis_label_text_font_style": "bold",
            },
            "Legend": {
                "spacing": 8,
                "glyph_width": 15,
                "label_standoff": 8,
                "label_text_color": "#E0E0E0",
                "label_text_font": "Helvetica",
                "label_text_font_size": "1.025em",
                "border_line_alpha": 0,
                "background_fill_alpha": 0.25,
                "background_fill_color": "#20262B",
                "title_text_color": "#a0a0a0",
            },
            "ColorBar": {
                "title_text_color": "#e0e0e0",
                "title_text_font": "Helvetica",
                "title_text_font_size": "1.025em",
                "title_text_font_style": "normal",
                "major_label_text_color": "#E0E0E0",
                "major_label_text_font": "Helvetica",
                "major_label_text_font_size": "1.025em",
                "background_fill_color": "#15191C",
                "background_fill_alpha": 0.4,
                "major_tick_line_alpha": 0,
                "bar_line_alpha": 0,
            },
            "Title": {
                "text_color": "#a0a0a0",
                "text_font": "helvetica",
                "text_font_size": "1.15em",
                "text_font_style": "bold",
            },
        }
    }

    bokeh_theme = _BkTheme(json=DARK)
    map_style = "mapbox://styles/mapbox/dark-v9"
    map_style_without_token = (
        "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
    )
    color_palette = list(palettes.Blues[9])
    chart_color = "#4292c6"
    css = param.Filename(default=STATIC_DIR_THEMES / "dark.css")
    datatile_active_color = DATATILE_ACTIVE_COLOR

    # Custom React Template
    _template = ReactTemplate

    # datasize_indicator_class: The color of the progress bar, one of
    # 'primary', 'secondary', 'success', 'info', 'warn', 'danger', 'light',
    # 'dark'
    datasize_indicator_class = "success"
