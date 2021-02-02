Panel Widgets
=============

.. currentmodule:: cuxfilter.charts

Range slider
------------

.. automethod:: panel_widgets.range_slider


.. jupyter-execute::
    :hide-code:

    import panel as pn
    pn.extension()


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

Date Range slider
-----------------

.. automethod:: panel_widgets.date_range_slider

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    from cuxfilter import charts, DataFrame

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'time':['2020-01-01', '2020-01-10 01', '2020-02-20 22']}))
    cux_df.data['time'] = cudf.to_datetime(cux_df.data['time'])

    date_range_slider = charts.date_range_slider('time')

    d = cux_df.dashboard([date_range_slider])
    date_range_slider.view()

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


Number Chart
------------
.. automethod:: panel_widgets.number

Example 1
~~~~~~~~~
.. jupyter-execute::

    import cudf
    from cuxfilter import charts, DataFrame

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}))
    number_chart = charts.number(x='val', aggregate_fn="mean", format="{value}%")

    d = cux_df.dashboard([number_chart])
    # view the individual number_chart chart part of the dashboard d
    number_chart.view()

Example 2
~~~~~~~~~
.. jupyter-execute::

    import cudf
    from cuxfilter import charts, DataFrame

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}))
    number_chart = charts.number(
                    expression='(key*val)*1000', aggregate_fn="mean",
                    title="custom eval expr",
                    format="{value:,}", font_size="20pt"
                )

    d = cux_df.dashboard([number_chart])
    # view the individual number chart part of the dashboard d
    number_chart.view()


Card Chart
------------
.. automethod:: panel_widgets.card

Example
~~~~~~~
.. jupyter-execute::

    import cudf
    from cuxfilter import charts, DataFrame
    import panel as pn

    cux_df = DataFrame.from_dataframe(cudf.DataFrame({'key': [0, 1, 2, 3, 4]}))
    card_chart = charts.card(pn.pane.Markdown("""
                # H1
                ## H2
                ### H3
                #### H4
                ##### H5
                ###### H6

                ### Emphasis

                Emphasis, aka italics, with *asterisks* or _underscores_.
                """), title="Test Markdown title")

    d = cux_df.dashboard([card_chart])
    # view the individual card_chart chart part of the dashboard d
    card_chart.view()
