Panel Widgets
=============

.. currentmodule:: cuxfilter.charts

Range slider
------------

.. automethod:: panel_widgets.range_slider

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    from cuxfilter import charts, DataFrame
    import cuxfilter

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}))
    range_slider = charts.range_slider('key')

    d = cux_df.dashboard([range_slider])
    range_slider.view()


Float slider
------------
.. automethod:: panel_widgets.float_slider

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    from cuxfilter import charts, DataFrame

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 0.5, 1, 1.5, 2], 'val':[float(i + 10) for i in range(5)]}))
    float_slider = charts.float_slider('key', step_size=0.5)

    d = cux_df.dashboard([float_slider])
    float_slider.view()



Int slider
----------
.. automethod:: panel_widgets.int_slider

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    from cuxfilter import charts, DataFrame

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}))
    int_slider = charts.int_slider('val')

    d = cux_df.dashboard([int_slider])
    #view the individual int_slider chart part of the dashboard d
    int_slider.view()


Dropdown
--------
.. automethod:: panel_widgets.drop_down

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    from cuxfilter import charts, DataFrame

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}))
    drop_down = charts.drop_down('val')

    d = cux_df.dashboard([drop_down])
    #view the individual drop_down chart part of the dashboard d
    drop_down.view()


Multiselect
-----------
.. automethod:: panel_widgets.multi_select

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    from cuxfilter import charts, DataFrame

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}))
    multi_select = charts.multi_select('val')

    d = cux_df.dashboard([multi_select])
    #view the individual multi_select chart part of the dashboard d
    multi_select.view()
