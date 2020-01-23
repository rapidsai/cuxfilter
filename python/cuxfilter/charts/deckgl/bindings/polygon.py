from bokeh.models import ColumnDataSource, LayoutDOM, LinearColorMapper
from bokeh.core.properties import Instance, Dict, String, Any, Bool


class PolygonDeckGL(LayoutDOM):

    # The special class attribute ``__implementation__`` should
    # contain a string of JavaScript (or CoffeeScript) code
    # that implements the JavaScript side of the custom extension model.
    __css__ = "https://api.tiles.mapbox.com/mapbox-gl-js/v1.4.0/mapbox-gl.css"
    __implementation__ = 'Polygon.ts'

    layer_spec = Dict(String, Any)
    deck_spec = Dict(String, Any)
    data_source = Instance(ColumnDataSource)
    color_mapper = Instance(LinearColorMapper)
    tooltip = Bool
