import numpy as np
import cupy as cp
import cudf
import numba
from numba import cuda
from math import sqrt

maxThreadsPerBlock = 64


def bundle_edges(edges, src="src", dst="dst"):
    # Create a duplicate table with:
    # * all the [src, dst] in the upper half
    # * all the [dst, src] pairs as the lower half, but flipped so dst->src,
    # src->dst
    edges["eid"] = edges.index
    edges_duplicated = cudf.DataFrame(
        {
            "eid": cudf.concat([edges["eid"], edges["eid"]]),
            # concat [src, dst] into the 'src' column
            src: cudf.concat([edges[src], edges[dst]]),
            # concat [dst, src] into the dst column
            dst: cudf.concat([edges[dst], edges[src]]),
        }
    )
    # Group the duplicated edgelist by [src, dst] and get the min edge id.
    # Since all the [dst, src] pairs have been flipped to [src, dst], each
    # edge with the same [src, dst] or [dst, src] vertices will be assigned
    # the same bundle id
    bundles = (
        edges_duplicated.groupby([src, dst])
        .agg({"eid": "min"})
        .reset_index()
        .rename(columns={"eid": "bid"}, copy=False)
    )

    # Join the bundle ids into the edgelist
    edges = edges.merge(bundles, on=[src, dst], how="inner")
    # Determine each bundle's size and relative offset
    bundles = edges["bid"].sort_values()
    lengths = bundles.value_counts(sort=False)
    offsets = lengths.cumsum() - lengths
    # Join the bundle segment lengths + offsets into the edgelist
    edges = edges.merge(
        cudf.DataFrame(
            {
                "start": offsets.reset_index(drop=True),
                "count": lengths.reset_index(drop=True),
                "bid": bundles.unique().reset_index(drop=True),
            }
        ),
        on="bid",
        how="left",
    )

    # Determine each edge's index relative to its bundle
    edges = edges.sort_values(by="bid").reset_index(drop=True)
    edges["_index"] = (
        cudf.core.index.RangeIndex(0, len(edges)) - edges["start"]
    ).astype("int32")

    # Re-sort the edgelist by edge id and cleanup
    edges = edges.sort_values("eid").reset_index(drop=True)
    edges = edges.rename(columns={"eid": "id"}, copy=False)
    return edges


@numba.jit
def bezier(start, end, control_point, steps, result):
    for i in range(steps.shape[0]):
        result[i] = (
            start * (1 - steps[i]) ** 2
            + 2 * (1 - steps[i]) * steps[i] * control_point
            + end * steps[i] ** 2
        )


@numba.jit
def add_aggregate_col(aggregate_col, steps, result):
    for i in range(steps.shape[0]):
        result[i] = aggregate_col


@cuda.jit
def compute_curves(nodes, control_points, result, steps):
    start = cuda.grid(1)
    stride = cuda.gridsize(1)

    for i in range(start, nodes.shape[0], stride):
        v1_x = nodes[i, 0]
        v1_y = nodes[i, 1]
        v2_x = nodes[i, 2]
        v2_y = nodes[i, 3]

        bezier(v1_x, v2_x, control_points[i, 0], steps, result[i, 0])
        result[i, 0, -1] = np.nan
        bezier(v1_y, v2_y, control_points[i, 1], steps, result[i, 1])
        result[i, 1, -1] = np.nan
        if nodes.shape[1] == 5:
            add_aggregate_col(nodes[i, 4], steps, result[i, 2])


def control_point_compute_kernel(
    x_src,
    y_src,
    count,
    _index,
    x_dst,
    y_dst,
    ctrl_point_x,
    ctrl_point_y,
    strokeWidth,
):
    """
    GPU kernel to compute control points for each edge
    """
    for i, (bcount, eindex) in enumerate(zip(count, _index)):
        midp_x = (x_src[i] + x_dst[i]) * 0.5
        midp_y = (y_src[i] + y_dst[i]) * 0.5
        diff_x = x_dst[i] - x_src[i]
        diff_y = y_dst[i] - y_src[i]
        normalized_x = diff_x / sqrt(float(diff_x ** 2 + diff_y ** 2))
        normalized_y = diff_y / sqrt(float(diff_x ** 2 + diff_y ** 2))

        unit_x = -1 * normalized_y
        unit_y = normalized_x

        maxBundleSize = sqrt(float((diff_x ** 2 + diff_y ** 2))) * 0.15
        direction = (1 - bcount % 2.0) + (-1) * bcount % 2.0
        size = (maxBundleSize / strokeWidth) * (eindex / bcount)
        if maxBundleSize < bcount * strokeWidth * 2.0:
            size = strokeWidth * 2.0 * eindex

        size += maxBundleSize

        ctrl_point_x[i] = midp_x + (unit_x * size * direction)
        ctrl_point_y[i] = midp_y + (unit_y * size * direction)


