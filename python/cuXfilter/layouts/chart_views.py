import panel as pn

def chart_view(*charts, **params):
    '''
        Description:
        
        -------------------------------------------
        Input:
        charts
        params
        -------------------------------------------

        Ouput:
        layout view
    '''
    view = pn.Column(**params, sizing_mode='scale_both')
    for chart in charts:
        if chart is not None:
            view.append(chart)
    
    return view