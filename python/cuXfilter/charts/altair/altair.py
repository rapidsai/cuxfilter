from . import plots

def bar(x, y=None, data_points=100, add_interaction=True, aggregate_fn='count', width=400, height=400, step_size=None, step_size_type=int, **library_specific_params):
    return plots.Bar(x, y, data_points, add_interaction, aggregate_fn, width, height, step_size, step_size_type, **library_specific_params)
