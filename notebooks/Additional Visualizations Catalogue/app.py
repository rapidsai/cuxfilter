import holoviews as hv
import panel as pn
from examples import holoviews, hvplot
from examples import get_code
import time

hv.extension("bokeh")

pn.config.throttled = True
pn.extension(loading_spinner="dots", loading_color="#0000ff")


explanation = pn.pane.Markdown("""holoviews""")


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

    holoviews_chart = pn.Tabs(
        (
            "Points",
            pn.Column(
                pn.Row(
                    pn.WidgetBox(
                        dfs,
                        pn.layout.HSpacer(),
                        n_points,
                        pn.layout.HSpacer(),
                        # response_time,
                        pn.panel(
                            pn.bind(
                                get_code, holoviews.points_plot, dfs, n_points
                            ),
                        ),
                    ),
                    pn.panel(
                        pn.bind(
                            plot,
                        ),
                        loading_indicator=True,
                    ),
                ),
            ),
        ),
        (
            "Curve",
            pn.Column(
                pn.Row(
                    pn.WidgetBox(
                        dfs,
                        pn.layout.HSpacer(),
                        n_points,
                        pn.layout.HSpacer(),
                        # response_time,
                        pn.panel(
                            pn.bind(
                                get_code, holoviews.curve_plot, dfs, n_points
                            ),
                        ),
                    ),
                    pn.panel(
                        pn.bind(holoviews.curve_plot, dfs, n_points),
                        loading_indicator=True,
                    ),
                ),
            ),
        ),
    )

    hvplot_chart = pn.Tabs(
        (
            "Points",
            pn.Column(
                pn.Row(
                    pn.WidgetBox(
                        dfs,
                        pn.layout.HSpacer(),
                        n_points,
                        pn.layout.HSpacer(),
                        # response_time,
                        pn.panel(
                            pn.bind(
                                get_code, hvplot.points_plot, dfs, n_points
                            ),
                        ),
                    ),
                    pn.panel(
                        pn.bind(hvplot.points_plot, dfs, n_points),
                        loading_indicator=True,
                    ),
                ),
            ),
        ),
        (
            "Curve",
            pn.Column(
                pn.Row(
                    pn.WidgetBox(
                        dfs,
                        pn.layout.HSpacer(),
                        n_points,
                        pn.layout.HSpacer(),
                        # response_time,
                        pn.bind(get_code, hvplot.curve_plot, dfs, n_points),
                    ),
                    pn.panel(
                        pn.bind(hvplot.curve_plot, dfs, n_points),
                        loading_indicator=True,
                    ),
                ),
            ),
        ),
    )

    pn.Row(
        pn.layout.HSpacer(),
        pn.Tabs(("Holoviews", holoviews_chart), ("Hvplot", hvplot_chart)),
        pn.layout.HSpacer(),
        sizing_mode="stretch_width",
        width=1000,
    ).show(max_opts=4, json=True, json_prefix="json", port=5000, open=False)
