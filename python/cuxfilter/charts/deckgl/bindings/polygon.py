from bokeh.models import ColumnDataSource, LayoutDOM, LinearColorMapper
from bokeh.core.properties import Instance, Dict, String, Any, Bool
from bokeh.util.compiler import TypeScript

from .typescript_impl import TS_CODE


class PolygonDeckGL(LayoutDOM):

    # The special class attribute ``__implementation__`` should
    # contain a string of JavaScript (or CoffeeScript) code
    # that implements the JavaScript side of the custom extension model.
    __implementation__ = TypeScript(TS_CODE)

    x = String
    layer_spec = Dict(String, Any)
    deck_spec = Dict(String, Any)
    data_source = Instance(ColumnDataSource)
    color_mapper = Instance(LinearColorMapper)
    tooltip = Bool
