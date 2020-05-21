from typing import Dict
import logging
from panel.config import panel_extension
import panel as pn

from ...layouts import chart_view


class BaseWidget:
    chart_type: str = None
    x: str = None
    color: str = None
    height: int = None
    width: int = None
    chart = None
    data_points = None
    start: float = None
    end: float = None
    _stride = None
    stride_type = int
    params = None
    min_value: float = 0.0
    max_value: float = 0.0
    label_map: Dict[str, str] = None
    use_data_tiles = False
    _initialized = False

    @property
    def name(self):
        return self.x + "_" + self.chart_type

    @property
    def stride(self):
        return self._stride

    @stride.setter
    def stride(self, value):
        if value is not None:
            self.stride_type = type(value)
        self._stride = value

    def __init__(
        self,
        x,
        width=400,
        height=10,
        data_points=None,
        step_size=None,
        step_size_type=int,
        **params,
    ):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        self.x = x
        self.width = width
        self.height = height
        self.params = params
        self.data_points = data_points
        self.stride_type = step_size_type
        self.stride = step_size

        if "value" in params:
            self.value = params["value"]
            params.pop("value")
        if "label_map" in params:
            self.label_map = params["label_map"]
            self.label_map = {v: k for k, v in self.label_map.items()}
            params.pop("label_map")

    def _repr_mimebundle_(self, include=None, exclude=None):
        view = self.view()
        if self._initialized and panel_extension._loaded:
            return view._repr_mimebundle_(include, exclude)

        if self._initialized is False:
            logging.warning(
                "dashboard has not been initialized."
                "Please run cuxfilter.dashboard.Dashboard([...charts])"
                " to view this object in notebook"
            )

        if panel_extension._loaded is False:
            logging.warning(
                "notebooks assets not loaded."
                "Please run cuxfilter.load_notebooks_assets()"
                " to view this object in notebook"
            )
            if isinstance(view, pn.Column):
                return view.pprint()
        return None

    def view(self):
        return chart_view(self.chart, width=self.width)

    def add_event(self, event, callback):
        self.chart.on_event(event, callback)

    def compute_query_dict(self, query_dict):
        print("base calc source function, to over-ridden by delegated classes")

    def reload_chart(self, *args, **kwargs):
        # No reload functionality, added function for consistency
        # with other charts
        return -1
