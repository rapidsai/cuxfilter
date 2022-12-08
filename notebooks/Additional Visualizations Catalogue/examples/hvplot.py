import panel as pn
import param
from examples import get_code
from . import PlotBase


class Charts(PlotBase):
    @param.depends("dtype", "n")
    def points_plot(self):
        exec(f"import hvplot.{self.dtype}")
        import holoviews as hv
        from .dataset import generate_random_points

        hv.extension("bokeh")

        # returns a {dtype} DataFrame
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
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # Create line charts
        line1 = df.hvplot.line(x="vertex", y="x").opts(color="red")
        line2 = df.hvplot.line(x="vertex", y="y").opts(color="blue")
        return (line1 * line2).opts(
            ylabel="value", title="Curve Plot", width=700, height=500
        )  # overlay

    @pn.depends("dtype", "n")
    def points_plot_code(self):
        return self.plot_code(self.points_plot)

    @pn.depends("dtype", "n")
    def curve_plot_code(self):
        return self.plot_code(self.curve_plot)

    def view(self):
        return pn.Tabs(
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
