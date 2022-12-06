def points_plot(dtype="cudf", n=100):
    exec(f"import hvplot.{dtype}")
    import holoviews as hv
    from .dataset import generate_random_points

    hv.extension("bokeh")

    # returns a {dtype} DataFrame
    df = generate_random_points(nodes=n, dtype=dtype)

    # generate hvplot points chart using {dtype} DataFrame
    return df.hvplot.points(x="x", y="y", c="cluster").opts(
        height=500, width=700
    )


def curve_plot(dtype="cudf", n=100):
    exec(f"import hvplot.{dtype}")
    import holoviews as hv
    from .dataset import generate_random_points

    hv.extension("bokeh")

    # returns a {dtype} DataFrame
    df = generate_random_points(nodes=n, dtype=dtype)

    # Create line charts
    line1 = df.hvplot.line(x="vertex", y="x").opts(color="red")
    line2 = df.hvplot.line(x="vertex", y="y").opts(color="blue")
    return (line1 * line2).opts(
        ylabel="value", title="Curve Plot", width=700, height=500
    )  # overlay
