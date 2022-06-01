from .core_non_aggregate import BaseNonAggregate


class BaseLine(BaseNonAggregate):
    stride = 0.0
    reset_event = None
    filter_widget = None
    x_axis_tick_formatter = None
    default_color = "#8735fb"

    @property
    def color_set(self):
        return self._color_input is not None

    @property
    def color(self):
        if self.color_set:
            return self._color_input
        return self.default_color

    @property
    def name(self):
        # overwrite BaseChart name function to allow unique chart on value x
        chart_type = self.chart_type if self.chart_type else "chart"
        return f"{self.x}_{self.y}_{chart_type}_{self.title}"

    def __init__(
        self,
        x,
        y,
        data_points=100,
        add_interaction=True,
        pixel_shade_type="linear",
        color=None,
        step_size=None,
        step_size_type=int,
        width=800,
        height=400,
        title="",
        timeout=100,
        x_axis_tick_formatter=None,
        y_axis_tick_formatter=None,
        unselected_alpha=0.2,
        **library_specific_params,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            x
            y
            data_points
            add_interaction
            aggregate_fn
            width
            height
            step_size
            step_size_type
            x_label_map
            y_label_map
            width
            height
            title
            timeout
            x_axis_tick_formatter
            y_axis_tick_formatter
            **library_specific_params
        -------------------------------------------

        Ouput:

        """
        self.x = x
        self.y = y
        self.data_points = data_points
        self.add_interaction = add_interaction
        self._color_input = color
        self.stride = step_size
        self.stride_type = step_size_type
        self.pixel_shade_type = pixel_shade_type
        self.title = title
        self.timeout = timeout
        self.x_axis_tick_formatter = x_axis_tick_formatter
        self.y_axis_tick_formatter = y_axis_tick_formatter
        self.unselected_alpha = unselected_alpha
        self.library_specific_params = library_specific_params
        self.width = width
        self.height = height
