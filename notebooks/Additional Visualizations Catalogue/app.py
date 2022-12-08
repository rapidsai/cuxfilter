import holoviews as hv
import panel as pn
from examples import holoviews, hvplot, datashader

pn.extension(loading_spinner="dots", loading_color="#0000ff", throttled=True)

if __name__ == "__main__":
    n_points = pn.widgets.IntSlider(
        name="Number of points", value=10000, start=10, end=100000, step=1000
    )
    dfs = pn.widgets.Select(
        name="Dataframe Type",
        options=["cudf", "pandas"],
    )

    pn.Row(
        pn.layout.HSpacer(),
        pn.Tabs(
            ("Holoviews", holoviews.Charts().view()),
            ("Hvplot", hvplot.Charts().view()),
            ("Datashader", datashader.Charts().view()),
            dynamic=True,
        ),
        pn.layout.HSpacer(),
        sizing_mode="stretch_width",
        width=1000,
    ).show(max_opts=4, json=True, json_prefix="json", port=5000, open=False)
