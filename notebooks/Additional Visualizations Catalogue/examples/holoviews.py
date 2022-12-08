import cudf
import cupy as cp
import numpy as np
import pandas as pd
import panel as pn
import param

from . import PlotBase


class Charts(PlotBase):
    @param.depends("dtype", "n")
    def bar_plot(self):
        exec(f"import {self.dtype}")
        import holoviews as hv

        hv.extension("bokeh")
        df_lib = cudf if self.dtype == "cudf" else pd
        arr_lib = cp if self.dtype == "cudf" else np

        # returns a {dtype} DataFrame
        # Sample {dtype} DataFrame
        #      value        freq
        # 0        0        67
        # 1        1        49
        # 2        2        58
        # ..     ...        ...
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
            height=500, width=700
        )

    @param.depends("dtype", "n")
    def points_plot(self):
        import holoviews as hv
        from examples.dataset import generate_random_points

        hv.extension("bokeh")

        # returns a {dtype} DataFrame
        # Sample {dtype} DataFrame
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
        # 1        1  49.471650  927.183736        0
        # 2        2  58.157023  937.713367        0
        # ..     ...        ...         ...      ...
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate holoviews points chart using {dtype} DataFrame
        return hv.Points(df, kdims=["x", "y"], vdims="cluster").opts(
            color="cluster", height=500, width=700
        )

    @param.depends("dtype", "n")
    def curve_plot(self):
        import holoviews as hv
        from examples.dataset import generate_random_points

        hv.extension("bokeh")

        # returns a {dtype}.DataFrame
        # Sample {dtype} DataFrame
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
        # 1        1  49.471650  927.183736        0
        # 2        2  58.157023  937.713367        0
        # ..     ...        ...         ...      ...
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # Create curve charts
        curve_x = hv.Curve(df, kdims="vertex", vdims="x").opts(
            color="red",
        )
        curve_y = hv.Curve(df, kdims="vertex", vdims="y").opts(color="blue")
        # overlay line charts
        return (curve_x * curve_y).opts(
            ylabel="value", title="Curve Plot", width=700, height=500
        )

    def view(self):
        return pn.Tabs(
            (
                "Bar",
                pn.Row(
                    pn.WidgetBox(self.param, self.bar_plot_code),
                    pn.panel(self.bar_plot, loading_indicator=True),
                ),
            ),
            (
                "Points",
                pn.Row(
                    pn.WidgetBox(self.param, self.points_plot_code),
                    pn.panel(self.points_plot, loading_indicator=True),
                ),
            ),
            (
                "Curve",
                pn.Row(
                    pn.WidgetBox(self.param, self.curve_plot_code),
                    pn.panel(self.curve_plot, loading_indicator=True),
                ),
            ),
            dynamic=True,
        )
