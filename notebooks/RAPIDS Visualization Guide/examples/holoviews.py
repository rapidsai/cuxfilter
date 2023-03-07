import cudf
import cupy as cp
import numpy as np
import pandas as pd

from . import PlotBase


class Charts(PlotBase):
    def bar_plot(self):
        exec(f"import {self.dtype}")
        import holoviews as hv

        # hv.extension("bokeh") # backend: bokeh/matplotlib/plotly
        df_lib = cudf if self.dtype == "cudf" else pd
        arr_lib = cp if self.dtype == "cudf" else np

        rand_arr = arr_lib.random.randint(0, 20, self.n)
        rand_vals = df_lib.Series(rand_arr).value_counts()

        df = df_lib.DataFrame(
            {
                "value": df_lib.Series(rand_vals.index),
                "freq": rand_vals,
            }
        )

        # generate holoviews points chart using {dtype} DataFrame
        return hv.Bars(df, kdims="value", vdims="freq").opts(
             title="Bar Plot", width=500, height=400
        )

    def points_plot(self):
        import holoviews as hv
        from examples.dataset import generate_random_points

        # hv.extension("bokeh") # backend: bokeh/matplotlib/plotly
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate holoviews points chart using {dtype} DataFrame
        return hv.Points(df, kdims=["x", "y"], vdims="cluster").opts(
            color="cluster", title="Scatter Plot", width=500, height=400
        )

    def line_plot(self):
        import holoviews as hv
        from examples.dataset import generate_random_points

        # hv.extension("bokeh") # backend: bokeh/matplotlib/plotly
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # Create line charts
        line_x = hv.Curve(df, kdims="vertex", vdims="x").opts(
            color="red",
        )
        line_y = hv.Curve(df, kdims="vertex", vdims="y").opts(color="blue")
        # overlay line charts
        return (line_x * line_y).opts(
            ylabel="value", title="Line Plot", width=500, height=500
        )
