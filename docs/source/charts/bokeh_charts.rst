Bokeh Charts
============

.. currentmodule:: cuxfilter.charts

Bar Chart
---------

.. automethod:: bokeh.bar

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    import cuxfilter
    import panel as pn

    cux_df = cuxfilter.DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}))
    bar_chart_1 = cuxfilter.charts.bokeh.bar('key', 'val', data_points=5, add_interaction=False)

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
    line_chart_1 = cuxfilter.charts.bokeh.line('key', 'val', data_points=5, add_interaction=False)

    d = cux_df.dashboard([line_chart_1])
    #view the individual bar chart part of the dashboard d
    #await d.preview()
    line_chart_1.view()

Choropleth Chart
----------------
.. automethod:: bokeh.choropleth

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    import cuxfilter


    cux_df = cuxfilter.DataFrame.from_dataframe(cudf.DataFrame({'states': [i for i in range(57)], 'val':[float(i + 10) for i in range(57)]}))
    choropleth_chart_1 = cuxfilter.charts.bokeh.choropleth(x = 'states', y = 'val', aggregate_fn='mean', data_points=57, add_interaction=False,
                                        geoJSONSource= 'https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_500k.json', geoJSONProperty='STATE',
                                        )

    d = cux_df.dashboard([choropleth_chart_1])
    #view the individual bar chart part of the dashboard d
    #await d.preview()
    choropleth_chart_1.view()









