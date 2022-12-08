import holoviews as hv
import panel as pn
from examples import holoviews, hvplot
from examples import get_code
import time

pn.extension(loading_spinner="dots", loading_color="#0000ff", throttled=True)

if __name__ == "__main__":
    n_points = pn.widgets.IntSlider(
        name="Number of points", value=10000, start=10, end=100000, step=1000
    )
    dfs = pn.widgets.Select(
        name="Dataframe Type",
        options=["cudf", "pandas"],
    )

    # response_time = pn.indicators.Number(name="Response Time", value=1)

    # @pn.depends(dfs=dfs, n_points=n_points)
    # def plot(dfs, n_points, response_time=response_time):
    #     st = time.time()
    #     result = holoviews.points_plot(dfs, n_points)
    #     response_time.value = time.time() - st
    #     return result

    holoviews_charts = holoviews.Charts().view()

    hvplot_charts = hvplot.Charts().view()

    pn.Row(
        pn.layout.HSpacer(),
        pn.Tabs(("Holoviews", holoviews_charts), ("Hvplot", hvplot_charts)),
        pn.layout.HSpacer(),
        sizing_mode="stretch_width",
        width=1000,
    ).show(max_opts=4, json=True, json_prefix="json", port=5000, open=False)
