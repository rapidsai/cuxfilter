import inspect
import panel as pn
import param


class PlotBase(param.Parameterized):
    dtype = param.Selector(objects=["cudf", "pandas"], default="cudf")
    n = param.Integer(1000, bounds=(100, 100000))

    def plot_code(self, fn):
        return get_code(fn, self.dtype, self.n)

    @pn.depends("dtype", "n")
    def points_plot_code(self):
        return self.plot_code(self.points_plot)

    @pn.depends("dtype", "n")
    def curve_plot_code(self):
        return self.plot_code(self.curve_plot)

    @pn.depends("dtype", "n")
    def bar_plot_code(self):
        return self.plot_code(self.bar_plot)


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
    )

    return pn.widgets.Ace(
        name="code",
        language="python",
        height=360,
        width=800,
        value=result,
        readonly=True,
    )
