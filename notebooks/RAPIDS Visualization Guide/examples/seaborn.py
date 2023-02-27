import cudf
import cupy as cp
import numpy as np
import pandas as pd

from . import PlotBase


class Charts(PlotBase):
    def bar_plot(self):
        exec(f"import {self.dtype}")
        import seaborn as sns
        import panel as pn
        from matplotlib.figure import Figure

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
        # Seaborn does not take cuDF directly, convert cudf dataframe to pandas df
        df = df.to_pandas() if type(df) == cudf.DataFrame else df

        # generate seaborn bar chart
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        sns.barplot(df, x="value", y="freq", ax=ax, color="blue")
        return pn.panel(fig)

    def points_plot(self):
        import seaborn as sns
        import panel as pn
        from matplotlib.figure import Figure
        from examples.dataset import generate_random_points

        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # Seaborn does not take cuDF directly, convert cudf dataframe to pandas df
        df = df.to_pandas() if type(df) == cudf.DataFrame else df

        # Create scatter chart
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        sns.scatterplot(df, x="x", y="y", hue="cluster", ax=ax)
        return pn.panel(fig)

    def line_plot(self):
        import seaborn as sns
        import panel as pn
        from matplotlib.figure import Figure
        from examples.dataset import generate_random_points

        df = generate_random_points(
            nodes=self.n, dtype=self.dtype
        ).sort_values(by="x")

        # Seaborn does not take cuDF directly, convert cudf dataframe to pandas df
        df = df.to_pandas() if type(df) == cudf.DataFrame else df

        # Create and combine multiple line charts
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        sns.lineplot(df, x="x", y="y", ax=ax)
        return pn.panel(fig)
