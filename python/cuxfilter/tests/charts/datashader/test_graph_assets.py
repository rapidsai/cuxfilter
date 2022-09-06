import dask_cudf
import pytest
import cudf
import cupy as cp
from cuxfilter.charts.datashader.custom_extensions import graph_assets

from ..utils import initialize_df, df_types

nodes_args = {"vertex": [0, 1, 2, 3], "x": [0, 1, 1, 2], "y": [0, 1, 2, 0]}
edges_args = {"source": [1, 1], "target": [0, 1], "color": [10, 11]}
result_args = {
    "x": cudf.Series(
        [1.0, 0.0, cp.NAN, 1.0, 1.0, cp.NAN],
    ),
    "y": cudf.Series(
        [1.0, 0.0, cp.NAN, 1.0, 1.0, cp.NAN],
    ),
    "color": cudf.Series(
        [10.0, 10.0, cp.NAN, 11.0, 11.0, cp.NAN],
    ),
}

nodes = [initialize_df(type, nodes_args) for type in df_types]
edges = [initialize_df(type, edges_args) for type in df_types]
results = [initialize_df(type, result_args) for type in df_types]


class TestGraphAssets:
    @pytest.mark.parametrize(
        "nodes, edges, edge_aggregate_col, edge_render_type, result",
        [
            (nodes[0], edges[0], "color", "direct", results[0]),
            (nodes[1], edges[1], "color", "direct", results[1]),
        ],
    )
    def test_calc_connected_edges(
        self, nodes, edges, edge_aggregate_col, edge_render_type, result
    ):
        res = graph_assets.calc_connected_edges(
            nodes,
            edges,
            "x",
            "y",
            "vertex",
            "source",
            "target",
            edge_aggregate_col=edge_aggregate_col,
            edge_render_type=edge_render_type,
            node_x_dtype=cp.float32,
            node_y_dtype=cp.float32,
        ).reset_index(drop=True)

        res = (
            res.compute().reset_index(drop=True)
            if isinstance(res, dask_cudf.DataFrame)
            else res
        )
        result = (
            result.compute()
            if isinstance(result, dask_cudf.DataFrame)
            else result
        )

        assert res.to_pandas().equals(result.to_pandas())
