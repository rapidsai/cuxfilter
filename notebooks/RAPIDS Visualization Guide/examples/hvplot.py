import cudf
import cupy as cp
import numpy as np
import pandas as pd

from . import PlotBase


class Charts(PlotBase):
    def bar_plot(self):
        exec(f"import {self.dtype}")
        exec(f"import hvplot.{self.dtype}")
        import holoviews as hv

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

        # generate hvplot bar chart using {dtype} DataFrame
        return df.hvplot.bar(x="value", y="freq", title="Bar Plot", width=500, height=400)

    def points_plot(self):
        exec(f"import hvplot.{self.dtype}")
        import holoviews as hv
        from .dataset import generate_random_points

        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate hvplot points chart using {dtype} DataFrame
        return df.hvplot.points(x="x", y="y", c="cluster").opts(
            title="Scatter Plot", width=500, height=400
        )

    def line_plot(self):
        exec(f"import hvplot.{self.dtype}")
        import holoviews as hv
        from .dataset import generate_random_points

        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate hvplot line charts
        line1 = df.hvplot.line(x="vertex", y="x").opts(color="red")
        line2 = df.hvplot.line(x="vertex", y="y").opts(color="blue")

        # overlay line charts
        return (line1 * line2).opts(
            title="Line Plot", width=500, height=400
        )
