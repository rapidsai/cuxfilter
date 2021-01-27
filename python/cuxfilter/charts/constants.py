import numpy as np
import pathlib
from bokeh.palettes import Viridis10

BOOL_MAP = {0: "False", 1: "True"}
CUXF_NAN_COLOR = "#d3d3d3"
CUXF_DEFAULT_COLOR_PALETTE = list(Viridis10)
CUDF_DATETIME_TYPES = tuple(
    f"datetime64[{i}]" for i in ["s", "ms", "us", "ns"]
) + (np.datetime64,)
CUDF_TIMEDELTA_TYPE = np.timedelta64
DATATILE_ACTIVE_COLOR = "#8ab4f7"
DATATILE_INACTIVE_COLOR = "#d3d9e2"

# Static server paths
CUSTOM_DIST_PATH_LAYOUTS = "layouts"
CUSTOM_DIST_PATH_THEMES = "themes"
STATIC_DIR_LAYOUT = pathlib.Path(__file__).parent.parent / "layouts/assets"
STATIC_DIR_THEMES = pathlib.Path(__file__).parent.parent / "themes/assets"
