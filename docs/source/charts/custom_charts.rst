Custom Charts
=============

.. currentmodule:: cuxfilter.charts

Table View Chart
----------------

.. automethod:: view_dataframe

.. jupyter-execute::
    :hide-code:

    import panel as pn
    pn.extension()


Example
~~~~~~~
.. jupyter-execute::

    import numpy as np
    import cudf
    import cuxfilter

    geoJSONSource='https://raw.githubusercontent.com/rapidsai/cuxfilter/GTC-2018-mortgage-visualization/javascript/demos/GTC%20demo/src/data/zip3-ms-rhs-lessprops.json'
    size = 1000

    cux_df = cuxfilter.DataFrame.from_dataframe(
        cudf.DataFrame({
                        '_color':np.random.randint(20,30, size=size*10)/100,
                        'zip': list(np.arange(1,1001))*10,
                        'elevation': np.random.randint(0,1000, size=size*10)
        })
    )

    chart0 = cuxfilter.charts.view_dataframe(['zip', 'elevation'])

    #declare dashboard
    d = cux_df.dashboard([chart0], title='Mortgage Dashboard')

    # cuxfilter.load_notebook_assets()
    chart0.view()
