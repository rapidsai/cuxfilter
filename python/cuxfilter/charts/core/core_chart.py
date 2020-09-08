from typing import Dict
import logging
from panel.config import panel_extension
import panel as pn


class BaseChart:
    chart_type: str = None
    x: str = None
    y: str = None
    aggregate_fn: str = "count"
    color: str = None
    _height: int = 0
    _width: int = 0
    add_interaction: bool = True
    chart = None
    source = None
    source_backup = None
    data_points: int = 0
    filter_widget = None
    _library_specific_params: Dict[str, str] = {}
    _stride = None
    stride_type = int
    min_value: float = 0.0
    max_value: float = 0.0
    x_label_map = {}
    y_label_map = {}
    _initialized = False

    @property
    def name(self):
        if self.chart_type is not None:
            return self.x + "_" + self.chart_type
        else:
            return self.x + "_"

    @property
    def stride(self):
        return self._stride

    @stride.setter
    def stride(self, value):
        self._stride = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        if self.chart is not None:
            self.update_dimensions(width=value)
        if self.filter_widget is not None:
            self.filter_widget.width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        if self.chart is not None:
            self.update_dimensions(height=value)

    @property
    def library_specific_params(self):
        return self._library_specific_params

    @library_specific_params.setter
    def library_specific_params(self, value):
        self._library_specific_params = value
        self.extract_mappers()
        self.set_color()

    def set_color(self):
        if "color" in self.library_specific_params:
            self.color = self.library_specific_params["color"]

    def extract_mappers(self):
        if "x_label_map" in self.library_specific_params:
            self.x_label_map = self.library_specific_params["x_label_map"]
            self.library_specific_params.pop("x_label_map")
        if "y_label_map" in self.library_specific_params:
            self.y_label_map = self.library_specific_params["y_label_map"]
            self.library_specific_params.pop("y_label_map")

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
        return self.chart

    def add_event(self, event, callback):
        self.chart.on_event(event, callback)

    def update_dimensions(self, width=None, height=None):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def calculate_source(self, data):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def generate_chart(self):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def add_reset_event(self, callback=None):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def compute_query_dict(self, query_dict):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def reset_chart(self, data: list = []):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def reload_chart(self, data, patch_update: bool):
        print("base calc source function, to over-ridden by delegated classes")
        return -1

    def format_source_data(self, source_dict, patch_update=False):
        """
        """
        # print('function to be overridden by library specific extensions')
        return -1

    def get_source_y_axis(self):
        # print('function to be overridden by library specific extensions')
        return []

    def apply_mappers(self):
        """
        """
        # print('function to be overridden by library specific extensions')
        return -1
