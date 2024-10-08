# RAPIDS Visualization Guide Notebook
Try a user guide notebook of an end-to-end RAPIDS visualization integrated workflow using the [Divvy Bikeshare dataset](https://divvybikes.com/system-data).
![divvy dashboard](images/plotly-dash-divvy.png)

### The workflow includes integrated examples that use:
- cuDF for EDA
- cuML for KDE and Kmeans
- cuSpatial for Haversine Distance
- cuGraph for FA2
- cuxfilter for cross-filtered bars, graph, and geospatial scatter charts
- hvPlot with bokeh, datashader, and panel for multiple chart types
- Plotly Dash for Dashboard App


# RAPIDS Visualization Guide Catalog
Interactively explore the below viz libraries and compare how easy it is to switch from CPU to GPU usage. View online at [docs.rapids.ai/visualization](https://docs.rapids.ai/visualization) or run the RAPIDS Visualization Guide Catalog notebook locally. 

### Featured Libraries:
- HoloViews: Declarative objects for quickly building complex interactive plots from high-level specifications. Directly uses cuDF.
- hvPlot: Quickly return interactive plots from cuDF, Pandas, Xarray, or other data structures. Just replace .plot() with .hvplot().
- Datashader: Rasterizing huge datasets quickly as scatter, line, geospatial, or graph charts. Directly uses cuDF.
- Plotly: Charting library that supports Plotly Dash for building complex analytics applications.
- Bokeh: Charting library for building complex interactive visualizations.
- Seaborn: Static single charting library that extends matplotlib.

### Other Notable Libraries:
- Panel: A high-level app and dashboarding solution for the Python ecosystem.
- PyDeck: Python bindings for interactive spatial visualizations with webGL powered deck.gl, optimized for a Jupyter environment.
- node RAPIDS: RAPIDS bindings in nodeJS, a high performance JS/TypeScript visualization alternative to using Python.
- cuxfilter: RAPIDS developed cross filtering dashboarding tool that integrates many of the libraries above.


### Dev Guide: Generate Static Charts from Notebook for Jekyll
**Note:** code for the apps are in the `/examples/` folder.

Be sure to replace `Charts().view()` with below to pre-compute and export each chart:
`Charts().view().save('chart-name.html', embed=True, embed_json=True, save_path="./data/", json_prefix="chart-JSON")`

Then run nbconvert to generate the wrapper page and manually add each exported chart:

```bash
conda create -n viz-catalog-env -c rapidsai -c conda-forge -c nvidia \
    cudf=22.12 datashader holoviews hvplot jupyterlab plotly python=3.9 seaborn

conda activate viz-catalog-env

# export markdown only page
jupyter nbconvert --to markdown RAPIDS\ Viz\ Catalog.ipynb --output viz.md
```
