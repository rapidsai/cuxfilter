import cupy as cp
import cudf
from cuxfilter.assets import cudf_utils
import dask_cudf
from numba import cuda
from math import sqrt, ceil

from ....assets import datetime as dt


def cuda_args(shape):
    """
    Compute the blocks-per-grid and threads-per-block parameters for use when
    invoking cuda kernels
    Parameters
    ----------
    shape: int or tuple of ints
        The shape of the input array that the kernel will parallelize over
    Returns
    -------
    tuple
        Tuple of (blocks_per_grid, threads_per_block)
    """
    if isinstance(shape, int):
        shape = (shape,)

    max_threads = cuda.get_current_device().MAX_THREADS_PER_BLOCK
    # Note: We divide max_threads by 2.0 to leave room for the registers
    # occupied by the kernel. For some discussion, see
    # https://github.com/numba/numba/issues/3798.
    threads_per_block = int(ceil(max_threads / 2.0) ** (1.0 / len(shape)))
    tpb = (threads_per_block,) * len(shape)
    bpg = tuple(int(ceil(d / threads_per_block)) for d in shape)
    return bpg, tpb


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


@cuda.jit(device=True)
def bezier(start, end, control_point, steps, result):
    for i in range(steps.shape[0]):
        result[i] = (
            start * (1 - steps[i]) ** 2
            + 2 * (1 - steps[i]) * steps[i] * control_point
            + end * steps[i] ** 2
        )


@cuda.jit(device=True)
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
        result[i, 0, -1] = cp.nan
        bezier(v1_y, v2_y, control_points[i, 1], steps, result[i, 1])
        result[i, 1, -1] = cp.nan
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
        normalized_x = diff_x / sqrt(float(diff_x**2 + diff_y**2))
        normalized_y = diff_y / sqrt(float(diff_x**2 + diff_y**2))

        unit_x = -1 * normalized_y
        unit_y = normalized_x

        maxBundleSize = sqrt(float((diff_x**2 + diff_y**2))) * 0.15
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
    curve_total_steps = curve_params.pop("curve_total_steps")
    # if aggregate column exists, ignore it for bundled edges compute
    fin_df_ = bundled_edges.apply_rows(
        control_point_compute_kernel,
        incols=connected_edge_columns[:4] + ["count", "_index"],
        outcols=dict(ctrl_point_x=cp.float32, ctrl_point_y=cp.float32),
        kwargs=curve_params,
    )

    shape = (
        fin_df_.shape[0],
        len(connected_edge_columns) - 2,
        curve_total_steps + 1,
    )
    result = cp.zeros(shape=shape, dtype=cp.float32)
    steps = cp.linspace(0, 1, curve_total_steps)

    # Make sure no control points are added for rows with source==destination
    fin_df_ = fin_df_.query(edge_source + "!=" + edge_target)
    compute_curves[cuda_args(fin_df_.shape[0])](
        fin_df_[connected_edge_columns].to_cupy(),
        fin_df_[["ctrl_point_x", "ctrl_point_y"]].to_cupy(),
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
        ).fillna(cp.nan)
    else:
        return cudf.DataFrame(
            {"x": result[:, 0].flatten(), "y": result[:, 1].flatten()}
        ).fillna(cp.nan)


@cuda.jit
def connect_edges(edges, result):
    start = cuda.grid(1)
    stride = cuda.gridsize(1)
    for i in range(start, edges.shape[0], stride):
        result[i, 0, 0] = edges[i, 0]
        result[i, 0, 1] = edges[i, 2]
        result[i, 0, 2] = cp.nan
        result[i, 1, 0] = edges[i, 1]
        result[i, 1, 1] = edges[i, 3]
        result[i, 1, 2] = cp.nan
        if edges.shape[1] == 5:
            result[i, 2, 0] = edges[i, 4]
            result[i, 2, 1] = edges[i, 4]
            result[i, 2, 2] = cp.nan


