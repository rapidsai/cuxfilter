# from .charts import Bar, Line, Scatter, Choropleth
# import .bokeh
import panel as pn

pn.extension(
    js_files={
        "deck": "https://unpkg.com/deck.gl@latest/dist.min.js",
        "mapbox": "https://api.tiles.mapbox.com/mapbox-gl-js/v1.4.0/mapbox-gl.js",
        "deck/json": "https://unpkg.com/@deck.gl/json@latest/dist.min.js",
    },
    css_files=[
        "https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.css"
    ],
)

from .bokeh import bokeh
from .datashader import datashader
from .deckgl import deckgl
from .panel_widgets import panel_widgets
from .core.core_view_dataframe import ViewDataFrame as view_dataframe
