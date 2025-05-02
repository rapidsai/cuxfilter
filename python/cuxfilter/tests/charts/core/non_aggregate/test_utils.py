import pytest
import cudf
import cupy as cp
import numpy as np
from cudf.testing import assert_series_equal

# Assume the function is in this path relative to the tests
from cuxfilter.charts.core.non_aggregate.utils import point_in_polygon


@pytest.fixture
def sample_points_df():
    """Create a sample cudf DataFrame for testing."""
    data = {
        "x": [
            0.5,
            1.5,
            0.5,
            1.5,
            0.0,
            2.0,
            1.0,
            1.0,
        ],  # Inside, Inside, Outside, Outside, Boundary, Boundary, Boundary Vertex, Inside
        "y": [0.5, 0.5, 1.5, 1.5, 0.5, 0.5, 0.0, 1.0],
        "val": [1, 2, 3, 4, 5, 6, 7, 8],
    }
    return cudf.DataFrame(data)


@pytest.fixture
def simple_polygon_list():
    """A simple square polygon as a list of tuples."""
    # Square from (0,0) to (1,1)
    return [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]


@pytest.fixture
def simple_polygon_numpy(simple_polygon_list):
    """The same simple square polygon as a NumPy array."""
    return np.array(simple_polygon_list, dtype=np.float64)


def test_point_in_polygon_basic(sample_points_df, simple_polygon_list):
    """Test basic point in polygon functionality with list polygon."""
    result = point_in_polygon(sample_points_df, "x", "y", simple_polygon_list)
    # Points: Inside(T), Outside(F), Outside(F), Outside(F), Boundary(T), Outside(F), Boundary Vertex(F), Boundary Vertex(F)
    # The ray casting implementation counts points on the left edge as inside.
    expected = cudf.Series(
        [True, False, False, False, True, False, False, False],
        index=sample_points_df.index,
    )
    assert_series_equal(result, expected)


def test_point_in_polygon_numpy_poly(sample_points_df, simple_polygon_numpy):
    """Test point in polygon functionality with NumPy polygon."""
    result = point_in_polygon(sample_points_df, "x", "y", simple_polygon_numpy)
    # Expect the same result as with the list polygon
    expected = cudf.Series(
        [True, False, False, False, True, False, False, False],
        index=sample_points_df.index,
    )
    assert_series_equal(result, expected)


def test_point_in_polygon_empty_df():
    """Test with an empty DataFrame."""
    empty_df = cudf.DataFrame({"x": [], "y": []})
    polygon = [(0, 0), (1, 0), (1, 1), (0, 1)]
    result = point_in_polygon(empty_df, "x", "y", polygon)
    expected = cudf.Series([], dtype="bool", index=empty_df.index)
    assert_series_equal(result, expected)


def test_point_in_polygon_invalid_polygon(sample_points_df):
    """Test with an invalid polygon (less than 3 vertices)."""
    invalid_poly = [(0, 0), (1, 1)]  # Only two vertices
    result = point_in_polygon(sample_points_df, "x", "y", invalid_poly)
    # Expect all False as the function should handle invalid polygons gracefully
    expected = cudf.Series(
        [False] * len(sample_points_df),
        index=sample_points_df.index,
        dtype="bool",
    )
    assert_series_equal(result, expected)


def test_point_in_polygon_flat_polygon(sample_points_df):
    """Test with polygon coordinates provided as a flat list."""
    flat_poly = [0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0]  # Square
    result = point_in_polygon(sample_points_df, "x", "y", flat_poly)
    # Expect the same result
    expected = cudf.Series(
        [True, False, False, False, True, False, False, False],
        index=sample_points_df.index,
    )
    assert_series_equal(result, expected)


def test_point_in_polygon_no_points_inside(sample_points_df):
    """Test case where no points are inside the polygon."""
    # Polygon shifted away from all points
    shifted_polygon = [(10.0, 10.0), (11.0, 10.0), (11.0, 11.0), (10.0, 11.0)]
    result = point_in_polygon(sample_points_df, "x", "y", shifted_polygon)
    expected = cudf.Series(
        [False] * len(sample_points_df), index=sample_points_df.index
    )
    assert_series_equal(result, expected)


def test_point_in_polygon_all_points_inside():
    """Test case where all points are inside the polygon."""
    points_df = cudf.DataFrame({"x": [0.2, 0.5, 0.8], "y": [0.2, 0.5, 0.8]})
    # Polygon encompassing all points
    large_polygon = [(-1, -1), (2, -1), (2, 2), (-1, 2)]
    result = point_in_polygon(points_df, "x", "y", large_polygon)
    expected = cudf.Series([True, True, True], index=points_df.index)
    assert_series_equal(result, expected)


# Note: Testing points exactly *on* the boundary can be tricky due to floating-point precision
# and the specific implementation of the ray casting algorithm (e.g., handling of horizontal edges,
# vertices, and whether the < or <= operator is used for intersection check).
# The current tests include boundary points and expect False based on the `<` check in the kernel.
# If boundary inclusion rules change, these expected values might need adjustment.
