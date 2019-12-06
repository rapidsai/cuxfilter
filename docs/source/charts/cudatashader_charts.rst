CuDataShader Charts
===================


.. currentmodule:: cuxfilter.charts


line chart
----------

.. automethod:: cudatashader.line

Example
~~~~~~~
.. jupyter-execute::

    from cuxfilter import DataFrame
    from cuxfilter.charts import cudatashader
    import numpy as np
    import cudf
    import random

    n = 100000                           # Number of points
    start = 1456297053                   # Start time
    end = start + 60 * 60 * 24 

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'x': np.linspace(start, end, n), 'y':np.random.normal(0, 0.3, size=n).cumsum() + 50}))   
    line_chart_1 = cudatashader.line(x='x', y='y')

    d = cux_df.dashboard([line_chart_1])
    line_chart_1.view()

Scatter_geo chart
-----------------

.. automethod:: cudatashader.scatter_geo

Example
~~~~~~~
.. jupyter-execute::

    from cuxfilter import DataFrame
    from cuxfilter.charts import cudatashader
    import cudf
    import random

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'x': [float(random.randrange(-8239000,-8229000)) for i in range(100000)], 'y':[float(random.randrange(4960000, 4980000)) for i in range(100000)]}))

    scatter_geo_chart = cudatashader.scatter_geo(x='x',
                                        y='y')

    d = cux_df.dashboard([scatter_geo_chart])
    scatter_geo_chart.view()


Scatter chart
-------------
.. automethod:: cudatashader.scatter


Example
~~~~~~~
.. jupyter-execute::

    from cuxfilter import DataFrame
    from cuxfilter.charts import cudatashader
    import cudf
    import random

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'x': [float(random.randrange(-8239000,-8229000)) for i in range(10000)], 'y':[float(random.randrange(4960000, 4980000)) for i in range(10000)]}))

    scatter_chart = cudatashader.scatter(x='x',
                                         y='y')

    d = cux_df.dashboard([scatter_chart])
    scatter_chart.view()


Stacked_Lines chart
-------------------

.. automethod:: cudatashader.stacked_lines


Example
~~~~~~~
.. jupyter-execute::

    from cuxfilter.sampledata import signals_data
    from cuxfilter import DataFrame
    from cuxfilter.charts import cudatashader

    cux_df = DataFrame.from_dataframe(signals_data)

    stacked_lines_chart = cudatashader.stacked_lines(x='Time', y=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'x', 'y', 'z'],
                                                        colors = ["red", "grey", "black", "purple", "pink",
                                                                "yellow", "brown", "green", "orange", "blue"]
                                                        )

    d = cux_df.dashboard([stacked_lines_chart])

    stacked_lines_chart.view()


Heat Map chart
--------------

.. automethod:: cudatashader.heatmap


Example
~~~~~~~
.. jupyter-execute::

    from cuxfilter import layouts, themes, DataFrame
    from cuxfilter.charts import cudatashader
    from cuxfilter.sampledata import unemployment_data

    cux_df = DataFrame.from_dataframe(unemployment_data)

    # this is the colormap from the original NYTimes plot
    colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]

    chart1 = cudatashader.heatmap(x='Year', y='Month', aggregate_col='rate',
                                color_palette=colors, point_size=20)


    d = cux_df.dashboard([chart1], layout=layouts.single_feature, theme=themes.dark)

    chart1.view()
