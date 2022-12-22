# cuXfilter 23.02.00 (Date TBD)

Please see https://github.com/rapidsai/cuxfilter/releases/tag/v23.02.00a for the latest changes to this development branch.

# cuXfilter 22.12.00 (8 Dec 2022)

## 📖 Documentation

- Create symlink to 10_minutes_to_cuxfilter.ipynb into the notebooks fo… ([#413](https://github.com/rapidsai/cuxfilter/pull/413)) [@taureandyernv](https://github.com/taureandyernv)

## 🛠️ Improvements

- Update `panel` version ([#421](https://github.com/rapidsai/cuxfilter/pull/421)) [@ajschmidt8](https://github.com/ajschmidt8)
- Remove stale labeler ([#410](https://github.com/rapidsai/cuxfilter/pull/410)) [@raydouglass](https://github.com/raydouglass)

# cuXfilter 22.10.00 (12 Oct 2022)

## 🐛 Bug Fixes

- fix test failing on non-matching indices for newer dask version ([#402](https://github.com/rapidsai/cuxfilter/pull/402)) [@AjayThorve](https://github.com/AjayThorve)
- Notebook update: removed spaces in directory name ([#400](https://github.com/rapidsai/cuxfilter/pull/400)) [@mmccarty](https://github.com/mmccarty)

## 🚀 New Features

- Allow cupy 11 ([#401](https://github.com/rapidsai/cuxfilter/pull/401)) [@galipremsagar](https://github.com/galipremsagar)

# cuXfilter 22.08.00 (17 Aug 2022)

## 🐛 Bug Fixes

- fix/incorrect-bokeh-legend-attributes ([#381](https://github.com/rapidsai/cuxfilter/pull/381)) [@AjayThorve](https://github.com/AjayThorve)

## 📖 Documentation

- Use common custom `js` &amp; `css` code ([#394](https://github.com/rapidsai/cuxfilter/pull/394)) [@galipremsagar](https://github.com/galipremsagar)
- Branch 22.08 merge 22.06 ([#377](https://github.com/rapidsai/cuxfilter/pull/377)) [@AjayThorve](https://github.com/AjayThorve)

## 🛠️ Improvements

- Update `pyproj` version specifier ([#392](https://github.com/rapidsai/cuxfilter/pull/392)) [@ajschmidt8](https://github.com/ajschmidt8)
- Update `geopandas` version specificer ([#390](https://github.com/rapidsai/cuxfilter/pull/390)) [@ajschmidt8](https://github.com/ajschmidt8)
- Revert &quot;Allow CuPy 11&quot; ([#388](https://github.com/rapidsai/cuxfilter/pull/388)) [@galipremsagar](https://github.com/galipremsagar)
- Update `nodejs` version specifier ([#385](https://github.com/rapidsai/cuxfilter/pull/385)) [@ajschmidt8](https://github.com/ajschmidt8)
- Allow CuPy 11 ([#383](https://github.com/rapidsai/cuxfilter/pull/383)) [@jakirkham](https://github.com/jakirkham)

# cuXfilter 22.06.00 (7 Jun 2022)

## 🔗 Links

- [Development Branch](https://github.com/rapidsai/cuxfilter/tree/branch-22.06)
- [Compare with `main` branch](https://github.com/rapidsai/cuxfilter/compare/main...branch-22.06)


## 🐛 Bug Fixes

- Fixed native support for dask_cudf dataframes. Seamless integration results in a dask_cudf.DataFrame working as a drop-in replacement for a cudf.DataFrame([#359, #366](https://github.com/rapidsai/cuxfilter/pull/359, #366)) [@AjayThorve
](https://github.com/AjayThorve
)

## 🛠️ Improvements

- added `unseleced_alpha` parameter to all datashader charts, displays unselected data as transparent (default alpha=0.2) ([#366](https://github.com/rapidsai/cuxfilter/pull/366))
- added binary data transfer support for choropleth charts, which results in a much smoother experience interacting with the choropleth charts ([#366](https://github.com/rapidsai/cuxfilter/pull/366))
- Simplify conda recipe ([#373](https://github.com/rapidsai/cuxfilter/pull/373)) [@Ethyling
](https://github.com/Ethyling
)
- Forward-merge branch-22.04 to branch-22.06 ([#370](https://github.com/rapidsai/cuxfilter/pull/370)) [@Ethyling
](https://github.com/Ethyling
)
- Use conda to build python packages during GPU tests ([#368](https://github.com/rapidsai/cuxfilter/pull/368)) [@Ethyling
](https://github.com/Ethyling
)
- Use conda compilers ([#351](https://github.com/rapidsai/cuxfilter/pull/351)) [@Ethyling
](https://github.com/Ethyling
)
- Build packages using mambabuild ([#347](https://github.com/rapidsai/cuxfilter/pull/347)) [@Ethyling](https://github.com/Ethyling)

# cuXfilter 22.04.00 (6 Apr 2022)

## 🐛 Bug Fixes

- update panel version ([#361](https://github.com/rapidsai/cuxfilter/pull/361)) [@AjayThorve](https://github.com/AjayThorve)

## 📖 Documentation

- Fix/examples ([#353](https://github.com/rapidsai/cuxfilter/pull/353)) [@AjayThorve](https://github.com/AjayThorve)
- Fix deprecated code changes of `cudf` ([#348](https://github.com/rapidsai/cuxfilter/pull/348)) [@galipremsagar](https://github.com/galipremsagar)

## 🛠️ Improvements

- Temporarily disable new `ops-bot` functionality ([#357](https://github.com/rapidsai/cuxfilter/pull/357)) [@ajschmidt8](https://github.com/ajschmidt8)
- Update `bokeh` version ([#355](https://github.com/rapidsai/cuxfilter/pull/355)) [@ajschmidt8](https://github.com/ajschmidt8)
- Add `.github/ops-bot.yaml` config file ([#352](https://github.com/rapidsai/cuxfilter/pull/352)) [@ajschmidt8](https://github.com/ajschmidt8)

# cuXfilter 22.02.00 (2 Feb 2022)

## 🐛 Bug Fixes

- fix reinit function ([#345](https://github.com/rapidsai/cuxfilter/pull/345)) [@AjayThorve](https://github.com/AjayThorve)

## 📖 Documentation

- Documentation &amp; Notebook updates ([#341](https://github.com/rapidsai/cuxfilter/pull/341)) [@AjayThorve](https://github.com/AjayThorve)
- Merge branch-21.12 into branch-22.02 ([#340](https://github.com/rapidsai/cuxfilter/pull/340)) [@AjayThorve](https://github.com/AjayThorve)
- Fix/remove custom extensions ([#324](https://github.com/rapidsai/cuxfilter/pull/324)) [@AjayThorve](https://github.com/AjayThorve)

## 🛠️ Improvements

- adds layouts to in-notebook dashboards (via d.app())  similar to standalone web apps ([#324](https://github.com/rapidsai/cuxfilter/pull/324)) [@AjayThorve ](https://github.com/AjayThorve )
- enabled google colab and amazon sagemaker studio support for in-notebook dashboards ([#324](https://github.com/rapidsai/cuxfilter/pull/324)) [@AjayThorve ](https://github.com/AjayThorve )
- replace distutils.version class with packaging.version.Version ([#338](https://github.com/rapidsai/cuxfilter/pull/338)) [@AjayThorve](https://github.com/AjayThorve)
- Fix imports tests syntax ([#336](https://github.com/rapidsai/cuxfilter/pull/336)) [@Ethyling](https://github.com/Ethyling)

# cuXfilter 21.12.00 (9 Dec 2021)

## 📖 Documentation

- update docstrings examples to fix #328 ([#329](https://github.com/rapidsai/cuxfilter/pull/329)) [@AjayThorve](https://github.com/AjayThorve)

# cuXfilter 21.10.00 (7 Oct 2021)

## 🐛 Bug Fixes

- revert pyppeteer dependency changes ([#322](https://github.com/rapidsai/cuxfilter/pull/322)) [@AjayThorve](https://github.com/AjayThorve)
- Fix/unique names ([#317](https://github.com/rapidsai/cuxfilter/pull/317)) [@AjayThorve](https://github.com/AjayThorve)

## 📖 Documentation

- Branch 21.10 merge 21.08 ([#318](https://github.com/rapidsai/cuxfilter/pull/318)) [@AjayThorve](https://github.com/AjayThorve)

## 🛠️ Improvements

- fix chart names being saved as incorrect keys prior to initialization ([#325](https://github.com/rapidsai/cuxfilter/pull/325)) [@AjayThorve](https://github.com/AjayThorve)
- Skip imports tests on arm64 ([#320](https://github.com/rapidsai/cuxfilter/pull/320)) [@Ethyling](https://github.com/Ethyling)
- ENH Replace gpuci_conda_retry with gpuci_mamba_retry ([#305](https://github.com/rapidsai/cuxfilter/pull/305)) [@dillon-cullinan](https://github.com/dillon-cullinan)

# cuXfilter 21.08.00 (Date TBD)

## 🐛 Bug Fixes

- Fix/follow up to #303 ([#304](https://github.com/rapidsai/cuxfilter/pull/304)) [@AjayThorve](https://github.com/AjayThorve)
- update pyproj version ([#302](https://github.com/rapidsai/cuxfilter/pull/302)) [@AjayThorve](https://github.com/AjayThorve)

## 🛠️ Improvements

- Fix/update bokeh version ([#303](https://github.com/rapidsai/cuxfilter/pull/303)) [@AjayThorve](https://github.com/AjayThorve)
- Fix `21.08` forward-merge conflicts ([#301](https://github.com/rapidsai/cuxfilter/pull/301)) [@ajschmidt8](https://github.com/ajschmidt8)
- Fix merge conflicts ([#290](https://github.com/rapidsai/cuxfilter/pull/290)) [@ajschmidt8](https://github.com/ajschmidt8)

# cuXfilter 21.06.00 (9 Jun 2021)

## 🛠️ Improvements

- Update `geopandas` version spec ([#292](https://github.com/rapidsai/cuxfilter/pull/292)) [@ajschmidt8](https://github.com/ajschmidt8)
- Update environment variable used to determine `cuda_version` ([#289](https://github.com/rapidsai/cuxfilter/pull/289)) [@ajschmidt8](https://github.com/ajschmidt8)
- Update `CHANGELOG.md` links for calver ([#287](https://github.com/rapidsai/cuxfilter/pull/287)) [@ajschmidt8](https://github.com/ajschmidt8)
- Update docs build script ([#286](https://github.com/rapidsai/cuxfilter/pull/286)) [@ajschmidt8](https://github.com/ajschmidt8)
- support space in workspace ([#267](https://github.com/rapidsai/cuxfilter/pull/267)) [@jolorunyomi](https://github.com/jolorunyomi)

# cuXfilter 0.19.0 (21 Apr 2021)

## 🐛 Bug Fixes

- Bug fix ([#261](https://github.com//rapidsai/cuxfilter/pull/261)) [@AjayThorve](https://github.com/AjayThorve)
- Bug fixes ([#257](https://github.com//rapidsai/cuxfilter/pull/257)) [@AjayThorve](https://github.com/AjayThorve)

## 📖 Documentation

- Fea/sidebar api change ([#262](https://github.com//rapidsai/cuxfilter/pull/262)) [@AjayThorve](https://github.com/AjayThorve)
- Auto-merge branch-0.18 to branch-0.19 ([#237](https://github.com//rapidsai/cuxfilter/pull/237)) [@GPUtester](https://github.com/GPUtester)

## 🛠️ Improvements

- Update Changelog Link ([#258](https://github.com//rapidsai/cuxfilter/pull/258)) [@ajschmidt8](https://github.com/ajschmidt8)
- Prepare Changelog for Automation ([#253](https://github.com//rapidsai/cuxfilter/pull/253)) [@ajschmidt8](https://github.com/ajschmidt8)
- Update 0.18 changelog entry ([#252](https://github.com//rapidsai/cuxfilter/pull/252)) [@ajschmidt8](https://github.com/ajschmidt8)
- Fix merge conflicts in #233 ([#234](https://github.com//rapidsai/cuxfilter/pull/234)) [@ajschmidt8](https://github.com/ajschmidt8)

# cuXfilter 0.18.0 (24 Feb 2021)

## Bug Fixes 🐛

- Add static html (#238) @AjayThorve

## Documentation 📖

- Update docs (#236) @AjayThorve

## Improvements 🛠️

- Update stale GHA with exemptions &amp; new labels (#247) @mike-wendt
- Add GHA to mark issues/prs as stale/rotten (#244) @Ethyling
- Pin Node version (#239) @ajschmidt8
- fix state preserving issue for lasso-select callbacks (#231) @AjayThorve
- Prepare Changelog for Automation (#229) @ajschmidt8
- New charts - Number &amp; Card (#228) @AjayThorve
- Refactor themes (#227) @AjayThorve
- Updated templates using Panel template + React-grid-layout (#226) @AjayThorve
- Auto-label PRs based on their content (#223) @jolorunyomi
- Fix forward-merger conflicts for #218 (#221) @ajschmidt8
- Branch 0.18 merge 0.17 - fix auto merge conflicts (#219) @AjayThorve

# cuXfilter 0.17.0 (10 Dec 2020)

## New Features
- PR #208 Adds support for new dtype - datetime for all chart types except choropleths, Added new chart widget type - DateRangeSlider
## Improvements
- PR #208 refactor - merged BaseLine and BaseBar to BaseAggregate
- PR #215 cleand up gpuCI scripts
## Bug Fixes
- PR #209 remove deprecated cudf methods- `to_gpu_matrix`, `add_column` and groupby parameter `method`
- PR #212 remove redundant docs folders and files, removed bloated notebooks
- PR #214 fix map_style in choropleths, and fix custom_binning param issue in core_aggregate charts
- PR #216 fix dashboard._get_server preventing the dashboard function error for panel>=0.10.0
- PR #217 pin open-ended dependency versions
# cuXfilter 0.16.0 (21 Oct 2020)

## New Features
- PR #177 Add support for lasso selections
- PR #192 Added drop_duplicates for view_dataframe chart type
- PR #194 Added jupyterhub support

## Improvements
- PR #191 Update doc build script for CI
- PR #192 Optimize graph querying logic
- PR #193 Update ci/local/README.md

## Bug Fixes
- PR #190 fix conflicts related to auto-merge with branch-0.15
- PR #192 fixes issues with non_aggregate charts having permanent inplace querying, and query_by_indices
- PR #196 fixes issue with static http scheme applied for dashboard url, now picking scheme from base_url
- PR #198 Fix notebook error handling in gpuCI
- PR #199, #202 fix doc build issues


# cuXfilter 0.15.0 (08 Sep 2020)

## New Features
- PR #164 Added new Graph api, supports (nodes[cuDF], edges[cuDF]) input
- PR #168 Added legends to non_aggregate charts

## Improvements
- PR #158 Add docs build script
- PR #159 Layouts Refactor
- PR #160 Install dependencies via meta packages
- PR #162 Dashboard and templates cleanup and tests
- PR #163 Updated Bokeh version to 2.1.1, added pydeck support
- PR #168 Replaced interactive datashader callback throttling to debouncing
- PR #169 Added Node-Inspect Neighbor widget to graph charts
Added edge-curving
- PR #173 Updates to installation docs
- PR #180 Added documentation for deploying as a multi-user dashboard

## Bug Fixes
- PR #161 fixed layouts bugs
- PR #171 pydeck 0.4.1 fixes and geo_mapper optimizations
- PR #180 Datashader version pin fixing issues with cuDF 0.14+
- PR #186 syntax fixes to avoid CI failure

# cuxfilter 0.14.0 (03 Jun 2020)

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
- PR #165 Fix issue with incorrect docker image being used in local build script

# cuxfilter 0.13.0 (31 March 2020)

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

# cuxfilter 0.12.0 (4 Feb 2020)

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
