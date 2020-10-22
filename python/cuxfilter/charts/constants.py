from bokeh.palettes import Viridis10
import numpy as np

CUXF_NAN_COLOR = "#d3d3d3"
CUXF_DEFAULT_COLOR_PALETTE = list(Viridis10)
DATATILE_ACTIVE_COLOR = "#8ab4f7"
DATATILE_INACTIVE_COLOR = "#d3d9e2"

CUDF_DATETIME_TYPES = [
    "datetime64[{}]".format(i) for i in ["s", "ms", "us", "ns"]
] + [np.datetime64]

CUDF_TIMEDELTA_TYPE = np.timedelta64
