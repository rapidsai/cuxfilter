import panel as pn
import param

from . import PlotBase


class Charts(PlotBase):
    chart = param.Selector(objects=["points", "line"], default="points")
    # datashader is best for rendering large datasets
    n = param.Integer(100000, bounds=(100000, 10000000))

    def points_plot(self):
        import datashader as ds
        import datashader.transfer_functions as tf
        import panel as pn

        from .dataset import generate_random_points

        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate datashader points chart using {dtype} DataFrame
        cvs = ds.Canvas(plot_height=400, plot_width=500)

        df["cluster"] = df["cluster"].astype("category")
        aggs = cvs.points(source=df, x="x", y="y", agg=ds.count_cat("cluster"))
        return pn.panel(tf.shade(aggs))

    def line_plot(self):
        import datashader as ds
        import datashader.transfer_functions as tf
        import panel as pn

        from .dataset import generate_random_points
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate datashader line charts
        cvs = ds.Canvas(plot_height=400, plot_width=500)
        aggs1 = cvs.line(source=df, x="vertex", y="x")
        aggs2 = cvs.line(source=df, x="vertex", y="y")
        imgs = [tf.shade(aggs1, cmap="red"), tf.shade(aggs2, cmap="blue")]
        return pn.panel(tf.stack(*imgs))
