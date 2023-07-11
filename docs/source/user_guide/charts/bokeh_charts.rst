Bokeh Charts
============

.. currentmodule:: cuxfilter.charts

Bar Chart
---------

.. automethod:: bokeh.bar

.. jupyter-execute::
    :hide-code:

    import panel as pn
    pn.extension()

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    import cuxfilter
    

    cux_df = cuxfilter.DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}))
    bar_chart_1 = cuxfilter.charts.bar('key', 'val', data_points=5, add_interaction=False)

    d = cux_df.dashboard([bar_chart_1])
    #view the individual bar chart part of the dashboard d
    #await d.preview()
    bar_chart_1.view()

Line Chart
----------
.. automethod:: bokeh.line

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    import cuxfilter

    cux_df = cuxfilter.DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}))
    line_chart_1 = cuxfilter.charts.line('key', 'val', data_points=5, add_interaction=False)

    d = cux_df.dashboard([line_chart_1])
    #view the individual bar chart part of the dashboard d
    #await d.preview()
    line_chart_1.view()