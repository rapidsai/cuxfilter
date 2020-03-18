Deckgl Charts
=============

.. currentmodule:: cuxfilter.charts

Choropleth3d Chart
------------------

.. automethod:: deckgl.choropleth3d

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

    chart0 = cuxfilter.charts.deckgl.choropleth3d( x='zip', color_column='_color', color_aggregate_fn='mean',
                elevation_column='elevation', elevation_factor=1000, elevation_aggregate_fn='mean', 
            geoJSONSource=geoJSONSource, data_points=size, add_interaction=True
    )

    #declare dashboard
    d = cux_df.dashboard([chart0],theme = cuxfilter.themes.dark, title='Mortgage Dashboard')

    # cuxfilter.load_notebook_assets()
    chart0.view()