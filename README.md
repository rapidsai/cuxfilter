# <div align="left"><img src="https://rapids.ai/assets/images/rapids_logo.png" width="90px"/>&nbsp; cuXfilter

cuXfilter ( ku-cross-filter ) is a [RAPIDS](https://github.com/rapidsai) framework to connect web visualizations to GPU accelerated crossfiltering. Inspired by the javascript version of the [original]( https://github.com/crossfilter/crossfilter), it enables interactive and super fast multi-dimensional filtering of 100 million+ row tabular datasets via [cuDF](https://github.com/rapidsai/cudf). 

## RAPIDS Viz
cuXfilter is one of the core projects of the “RAPIDS viz” team. Taking the axiom that “a slider is worth a thousand queries” from @lmeyerov to heart, we want to enable fast exploratory data analytics through an easier-to-use pythonic notebook interface. 

As there are many fantastic visualization libraries available for the web, our general principle is not to create our own viz library, but to enhance others with faster acceleration, larger datasets, and better dev UX. **Basically, we want to take the headache out of interconnecting multiple charts to a GPU backend, so you can get to visually exploring data faster.**

By the way, cuXfilter is best used to interact with large (1 million+) tabular datasets. GPU’s are fast, but accessing that speedup requires some architecture overhead that isn’t worthwhile for small datasets. 

For more detailed requirements, see below.

## cuXfilter.py Architecture

The python version of cuXfilter leverage jupyter notebook and bokeh server to greatly reduce backend complexity. Currently we are focusing development efforts on the python version instead of the older javascript version.

<img src="https://github.com/rapidsai/cuxfilter/blob/master/docs/_images/RAPIDS%20Viz%20EcoSystem%20v2.png" />

### What is cuDataTiles?

cuXfilter.py implements cuDataTiles, a GPU accelerated version of data tiles based on the work of [Falcon](https://github.com/uwdata/falcon). When starting to interact with specific charts in a cuXfilter dashboard, values for the other charts are precomputed to allow for fast slider scrubbing without having to recalculate values. 

### Open Source Projects

cuXfilter wouldn’t be possible without using these great open source projects:

- [Bokeh](https://bokeh.pydata.org/en/latest/)
- [DataShader](http://datashader.org/)
- [Panel](https://panel.pyviz.org/)
- [Falcon](https://github.com/uwdata/falcon)
- [Jupyter](https://jupyter.org/about)


### Where is the original cuXfilter and Mortgage Viz Demo?

The original version (0.1) of cuXfilter, most known for the backend powering the Mortgage Viz Demo, has been moved into the `/javascript` folder. As it has a much more complicated backend and javascript API, we’ve decided to focus more on the streamlined notebook focused version in the `/python` folder.

## Get Started

```python
from cuXfilter import charts, DataFrame
from cuXfilter.layouts import layout_1, layout_2
import cudf

df = cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]})

#create cuXfilter DataFrame
cux_df = DataFrame.from_dataframe(df)
line_chart = charts.bokeh.line('key', 'val', data_points=5)
bar_chart = charts.bokeh.bar('key', 'val', data_points=5)

charts = [line_chart, bar_chart]

#create the dashboard object
d = cux_df.dashboard(charts, title='Custom dashboard', data_size_widget=True)

#display the dashboard as a web-app
d.show()
```

## Documentation

Full documentation can be found [here](https://rapidsai.github.io/cuxfilter/index.html).

Troubleshooting help can be found [here](https://rapidsai.github.io/cuxfilter/installation.html#troubleshooting).

## Dependecies

- [cudf](https://github.com/rapidsai/cudf)
- [panel](https://github.com/pyviz/panel)
- [bokeh](https://github.com/bokeh/bokeh)
- [cuDatashader](https://github.com/rapidsai/cudatashader)

## Installation

```bash

git clone https://github.com/rapidsai/cuxfilter
cd python

#if you want to install it in an isolated environment
conda create -n test_env
source activate test_env

#install dependencies
make

#install cuXfilter-py, while in the root folder
pip install -e .

#install cuDatashader
git clone https://github.com/rapidsai/cudatashader
cd cuviz
pip install -e .

#run notebooks
jupyter notebook
```

## Guides and Layout Templates

Currently supported layout templates and example code can be found [here](https://rapidsai.github.io/cuxfilter/layouts/Layouts.html)

### Currently Supported Charts
| Library  | Chart type |
| ------------- | ------------- |
| bokeh  | bar, line, choropleth  |
| cudatashader  | scatter, scatter_geo, line, heatmap  |
| panel_widgets  | range_slider, float_slider, int_slider, drop_down, multi_select  |
| custom    | view_dataframe |

Our plan is to **add support in the future** for the following libraries:
1. plotly
2. altair
3. pydeck

## Contributing Developers Guide

cuXfilter.py acts like a connector library and it is easy to add support for new libraries. The `python/cuxfilter/charts/core` directory has all the core chart classes which can be inherited and used to implement a few (viz related) functions and support dashboarding in cuXfilter directly.

You can see the examples to implement viz libraries in the bokeh and cudatashader directories. Let us know if you would like to add a chart by opening a feature request issue or submitting a PR.

For more details, check out the [contributing guide](./CONTRIBUTING.md).

## Future Work
cuXfilter development is in early stages and on going. See what we are planning next on the [projects page](https://github.com/rapidsai/cuxfilter/projects).

