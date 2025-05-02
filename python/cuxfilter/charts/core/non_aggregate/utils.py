from numba import cuda
from numba.core.errors import NumbaPerformanceWarning
import cupy as cp
import cudf
import warnings


# Define the CUDA kernel using numba.cuda.jit
# This kernel implements the ray casting algorithm
@cuda.jit(device=True)
def point_in_polygon_ray_cast(px, py, polygon_xy, num_vertices):
    """
    Check if a single point (px, py) is inside a polygon using ray casting.

    This is a device function intended to be called from a CUDA kernel.

    Parameters
    ----------
    px : float
        X-coordinate of the point.
    py : float
        Y-coordinate of the point.
    polygon_xy : cupy.ndarray
        Flat array of polygon vertices, interleaved [x0, y0, x1, y1, ...].
    num_vertices : int
        Number of vertices in the polygon.

    Returns
    -------
    bool
        True if the point is inside the polygon, False otherwise.
    """
    intersections = 0
    for j in range(num_vertices):
        vjx = polygon_xy[2 * j]
        vjy = polygon_xy[2 * j + 1]
        # Get next vertex, wrapping around
        j_plus_1 = (j + 1) % num_vertices
        vj1x = polygon_xy[2 * j_plus_1]
        vj1y = polygon_xy[2 * j_plus_1 + 1]

        # Check if the horizontal ray crosses the edge (vj, vj1)
        # Condition 1: Is the point's y-coordinate within the edge's y-range?
        if (vjy <= py < vj1y) or (vj1y <= py < vjy):
            # Condition 2: Is the edge not horizontal?
            if vjy != vj1y:
                # Calculate the x-coordinate of the intersection
                x_intersection = vjx + (py - vjy) * (vj1x - vjx) / (vj1y - vjy)
                # Condition 3: Is the intersection point to the right of
                # the point?
                if px < x_intersection:
                    intersections += 1

    # Point is inside if the number of intersections is odd
    return intersections % 2 == 1


@cuda.jit
def point_in_polygon_kernel(points_xy, polygon_xy, num_vertices, out):
    """
    CUDA kernel to check an array of points against a single polygon.

    Each thread checks one point.

    Parameters
    ----------
    points_xy : cupy.ndarray
        Flat array of point coordinates, interleaved [px0, py0, px1, py1, ...].
    polygon_xy : cupy.ndarray
        Flat array of polygon vertices, interleaved [vx0, vy0, vx1, vy1, ...].
    num_vertices : int
        Number of vertices in the polygon.
    out : cupy.ndarray
        Output boolean array. out[i] is True if points_xy[2*i:2*i+2] is
        inside the polygon.
    """
    i = cuda.grid(1)  # Global thread index

    # Check if index is within bounds (number of points)
    if i < points_xy.shape[0] // 2:
        px = points_xy[2 * i]
        py = points_xy[2 * i + 1]

        # Call the device function for the actual check
        out[i] = point_in_polygon_ray_cast(px, py, polygon_xy, num_vertices)


def point_in_polygon(df, x, y, polygon_coords):
    """
    Checks which points in a DataFrame are inside a given polygon using a CUDA
    kernel.

    Parameters
    ----------
    df : cudf.DataFrame
        DataFrame containing the points.
    x : str
        Column name for the x-coordinates of the points.
    y : str
        Column name for the y-coordinates of the points.
    polygon_coords : list of tuples or similar array-like
        Coordinates of the polygon vertices, e.g., [(x1, y1), (x2, y2), ...].
        The polygon should be closed.

    Returns
    -------
    cudf.Series
        A boolean Series indicating whether each point is inside the polygon.
    """
    if not isinstance(df, cudf.DataFrame):
        raise TypeError("Input 'df' must be a cudf.DataFrame")

    # 1. Prepare point data
    num_points = len(df)
    if num_points == 0:
        return cudf.Series([], dtype="bool", index=df.index)

    # Interleave columns directly using cudf and get cupy array
    # .values returns a cupy array for cudf Series/DataFrame
    points_xy_cp = df[[x, y]].astype(cp.float64).interleave_columns().values

    # 2. Prepare polygon data
    try:
        # Directly create cupy array from polygon_coords
        polygon_xy_cp = cp.array(polygon_coords, dtype=cp.float64)

        # Flatten if it's a list of pairs (N, 2)
        if polygon_xy_cp.ndim == 2 and polygon_xy_cp.shape[1] == 2:
            polygon_xy_cp = polygon_xy_cp.flatten()
        elif polygon_xy_cp.ndim != 1:
            raise ValueError(
                "Polygon coordinates must be list of pairs or flat list."
            )

        # Validate size
        if polygon_xy_cp.size % 2 != 0:
            raise ValueError(
                "Polygon coordinates must have an even number of elements."
            )

        num_vertices = polygon_xy_cp.size // 2

        if num_vertices < 3:
            raise ValueError("Polygon must have at least 3 vertices.")

    except (ValueError, TypeError):
        # Handle invalid polygon formats or insufficient vertices
        # Return all False as per the check at the start
        if isinstance(df.index, cudf.MultiIndex):
            idx = cudf.RangeIndex(len(df))
        else:
            idx = df.index
        return cudf.Series([False] * len(df), index=idx, dtype="bool")

    # 3. Prepare output array
    out_gpu = cp.zeros(num_points, dtype=cp.bool_)

    # 4. Configure and launch kernel
    threads_per_block = 128
    blocks_per_grid = (
        num_points + (threads_per_block - 1)
    ) // threads_per_block

    if blocks_per_grid > 0:
        # Suppress NumbaPerformanceWarning for low grid size in tests
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=NumbaPerformanceWarning,
                message="Grid size.*result in GPU under-utilization",
            )
            point_in_polygon_kernel[blocks_per_grid, threads_per_block](
                points_xy_cp, polygon_xy_cp, num_vertices, out_gpu
            )

    # 5. Return result as cudf.Series, preserving original index
    return cudf.Series(out_gpu, index=df.index)
