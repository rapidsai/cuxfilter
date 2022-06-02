Datashader Charts
=================


.. currentmodule:: cuxfilter.charts


line chart
----------

.. automethod:: datashader.line

.. jupyter-execute::
    :hide-code:

    import panel as pn
    pn.extension()

Example
~~~~~~~
.. jupyter-execute::

    from cuxfilter import DataFrame
    from cuxfilter.charts.datashader import line
    import numpy as np
    import cudf
    import random
    import cuxfilter

    n = 100000                           # Number of points
    start = 1456297053                   # Start time
    end = start + 60 * 60 * 24 

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'x': np.linspace(start, end, n), 'y':np.random.normal(0, 0.3, size=n).cumsum() + 50}))   
    line_chart_1 = line(x='x', y='y', unselected_alpha=0.2)

    d = cux_df.dashboard([line_chart_1])
    line_chart_1.view()


Scatter chart
-------------
.. automethod:: datashader.scatter


Example
~~~~~~~
.. jupyter-execute::

    from cuxfilter import DataFrame
    from cuxfilter.charts import scatter
    import cudf
    import random

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'x': [float(random.randrange(-8239000,-8229000)) for i in range(10000)], 'y':[float(random.randrange(4960000, 4980000)) for i in range(10000)]}))
    # setting pixel_shade_type='linear' to display legend (currently supports only log/linear)
    scatter_chart = scatter(x='x',y='y', pixel_shade_type="linear", unselected_alpha=0.2)

    d = cux_df.dashboard([scatter_chart])
    scatter_chart.view()


Stacked_Lines chart
-------------------

.. automethod:: datashader.stacked_lines


Example
~~~~~~~
.. jupyter-execute::

    from cuxfilter.sampledata import signals_data
    from cuxfilter import DataFrame
    from cuxfilter.charts import stacked_lines

    cux_df = DataFrame.from_dataframe(signals_data)

    stacked_lines_chart = stacked_lines(x='Time', y=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'x', 'y', 'z'],
                                                        colors = ["red", "grey", "black", "purple", "pink",
                                                                "yellow", "brown", "green", "orange", "blue"],
                                                        unselected_alpha=0.2
                                                        )

    d = cux_df.dashboard([stacked_lines_chart])

    stacked_lines_chart.view()

Heat Map chart
--------------

.. automethod:: datashader.heatmap


Example
~~~~~~~
.. jupyter-execute::

    from cuxfilter import layouts, themes, DataFrame
    from cuxfilter.charts import heatmap
    from cuxfilter.sampledata import unemployment_data

    cux_df = DataFrame.from_dataframe(unemployment_data)

    # this is the colormap from the original NYTimes plot
    colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]

    chart1 = heatmap(x='Year', y='Month', aggregate_col='rate',
                                color_palette=colors, point_size=20, unselected_alpha=0.2)


    d = cux_df.dashboard([chart1], layout=layouts.single_feature, theme=themes.dark)
    chart1.view()


Graph chart
--------------

.. automethod:: datashader.graph


Example
~~~~~~~
.. jupyter-execute::
    :hide-code:

    from bokeh.io import show, output_notebook
    output_notebook()
    
.. jupyter-execute::

    import cuxfilter
    import cudf

    edges = cudf.DataFrame({
        'source': [0, 0, 0, 0, 1, 1, 1, 0, 1, 2, 1, 1, 2, 0, 0],
        'target': [1, 2, 3, 1, 2, 3, 3, 2, 2, 3, 3, 3, 3, 3, 3]
    })

    nodes = cudf.DataFrame({
        'vertex': [0, 1, 2, 3],
        'x': [-3.3125157356262207,-1.8728941679000854, 0.9095478653907776, 1.9572150707244873],
        'y': [-1.6965408325195312, 2.470950126647949,-2.969928503036499,0.998791515827179]
    })

    cux_df = cuxfilter.DataFrame.load_graph((nodes, edges))

    chart0 = cuxfilter.charts.datashader.graph(node_pixel_shade_type='linear', unselected_alpha=0.2)

    d = cux_df.dashboard([chart0], layout=cuxfilter.layouts.double_feature)
    chart0.view()

