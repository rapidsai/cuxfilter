import cudf
import cupy as cp
import numpy as np
import pandas as pd

from . import PlotBase


class Charts(PlotBase):
    def bar_plot(self):
        exec(f"import {self.dtype}")
        import holoviews as hv

        # hv.extension("bokeh")
        df_lib = cudf if self.dtype == "cudf" else pd
        arr_lib = cp if self.dtype == "cudf" else np

        # returns a {dtype} DataFrame, Sample:
        #      value        freq
        # 0        0        67
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

    def points_plot(self):
        import holoviews as hv
        from examples.dataset import generate_random_points

        # hv.extension("bokeh")

        # returns a {dtype}.DataFrame, Sample:
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
        # ..     ...        ...         ...      ...
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate holoviews points chart using {dtype} DataFrame
        return hv.Points(df, kdims=["x", "y"], vdims="cluster").opts(
            color="cluster", height=500, width=700
        )

    def curve_plot(self):
        import holoviews as hv
        from examples.dataset import generate_random_points

        # hv.extension("bokeh")

        # returns a {dtype}.DataFrame, Sample:
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
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
