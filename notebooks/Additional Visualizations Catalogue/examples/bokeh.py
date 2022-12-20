import cudf
import cupy as cp
import numpy as np
import pandas as pd
import panel as pn

from . import PlotBase


class Charts(PlotBase):
    def bar_plot(self):
        exec(f"import {self.dtype}")
        from bokeh.plotting import figure

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
        # Bokeh does not take cuDF directly, convert cudf dataframe to pandas df
        df = df.to_pandas() if type(df) == cudf.DataFrame else df

        # generate bokeh bar chart
        p = figure(height=800, width=700, title="Bokeh Bar Chart")
        p.vbar(source=df, x="value", top="freq", width=0.9)
        return pn.pane.Bokeh(p)

    def points_plot(self):
        from bokeh.palettes import Spectral10
        from bokeh.plotting import figure
        from bokeh.transform import factor_cmap
        from examples.dataset import generate_random_points

        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # Bokeh does not take cuDF directly, convert cudf dataframe to pandas df
        df = df.to_pandas() if type(df) == cudf.DataFrame else df

        factor_s = [str(i) for i in df.cluster.unique()]
        df["cluster_s"] = df.cluster.apply(lambda i: str(i))

        # Create scatter chart
        graph = figure(title="Bokeh Scatter Graph", height=800, width=700)
        graph.scatter(
            source=df,
            x="x",
            y="y",
            fill_color=factor_cmap(
                "cluster_s", palette=Spectral10, factors=factor_s
            ),
            color="black",
        )
        return pn.pane.Bokeh(graph)

    def curve_plot(self):
        from bokeh.palettes import Spectral10
        from bokeh.plotting import figure, show
        from bokeh.transform import factor_cmap
        from examples.dataset import generate_random_points

        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # Bokeh does not take cuDF directly, convert cudf dataframe to pandas df
        df = df.to_pandas() if type(df) == cudf.DataFrame else df

        # Create and combine multiple line charts
        p = figure(
            title="Line",
            x_axis_label="x",
            y_axis_label="y",
            height=800,
            width=700,
        )
        p.line(x=df["vertex"], y=df["x"], line_width=2, color="red")
        p.line(x=df["vertex"], y=df["y"], line_width=2, color="blue")
        return pn.pane.Bokeh(p)