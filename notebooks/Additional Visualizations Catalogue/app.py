import panel as pn
import holoviews as hv
from dataset import generate_random_points

hv.extension("bokeh")

pn.config.throttled = True


def holoviews_plot(dtype="cudf", n=100):
    data = generate_random_points(nodes=n, dtype=dtype)
    result = pn.Tabs(
        (
            "output",
            hv.Points(data=data, kdims=["x", "y"], vdims="cluster").opts(
                color="cluster", height=500, width=700
            ),
        ),
        (
            "code",
            pn.widgets.Ace(
                language="python",
                theme="monokai",
                height=360,
                value=f"""import {dtype if dtype=="cudf" else f"{dtype} as pd"}
from dataset import generate_random_points
import holoviews as hv

hv.extension("bokeh")

# generating a random dataset of type {dtype}.core.DataFrame
dataset = {
        "generate_random_points(nodes=n, dtype='cudf')"
        if dtype == "cudf"
        else "generate_random_points(nodes=n, dtype='pandas')"
    }

#Create points chart
hv.Points(data=dataset,kdims=['x','y'],vdims='cluster')
    .opts(color='cluster',height=500,width=700)""",
                width=800,
            ),
        ),
    )
    return result


explanation = pn.pane.Markdown("""holoviews""")


if __name__ == "__main__":
    n_points = pn.widgets.IntSlider(
        name="Number of points", value=10000, start=10, end=5000000, step=1000
    )
    dfs = pn.widgets.RadioButtonGroup(
        name="dataframe type",
        options=["cudf", "pandas"],
        button_type="primary",
    )

    app2 = pn.Column(
        pn.Row(
            pn.WidgetBox(dfs, n_points),
            pn.bind(holoviews_plot, dfs, n_points),
        )
    )

    pn.Row(
        pn.layout.HSpacer(),
        pn.Tabs(("Holoviews", app2)),
        pn.layout.HSpacer(),
        sizing_mode="stretch_width",
    ).show(max_opts=4, json=True, json_prefix="json")
