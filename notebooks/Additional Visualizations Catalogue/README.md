# RAPIDS Accelerated Visualizations Catalog

## RAPIDS cuXfilter

GPU powered cross filter focused dashboards with minimal code.
https://github.com/rapidsai/cuxfilter
https://docs.rapids.ai/api/cuxfilter/stable/
Note: uses cuDF, cuGraph, cuML, and cuSpatial

## Generate static webpage

```bash
conda create -n rapids-22.12 -c rapidsai -c conda-forge -c nvidia  \
    rapids=22.12 python=3.9 cudatoolkit=11.5 \
    dash seaborn hvplot

conda activate rapids-22.12

rm -rf state/* && jupyter nbconvert --to html RAPIDS\ Viz\ Catalog.ipynb --execute --output index.html
```

## Holoviews

Powerful visualization library.
https://holoviews.org/
https://holoviews.org/reference_manual/holoviews.core.data.html?highlight=cudf#module-holoviews.core.data.cudf
https://holoviews.org/user_guide/Tabular_Datasets.html
Note: uses cuDF

### Examples

1. Line chart

![holo1](https://user-images.githubusercontent.com/35873124/189231780-25ab8fc9-40ff-4c68-a2e1-e16fd7d065d2.png)

2. Scatter chart

![holo2](https://user-images.githubusercontent.com/35873124/189231812-82c11d31-efd7-4600-b6ce-3424f3801978.png)

## hvPlot

Holoview backed chart API.
https://hvplot.holoviz.org/
https://hvplot.holoviz.org/user_guide/Introduction.html?highlight=rapids#
Note: uses cuDF

### Examples

1. Line chart

![hv1](https://user-images.githubusercontent.com/35873124/189232010-268448d6-728e-4064-bd69-53af8d55d840.png)

2. Scatter chart

![hv2](https://user-images.githubusercontent.com/35873124/189232024-cde570fe-8178-42cb-996a-c25146af2cb1.png)

## Datashader

Large dataset visualization pipline library.
https://datashader.org/
https://datashader.org/user_guide/Performance.html?highlight=cudf#data-objects
Note: uses cuDF

### Examples

1. Line chart

![ds1](https://user-images.githubusercontent.com/35873124/189232047-b4896cbd-3520-449a-a438-fa9b5c9af7b4.png)

2. Scatter chart

![ds2](https://user-images.githubusercontent.com/35873124/189232059-29e7ba3b-aaeb-4634-8bbd-d617e7f9146c.png)

## Plotly Dash

Python backed ML application library.
https://plotly.com/dash/
https://github.com/plotly/dash
https://dash.plotly.com/holoviews#gpu-accelerating-datashader-and-linked-selections-with-rapids
Note: implicit integration through Holoviews.

### Example

![Dash1](https://user-images.githubusercontent.com/35873124/189232087-b5045320-9e90-4b07-b30f-40ca5091e195.png)

## Bokeh

Python visualization library.
https://bokeh.org/
Note: integration through callbacks.

### Examples

1. Line chart

![bokeh1](https://user-images.githubusercontent.com/35873124/189232113-21886601-e264-48a0-998d-165a1facc769.png)

2. Scatter chart

![bokeh2](https://user-images.githubusercontent.com/35873124/189232453-6820f840-0daf-4b56-828b-5e09900df349.png)

## pyDeck

Python notebook implementation of the Deck.gl visualization library.
https://pydeck.gl/
Note: no direct integration.

### Examples

1. Line chart

![pyDeck1](https://user-images.githubusercontent.com/35873124/189232147-709a3643-a430-484b-82a8-47a83d39f302.png)

2. Scatter chart

![pyDeck2](https://user-images.githubusercontent.com/35873124/189232166-7ee01da4-2f82-43f6-9e95-fdd36d4d6e88.png)
