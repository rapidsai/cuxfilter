Deckgl Charts
=============

.. currentmodule:: cuxfilter.charts

Choropleth Chart
------------------

.. automethod:: deckgl.choropleth

Example 3d-Choropleth
~~~~~~~~~~~~~~~~~~~~~
.. jupyter-execute::

    import numpy as np
    import cudf
    import cuxfilter

    geoJSONSource='https://raw.githubusercontent.com/rapidsai/cuxfilter/GTC-2018-mortgage-visualization/javascript/demos/GTC%20demo/src/data/zip3-ms-rhs-lessprops.json'
    size = 1000

    cux_df = cuxfilter.DataFrame.from_dataframe(
        cudf.DataFrame({
                        'color':np.random.randint(20,30, size=size*10)/100,
                        'zip': list(np.arange(1,1001))*10,
                        'elevation': np.random.randint(0,1000, size=size*10)
        })
    )

    chart0 = cuxfilter.charts.choropleth( x='zip', color_column='color', color_aggregate_fn='mean',
                elevation_column='elevation', elevation_factor=1000, elevation_aggregate_fn='mean', 
            geoJSONSource=geoJSONSource, data_points=size, add_interaction=True
    )

    #declare dashboard
    d = cux_df.dashboard([chart0],theme = cuxfilter.themes.dark, title='Mortgage Dashboard')

    # use chart0.view() in a notebook cell to view the individual charts
    chart0.view()


    
Example 2d-Choropleth
~~~~~~~~~~~~~~~~~~~~~
.. jupyter-execute::

    import numpy as np
    import cudf
    import cuxfilter

    geoJSONSource='https://raw.githubusercontent.com/rapidsai/cuxfilter/GTC-2018-mortgage-visualization/javascript/demos/GTC%20demo/src/data/zip3-ms-rhs-lessprops.json'
    size = 1000

    cux_df = cuxfilter.DataFrame.from_dataframe(
        cudf.DataFrame({
                        'color':np.random.randint(20,30, size=size*10)/100,
                        'zip': list(np.arange(1,1001))*10,
                        'elevation': np.random.randint(0,1000, size=size*10)
        })
    )

    chart0 = cuxfilter.charts.choropleth( x='zip', color_column='color', color_aggregate_fn='mean',
            geoJSONSource=geoJSONSource, data_points=size, add_interaction=True
    )

    #declare dashboard
    d = cux_df.dashboard([chart0],theme = cuxfilter.themes.dark, title='Mortgage Dashboard')

    # use chart0.view() in a notebook cell to view the individual charts
    chart0.view()

