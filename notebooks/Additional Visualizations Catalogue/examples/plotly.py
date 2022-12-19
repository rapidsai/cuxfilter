import cudf
import cupy as cp
import numpy as np
import pandas as pd
import panel as pn

from . import PlotBase

pn.extension("plotly")


class Charts(PlotBase):
    def bar_plot(self):
        exec(f"import {self.dtype}")
        import plotly.express as px

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
        # Bokeh does not take cuDF directly, convert cudf dataframe to pandas df
        df = df.to_pandas() if type(df) == cudf.DataFrame else df

        # generate bokeh bar chart
        fig = px.bar(df, x="value", y="freq")
        return pn.panel(fig)

    def points_plot(self):
        # Load additional libraries bokeh
        import plotly.express as px
        from examples.dataset import generate_random_points

        # returns a {dtype} DataFrame
        # Sample {dtype} DataFrame
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
        # 1        1  49.471650  927.183736        0
        # 2        2  58.157023  937.713367        0
        # ..     ...        ...         ...      ...
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # Bokeh does not take cuDF directly, convert cudf dataframe to pandas df
        df = df.to_pandas() if type(df) == cudf.DataFrame else df

        # Create scatter chart
        fig = px.scatter(
            df,
            x="x",
            y="y",
            color="cluster",
        )
        return pn.panel(fig)

    def curve_plot(self):
        # Load additional libraries bokeh
        import plotly.express as px
        from examples.dataset import generate_random_points

        # returns a {dtype}.DataFrame
        # Sample {dtype} DataFrame
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
        # 1        1  49.471650  927.183736        0
        # 2        2  58.157023  937.713367        0
        # ..     ...        ...         ...      ...
        df = generate_random_points(
            nodes=self.n, dtype=self.dtype
        ).sort_values(by="x")

        # Bokeh does not take cuDF directly, convert cudf dataframe to pandas df
        df = df.to_pandas() if type(df) == cudf.DataFrame else df

        # Create and combine multiple line charts
        fig = px.line(df, x="x", y="y")

        return pn.panel(fig)
