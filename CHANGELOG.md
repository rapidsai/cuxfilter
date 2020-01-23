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
- PR #90 Implemented deck-gl_bokeh plugin and integrated with cuxfilter with layout and theme options
Added full support for polygon layer