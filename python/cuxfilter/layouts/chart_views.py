import panel as pn


def chart_view(charts, **params):
    """
    Parameters:
    -----------
    - charts
    - **params

    Ouput:
    ------
    layout view
    """
    return pn.panel(charts, **params)
    # for chart in charts:
    #     if chart is not None:
    #         view.append(chart)
    # return view


def widget_view(*charts, **params):
    """
    Parameters:
    -----------
    - charts
    - **params

    Ouput:
    ------
    layout view
    """
    return pn.panel(*charts)