def curved_connect_edges(
    edges, edge_source, edge_target, connected_edge_columns, curve_params
):
    """
        edges: cudf DataFrame(x_src, y_src, x_dst, y_dst)

        returns a cudf DataFrame of the form (
            row1 -> x_src, y_src
            row2 -> x_dst, y_dst
            row3 -> nan, nan
            ...
        ) as the input to datashader.line
    """
    bundled_edges = bundle_edges(edges, src=edge_source, dst=edge_target)

    # if aggregate column exists, ignore it for bundled edges compute
    fin_df_ = bundled_edges.apply_rows(
        control_point_compute_kernel,
        incols=connected_edge_columns[:4] + ["count", "_index"],
        outcols=dict(ctrl_point_x=np.float32, ctrl_point_y=np.float32),
        kwargs=curve_params,
    )

    shape = (fin_df_.shape[0], len(connected_edge_columns) - 2, 101)
    result = cp.zeros(shape=shape, dtype=cp.float32)
    steps = cp.linspace(0, 1, 100)

    compute_curves[maxThreadsPerBlock, maxThreadsPerBlock](
        fin_df_[connected_edge_columns].to_gpu_matrix(),
        fin_df_[["ctrl_point_x", "ctrl_point_y"]].to_gpu_matrix(),
        result,
        steps,
    )

    if len(connected_edge_columns) == 5:
        return cudf.DataFrame(
            {
                "x": result[:, 0].flatten(),
                "y": result[:, 1].flatten(),
                connected_edge_columns[-1]: result[:, 2].flatten(),
            }
        ).fillna(np.nan)
    else:
        return cudf.DataFrame(
            {"x": result[:, 0].flatten(), "y": result[:, 1].flatten()}
        ).fillna(np.nan)


@cuda.jit
def connect_edges(edges, result):
    start = cuda.grid(1)
    for i in range(start, edges.shape[0], 1):
        result[i, 0, 0] = edges[i, 0]
        result[i, 0, 1] = edges[i, 2]
        result[i, 0, 2] = np.nan
        result[i, 1, 0] = edges[i, 1]
        result[i, 1, 1] = edges[i, 3]
        result[i, 1, 2] = np.nan
        if edges.shape[1] == 5:
            result[i, 2, 0] = edges[i, 4]
            result[i, 2, 1] = edges[i, 4]
            result[i, 2, 2] = np.nan


def directly_connect_edges(edges):
    """
        edges: cudf DataFrame(x_src, y_src, x_dst, y_dst)

        returns a cudf DataFrame of the form (
            row1 -> x_src, y_src
            row2 -> x_dst, y_dst
            row3 -> nan, nan
            ...
        ) as the input to datashader.line
    """
    result = cp.zeros(
        shape=(edges.shape[0], edges.shape[1] - 2, 3), dtype=cp.float32
    )
    connect_edges[maxThreadsPerBlock, maxThreadsPerBlock](
        edges.to_gpu_matrix(), result
    )
    if edges.shape[1] == 5:
        return cudf.DataFrame(
            {
                "x": result[:, 0].flatten(),
                "y": result[:, 1].flatten(),
                edges.columns[-1]: result[:, 2].flatten(),
            }
        ).fillna(np.nan)
    else:
        return cudf.DataFrame(
            {"x": result[:, 0].flatten(), "y": result[:, 1].flatten()}
        ).fillna(np.nan)


def calc_connected_edges(
    nodes,
    edges,
    node_x,
    node_y,
    node_id,
    edge_source,
    edge_target,
    edge_aggregate_col,
    edge_render_type="direct",
    curve_params=None,
):
    """
        calculate directly connected edges
        nodes: cudf.DataFrame
        edges: cudf.DataFrame
        edge_type: direct/curved
    """
    edges_columns = [
        edge_source,
        edge_target,
        edge_aggregate_col,
        node_x,
        node_y,
    ]

    connected_edge_columns = [
        node_x + "_src",
        node_y + "_src",
        node_x + "_dst",
        node_y + "_dst",
        edge_aggregate_col,
    ]
    # removing edge_aggregate_col if its None
    if edge_aggregate_col is None:
        edges_columns.remove(None)
        connected_edge_columns.remove(None)

    connected_edges_df = edges.merge(
        nodes, left_on=edge_source, right_on=node_id
    )[edges_columns].reset_index(drop=True)

    connected_edges_df = connected_edges_df.merge(
        nodes, left_on=edge_target, right_on=node_id, suffixes=("_src", "_dst")
    ).reset_index(drop=True)

    if edge_render_type == "direct":
        result = directly_connect_edges(
            connected_edges_df[connected_edge_columns]
        )

    elif edge_render_type == "curved":
        result = curved_connect_edges(
            connected_edges_df,
            edge_source,
            edge_target,
            connected_edge_columns,
            curve_params,
        )

    if result.shape[0] == 0:
        result = cudf.DataFrame({k: np.nan for k in ["x", "y"]})
        if edge_aggregate_col is not None:
            result[edge_aggregate_col] = np.nan

    return result
