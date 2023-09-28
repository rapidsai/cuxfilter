import inspect
import panel as pn
import param


class PlotBase(param.Parameterized):
    chart = param.Selector(objects=["bar", "points", "line"], default="bar")
    dtype = param.Selector(objects=["cudf", "pandas"], default="cudf")
    n = param.Integer(1000, bounds=(100, 100000))

    @pn.depends("chart", "dtype", "n")
    def plot_code(self):
        if self.chart == "bar":
            return get_code(self.bar_plot, self.dtype, self.n)
        elif self.chart == "points":
            return get_code(self.points_plot, self.dtype, self.n)
        return get_code(self.line_plot, self.dtype, self.n)

    @pn.depends("chart", "dtype", "n")
    def plot(self):
        if self.chart == "bar":
            return self.bar_plot()
        elif self.chart == "points":
            return self.points_plot()
        return self.line_plot()

    @pn.depends("chart", "dtype", "n")
    def view(self):
        # return self.plot
        return pn.Column(
            pn.Row("**Chart Options**"),
            pn.Row(self.param.chart, self.param.dtype, self.param.n, sizing_mode='stretch_width'),
            pn.Row(self.plot_code, self.plot)
        )

def get_code(fn, dtype, n):
    result = (
        "".join(
            list(
                map(
                    lambda x: x.replace("        ", "", 1),
                    list(
                        filter(
                            lambda x: not (
                                "@param.depends" in x
                                or "(self)" in x
                                or x.lstrip().startswith(("df_lib", "arr_lib"))
                                or (
                                    dtype == "pandas"
                                    and (
                                        x.lstrip().startswith("# Bokeh")
                                        or x.lstrip().startswith("# Seaborn")
                                        or x.lstrip().startswith("# Plotly")
                                        or "df.to_pandas()" in x
                                    )
                                )
                            ),
                            inspect.getsourcelines(fn)[0],
                        )
                    ),
                )
            )
        )
        .replace("self.n", f"{n}")
        .replace("=self.dtype", f'="{dtype}"')
        .replace("{dtype}", f"{dtype}")
        .replace("return ", "")
        .replace(
            'exec(f"import hvplot.{self.dtype}")', f"import hvplot.{dtype}"
        )
        .replace(
            'exec(f"import {self.dtype}")',
            f"import {dtype if dtype == 'cudf' else dtype+' as pd'}\nimport {'cupy as cp' if dtype == 'cudf' else 'numpy as np'}",
        )
        .replace("df_lib", f"{dtype if dtype=='cudf' else 'pd'}")
        .replace("arr_lib", f"{'cp' if dtype=='cudf' else 'np'}")
        .replace(" if type(df) == cudf.DataFrame else df", "")
        .replace("# hv.extension", "hv.extension")
        .replace("# pn.extension", "pn.extension")
    )

    return pn.pane.Markdown("```python \n" + result + "```", width=500)
