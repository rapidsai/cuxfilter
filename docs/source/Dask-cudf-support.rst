cuxfilter with multi-GPU using dask_cudf
========================================

`Dask-cuDF <https://github.com/rapidsai/cudf/tree/main/python/dask_cudf>`_ extends Dask where necessary to allow its DataFrame partitions to be processed by cuDF GPU DataFrames as opposed to Pandas DataFrames. For instance, when you call dask_cudf.read_csv(…), your cluster’s GPUs do the work of parsing the CSV file(s) with underlying cudf.read_csv().

When to use cuDF and Dask-cuDF
------------------------------

If your workflow is fast enough on a single GPU or your data comfortably fits in memory on a single GPU, you would want to use cuDF. If you want to distribute your workflow across multiple GPUs, have more data than you can fit in memory on a single GPU, or want to analyze data spread across many files at once, you would want to use Dask-cuDF.

A very useful guide to using Dask-cudf can be found `here <https://docs.rapids.ai/api/cudf/stable/user_guide/10min.html>`_

Cuxfilter with Dask-cudf
------------------------

Using cuxfilter with Dask-cudf is a very seamless experience, and passing in a `dask_cudf.DataFrame` object, instead of `cudf.DataFrame` object should just work, without any other modifications. The `dask_cudf.DataFrame` should however be initialized with it's partitions set, before passing it the the `cuxfilter.DataFrame.from_dataframe` function.

For more information and examples, please visit the cuxfilter repository with `dask_cudf notebooks <https://github.com/rapidsai/cuxfilter/tree/branch-22.06/notebooks/notebooks/cuxfilter%20with%20dask_cudf>`_


.. list-table:: Currently Supported Charts
    :widths: 50 50
    :header-rows: 1

    * - Library
      - Chart type
    * - bokeh
      - bar, line
    * - datashader
      - scatter, scatter_geo, line, stacked_lines, heatmap, graph(note: edge rendering support is limited for now)
    * - panel_widgets
      - range_slider, date_range_slider, float_slider, int_slider, drop_down, multi_select, card, number
    * - custom
      - view_dataframe
    * - deckgl
      - choropleth(3d and 2d)