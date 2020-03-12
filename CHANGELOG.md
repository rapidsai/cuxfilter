# cuXfilter 0.14.0 (Date TBD)

## New Features

## Improvements

## Bug Fixes

# cuXfilter 0.13.0 (TBD)

## New Features

- PR #111 Add notebooks testing to CI

## Improvements

## Bug Fixes


# cuxfilter 0.2.0 (19 Sep 2019)

## New Features

- Initial release of cuxfilter python package

## Improvements

- Massive refactor and architecture change compared to the js (client-server) architecture

## Bug Fixes

- PR #78 Fix gpuCI GPU build script
- PR #83 Fix conda upload
- PR #84 Updated Docs and Readme with conda nightly install instructions for cuxfilter version 0.12
- PR #86 Implemented #79 - cudatashader replaced by datashader(>=0.9) with cudf & dask_cudf support
- PR #87 Implemented jupyter-server-proxy as discussed in #73
- PR #89 Fixed headless chrome sandbox for dashboard preview feature issue mentioned in #88
- PR #90 Implemented deck-gl_bokeh plugin and integrated with cuxfilter with layout and theme options
  and added full support for deck.gl/polygon layer
- PR #93 Added typescript bindings in conda build package and added tests
- PR #95 Faster import time, segregated in-notebook asset loading to save import costs, updated tests
- PR #100 Bug Fixes - Added NaN value handling for custom bin computations in numba kernels
- PR #104 Bug Fixes - fixed naming issue for geo column for choropleth3d charts, which did not allow all-small-caps names
- PR #112 - updated bokeh dependecy to be 1.* instead of >1