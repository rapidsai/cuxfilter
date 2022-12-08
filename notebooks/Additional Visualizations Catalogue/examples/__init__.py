import inspect
import panel as pn
import param


class PlotBase(param.Parameterized):
    dtype = param.Selector(objects=["cudf", "pandas"], default="cudf")
    n = param.Integer(1000, bounds=(100, 100000))

    @param.depends("dtype", "n")
    def plot_code(self, fn):
        return get_code(fn, self.dtype, self.n)


def get_code(fn, dtype, n):
    result = (
        "".join(
            list(
                map(
                    lambda x: x.replace("        ", "", 1),
                    list(
                        filter(
                            lambda x: not (
                                "@param.depends" in x or "(self)" in x
                            ),
                            inspect.getsourcelines(fn)[0],
                        )
                    ),
                )
            )
        )
        .replace("=self.n", f"={n}")
        .replace("=self.dtype", f'="{dtype}"')
        .replace("{dtype}", f"{dtype}")
        .replace("return ", "")
        .replace(f'exec(f"import hvplot.{dtype}")', f"import hvplot.{dtype}")
    )

    return pn.widgets.Ace(
        name="code",
        language="python",
        height=360,
        width=800,
        value=result,
        readonly=True,
    )
