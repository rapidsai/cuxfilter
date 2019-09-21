CuDataShader Charts
===================


.. currentmodule:: cuXfilter.charts


line chart
----------

.. automethod:: cudatashader.line

Example
~~~~~~~
.. jupyter-execute::

    from cuXfilter import charts, DataFrame
    import numpy as np
    import cudf
    import random

    n = 100000                           # Number of points
    start = 1456297053                   # Start time
    end = start + 60 * 60 * 24 

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'x': np.linspace(start, end, n), 'y':np.random.normal(0, 0.3, size=n).cumsum() + 50}))   
    line_chart_1 = charts.cudatashader.line(x='x', y='y')

    d = cux_df.dashboard([line_chart_1])
    line_chart_1.view()

Scatter_geo chart
-----------------

.. automethod:: cudatashader.scatter_geo

Example
~~~~~~~
.. jupyter-execute::

    from cuXfilter import charts, DataFrame
    import cudf
    import random

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'x': [float(random.randrange(-8239000,-8229000)) for i in range(100000)], 'y':[float(random.randrange(4960000, 4980000)) for i in range(100000)]}))

    scatter_geo_chart = charts.cudatashader.scatter_geo(x='x',
                                        y='y')

    d = cux_df.dashboard([scatter_geo_chart])
    scatter_geo_chart.view()


Scatter chart
-------------
.. automethod:: cudatashader.scatter


Example
~~~~~~~
.. jupyter-execute::

    from cuXfilter import charts, DataFrame
    import cudf
    import random

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'x': [float(random.randrange(-8239000,-8229000)) for i in range(10000)], 'y':[float(random.randrange(4960000, 4980000)) for i in range(10000)]}))

    scatter_chart = charts.cudatashader.scatter(x='x',
                                         y='y')

    d = cux_df.dashboard([scatter_chart])
    scatter_chart.view()