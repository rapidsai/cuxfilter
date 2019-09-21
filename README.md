# cuXfilter

cuXfilter ( ku-cross-filter ) is a [RAPIDS](https://github.com/rapidsai) framework to connect web visualizations to GPU accelerated crossfiltering. Inspired by the javascript version of the [original]( https://github.com/crossfilter/crossfilter), it enables interactive and super fast multi-dimensional filtering of 100 million+ row tabular datasets via [cuDF](https://github.com/rapidsai/cudf). 
RAPIDS Viz
cuXfilter is one of the core projects of the “RAPIDS viz” team. Taking the axiom that “a slider is worth a thousand queries” from @lmeyerov to heart, we want to enable fast exploratory data analytics through an easier-to-use pythonic notebook interface. 

As there are many fantastic visualization libraries available for the web, our general principle is not to create our own viz library, but to enhance others with faster acceleration, larger datasets, and better dev UX. Basically, we want to take the headache out of interconnecting multiple charts to a GPU backend, so you can get to visually exploring data faster.

cuXfilter is best used to interact with large (1 million+) tabular datasets. GPU’s are fast, but accessing that speedup requires some architecture overhead that isn’t worthwhile for small datasets. 

For more detailed requirements, see below.

## cuXfilter (python) General Architecture


### What is cuDataTiles?

cuXfilter implements cuDataTiles, a GPU accelerated version of data tiles based on the work of [Falcon](https://github.com/uwdata/falcon). When starting to interact with specific charts in a cuXfilter dashboard, values for the other charts are precomputed to allow for fast slider scrubbing without having to recalculate values. 

## Open Source Projects

cuXfilter wouldn’t be possible without using some of these other great open source projects:

- [Bokeh](https://bokeh.pydata.org/en/latest/)
- [DataShader](http://datashader.org/)
- [Panel](https://panel.pyviz.org/)
- [Falcon](https://github.com/uwdata/falcon)
- [Jupyter](https://jupyter.org/about)


### Where is the original cuXfilter and Mortgage Viz Demo?

The original version of cuXfilter, most known for the backend powering the Mortgage Viz Demo, has been moved into the /javascript folder. As it has a much more complicated backend and javascript API, we’ve decided to focus more on the streamlined notebook focused version in the /python folder for the foreseeable future. 

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

Full documentation [here](rapidsai.github.io/cuxfilter).


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
Currently supported layout templates can be found [here](rapidsai.github.io/cuxfilter/layouts/Layouts.html)

### Currently Supported Charts
| Library  | Chart type |
| ------------- | ------------- |
| bokeh  | bar, line, choropleth  |
| cudatashader  | scatter, scatter_geo, line, heatmap  |
| panel_widgets  | range_slider, float_slider, int_slider, drop_down, multi_select  |
| custom    | view_dataframe |

## Contributing Developers Guide

cuXfilter.py acts like a connector library and it is easy to add support for new libraries. The cuxfilter/charts/core directory has all the core chart classes which can be inherited and used to implement a few (viz related) functions and support dashboarding in cuXfilter directly.

You can see the examples to implement viz libraries in the bokeh and cudatashader directories. 

Current plan is to add support for the following libraries apart from bokeh and cudatashader:
1. plotly
2. altair
3. pydeck

Open a feature request for requesting support for libraries other than the above mentioned ones.

For more details, check out the [contributing guide](./CONTRIBUTING.md).

## Troubleshooting
Troubleshooting help can be found [here](rapidsai.github.io/cuxfilter/installation.html#troubleshooting).

## Future Work
CuXfilter development is in early stages and on going. See what we are planning to do on the [projects page](https://github.com/rapidsai/cuxfilter/projects).