def directly_connect_edges(edges, x, y, edge_aggregate_col=None):
    """
    edges: cudf DataFrame(x_src, y_src, x_dst, y_dst)
    x: str, node x-coordinate column name
    y: str, node y-coordinate column name
    edge_aggregate_col: str, edge aggregate column name, if any

    returns a cudf DataFrame of the form (
        row1 -> x_src, y_src
        row2 -> x_dst, y_dst
        row3 -> nan, nan
        ...
    ) as the input to datashader.line
    """
    # dask.distributed throws a not supported error when cudf.NA is used
    edges[x] = cp.NAN
    edges[y] = cp.NAN

    src_columns = [f"{x}_src", f"{y}_src"]
    dst_columns = [f"{x}_dst", f"{y}_dst"]
    if edge_aggregate_col:
        src_columns.append(edge_aggregate_col)
        dst_columns.append(edge_aggregate_col)

    # realign each src -> target row, as 3 rows:
    #   [[x_src, y_src], [x_dst, y_dst], [nan, nan]]
    return cudf.concat(
        [
            edges[src_columns].rename(columns={f"{x}_src": x, f"{y}_src": y}),
            edges[dst_columns].rename(columns={f"{x}_dst": x, f"{y}_dst": y}),
            edges[[x, y]],
        ]
    ).sort_index()


def calc_connected_edges(
    nodes,
    edges,
    node_x,
    node_y,
    node_id,
    edge_source,
    edge_target,
    edge_aggregate_col,
    node_x_dtype,
    node_y_dtype,
    edge_render_type="direct",
    curve_params=None,
):
    """
    calculate directly connected edges
    nodes: cudf.DataFrame/dask_cudf.DataFrame
    edges: cudf.DataFrame/dask_cudf.DataFrame
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

    nodes = nodes[[node_id, node_x, node_y]].drop_duplicates()

    nodes[node_x] = dt.to_int64_if_datetime(nodes[node_x], node_x_dtype)
    nodes[node_y] = dt.to_int64_if_datetime(nodes[node_y], node_y_dtype)

    connected_edges_df = edges.merge(
        nodes, left_on=edge_source, right_on=node_id
    )[edges_columns].reset_index(drop=True)

    connected_edges_df = connected_edges_df.merge(
        nodes,
        left_on=edge_target,
        right_on=node_id,
        suffixes=("_src", "_dst"),
    ).reset_index(drop=True)

    result = cudf.DataFrame()

    def get_df_size(df):
        if isinstance(df, dask_cudf.DataFrame):
            return df.shape[0].compute()
        return df.shape[0]

    if get_df_size(connected_edges_df) > 1:
        # shape=1 when the dataset has src == dst edges
        if edge_render_type == "direct":
            if isinstance(edges, dask_cudf.DataFrame):
                result = (
                    connected_edges_df[connected_edge_columns]
                    .map_partitions(
                        directly_connect_edges,
                        node_x,
                        node_y,
                        edge_aggregate_col,
                    )
                    .persist()
                )
                # cull any empty partitions, since dask_cudf dataframe
                # filtering may result in one
                result = cudf_utils.cull_empty_partitions(result)
            else:
                result = directly_connect_edges(
                    connected_edges_df[connected_edge_columns],
                    node_x,
                    node_y,
                    edge_aggregate_col,
                )

        elif edge_render_type == "curved":
            if isinstance(edges, dask_cudf.DataFrame):
                raise NotImplementedError(
                    "curved edges not implemented for dask_cudf Dataframes"
                )
            result = curved_connect_edges(
                connected_edges_df,
                edge_source,
                edge_target,
                connected_edge_columns,
                curve_params.copy(),
            )

    if get_df_size(result) == 0:
        result = cudf.DataFrame({k: cp.nan for k in ["x", "y"]})
        if edge_aggregate_col is not None:
            result[edge_aggregate_col] = cp.nan

    return result
