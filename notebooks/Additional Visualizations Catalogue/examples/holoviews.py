def points_plot(dtype="cudf", n=100):
    import holoviews as hv
    from .dataset import generate_random_points

    hv.extension("bokeh")

    # returns a {dtype} DataFrame
    df = generate_random_points(nodes=n, dtype=dtype)

    # generate holoviews points chart using {dtype} DataFrame
    result = hv.Points(df, kdims=["x", "y"], vdims="cluster").opts(
        color="cluster", height=500, width=700
    )
    return result


def curve_plot(dtype="cudf", n=100):
    import holoviews as hv
    from .dataset import generate_random_points

    hv.extension("bokeh")

    # returns a {dtype} DataFrame
    df = generate_random_points(nodes=n, dtype=dtype)

    # Create curve charts
    curve_x = hv.Curve(df, kdims="vertex", vdims="x").opts(
        color="red",
    )
    curve_y = hv.Curve(df, kdims="vertex", vdims="y").opts(color="blue")

    # overlay
    return (curve_x * curve_y).opts(
        ylabel="value", title="Curve Plot", width=700, height=500
    )
