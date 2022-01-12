import panel as pn


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
    view = pn.layout.Card(**params, sizing_mode="scale_width")
    for chart in charts:
        if chart is not None:
            view.append(chart)
    return view
