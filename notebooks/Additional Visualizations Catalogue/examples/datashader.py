import panel as pn
import param

from . import PlotBase


class Charts(PlotBase):
    chart = param.Selector(objects=["points", "line"], default="points")
    n = param.Integer(100000, bounds=(100000, 10000000))

    def points_plot(self):
        import datashader as ds
        import datashader.transfer_functions as tf

        from .dataset import generate_random_points

        # returns a {dtype} DataFrame
        # Sample {dtype} DataFrame
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
        # 1        1  49.471650  927.183736        0
        # 2        2  58.157023  937.713367        0
        # ..     ...        ...         ...      ...
        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate datashader points chart using {dtype} DataFrame
        cvs = ds.Canvas(plot_height=500, plot_width=700)
        df["cluster"] = df["cluster"].astype("category")
        # Convert to category for giving distinct color
        aggs = cvs.points(source=df, x="x", y="y", agg=ds.count_cat("cluster"))
        return tf.shade(aggs)

    def curve_plot(self):
        import datashader as ds
        import datashader.transfer_functions as tf

        from .dataset import generate_random_points

        # returns a {dtype} DataFrame
        # Sample {dtype} DataFrame
        #     vertex          x           y  cluster
        # 0        0  67.559061  956.872971        0
        # 1        1  49.471650  927.183736        0
        # 2        2  58.157023  937.713367        0
        # ..     ...        ...         ...      ...

        df = generate_random_points(nodes=self.n, dtype=self.dtype)

        # generate datashader line charts
        cvs = ds.Canvas(plot_height=500, plot_width=700)
        aggs1 = cvs.line(source=df, x="vertex", y="x")
        aggs2 = cvs.line(source=df, x="vertex", y="y")
        imgs = [tf.shade(aggs1, cmap="red"), tf.shade(aggs2, cmap="blue")]
        return tf.stack(*imgs)
