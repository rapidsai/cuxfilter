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
        exec(f"import hvplot.{self.dtype}")
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

        # generate hvplot bar chart using {dtype} DataFrame
        return df.hvplot.bar(x="value", y="freq", height=500, width=700)

    @param.depends("dtype", "n")
    def points_plot(self):
        exec(f"import hvplot.{self.dtype}")
        import holoviews as hv

        from .dataset import generate_random_points

        hv.extension("bokeh")

        # returns a {dtype} DataFrame
        # Sample {dtype} DataFrame
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
        # 1        1  49.471650  927.183736        0
        # 2        2  58.157023  937.713367        0
        # ..     ...        ...         ...      ...
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate hvplot points chart using {dtype} DataFrame
        return df.hvplot.points(x="x", y="y", c="cluster").opts(
            height=500, width=700
        )

    @param.depends("dtype", "n")
    def curve_plot(self):
        exec(f"import hvplot.{self.dtype}")
        import holoviews as hv

        from .dataset import generate_random_points

        hv.extension("bokeh")

        # returns a {dtype} DataFrame
        # Sample {dtype} DataFrame
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
        # 1        1  49.471650  927.183736        0
        # 2        2  58.157023  937.713367        0
        # ..     ...        ...         ...      ...

        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate hvplot line charts
        line1 = df.hvplot.line(x="vertex", y="x").opts(color="red")
        line2 = df.hvplot.line(x="vertex", y="y").opts(color="blue")
        # overlay line charts
        return (line1 * line2).opts(
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
