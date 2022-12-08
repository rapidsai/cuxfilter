import panel as pn
import param
from examples import get_code
from . import PlotBase


class Charts(PlotBase):
    @param.depends("dtype", "n")
    def points_plot(self):
        import holoviews as hv
        from examples.dataset import generate_random_points

        hv.extension("bokeh")

        # returns a {dtype} DataFrame
        df = generate_random_points(nodes=self.n, dtype=self.dtype)
        # generate holoviews points chart using {dtype} DataFrame
        return hv.Points(df, kdims=["x", "y"], vdims="cluster").opts(
            color="cluster", height=500, width=700
        )

    @param.depends("dtype", "n")
    def curve_plot(self):
        import holoviews as hv
        from examples.dataset import generate_random_points

        hv.extension("bokeh")

        # returns a {dtype} DataFrame
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # Create curve charts
        curve_x = hv.Curve(df, kdims="vertex", vdims="x").opts(
            color="red",
        )
        curve_y = hv.Curve(df, kdims="vertex", vdims="y").opts(color="blue")
        # overlay
        return (curve_x * curve_y).opts(
            ylabel="value", title="Curve Plot", width=700, height=500
        )

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
