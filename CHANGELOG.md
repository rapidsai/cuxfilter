# cuXfilter 0.15.0 (Date TBD)

## New Features

## Improvements
- PR #158 Add docs build script
- PR #159 Layouts Refactor
- PR #160 Install dependencies via meta packages
- PR #162 Dashboard and templates cleanup and tests
- PR #163 Updated Bokeh version to 2.1.1, added pydeck support
- PR #164 Added new Graph api, supports (nodes[cuDF], edges[cuDF]) input

## Bug Fixes
- PR #161 fixed layouts bugs

# cuXfilter 0.14.0 (03 Jun 2020)

## New Features
- PR #136 Local gpuCI build script
- PR #148 Added dask_cudf support to all charts

## Improvements
- PR #129 optimizations to grouby query, using boolean masks
- PR #135 implemented stateless non-aggregate querying
- PR #148 made groupby pre-computations consistent, made dashboard querying stateless
- PR #151 implmented autoscaling true/false for bar, line charts
add_chart now dynamically updates a running dashboard in real-time(page-refresh required)
- PR #155 Add git commit to conda package

## Bug Fixes
- PR #127 fixed logic for calculating datatiles for 2d and 3d choropleth charts
- PR #128, #130 Bug fixes and test updates
- PR #131 Filter fix for non aggregate charts(scatter, scattter-geo, line, stacked-lines, heatmap)
- PR #132 Aggregate filter accuracy fix
- PR #133 Added Nodejs dependency in build files
- PR #148 logic fixes to datatile compute and using vectorized operations instead of numba kernels for datatile compute
- PR #151 docs and minor bug fixes, also fixed dashboard server notebook issues

# cuXfilter 0.13.0 (31 March 2020)

## New Features

- PR #111 Add notebooks testing to CI

## Improvements
- PR #95 Faster import time, segregated in-notebook asset loading to save import costs, updated tests
- PR #114 Major refactor - added choropleth(2d and 3d) deckgl chart, updated chart import to skip library names. Major bug fixes

## Bug Fixes
- PR #100 Bug Fixes - Added NaN value handling for custom bin computations in numba kernels
- PR #104 Bug Fixes - fixed naming issue for geo column for choropleth3d charts, which did not allow all-small-caps names
- PR #112 - updated bokeh dependecy to be 1.* instead of >1
- PR #122 Critical bug fix - resolves rendering issue related to deckgl charts

# cuXfilter 0.12.0 (4 Feb 2020)

## New Features

- PR #111 Add notebooks testing to CI

## Improvements
- PR #84 Updated Docs and Readme with conda nightly install instructions for cuxfilter version 0.12
- PR #86 Implemented #79 - cudatashader replaced by datashader(>=0.9) with cudf & dask_cudf support
- PR #90 Implemented deck-gl_bokeh plugin and integrated with cuxfilter with layout and theme options
- PR #93 Added typescript bindings in conda build package and added tests
- PR #89 Fixed headless chrome sandbox for dashboard preview feature issue mentioned in #88
  and added full support for deck.gl/polygon layer
- PR #87 Implemented jupyter-server-proxy as discussed in #73

## Bug Fixes
- PR #78 Fix gpuCI GPU build script
- PR #83 Fix conda upload

# cuxfilter 0.2.0 (19 Sep 2019)

## New Features

- Initial release of cuxfilter python package

## Improvements

- Massive refactor and architecture change compared to the js (client-server) architecture

## Bug Fixes
