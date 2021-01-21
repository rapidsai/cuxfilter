import panel as pn


def is_widget(obj):
    return "widget" in obj.chart_type or obj.chart_type == "datasize_indicator"


def chart_view(*charts, **params):
    """
    Parameters:
    -----------
    - charts
    - **params

    Ouput:
    ------
    layout view
    """
    view = pn.layout.Card(**params, sizing_mode="stretch_both")
    for chart in charts:
        if chart is not None:
            view.append(chart)
    return view
