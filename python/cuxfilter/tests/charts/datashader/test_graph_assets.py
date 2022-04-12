import pytest
import cudf
import cupy as cp
from cuxfilter.charts.datashader.custom_extensions import graph_assets

pytest


class TestGraphAssets:
    nodes = cudf.DataFrame(
        {"vertex": [0, 1, 2, 3], "x": [0, 1, 1, 2], "y": [0, 1, 2, 0]}
    )
    edges = cudf.DataFrame(
        {"source": [1, 1], "target": [0, 1], "color": [10, 11]}
    )

    @pytest.mark.parametrize(
        "edge_aggregate_col, edge_render_type, result",
        [
            (
                "color",
                "direct",
                cudf.DataFrame(
                    {
                        "x": cudf.Series(
                            [1.0, 0.0, cp.NAN, 1.0, 1.0, cp.NAN],
                            dtype=nodes.x.dtype,
                        ),
                        "y": cudf.Series(
                            [1.0, 0.0, cp.NAN, 1.0, 1.0, cp.NAN],
                            dtype=nodes.y.dtype,
                        ),
                        "color": cudf.Series(
                            [10.0, 10.0, cp.NAN, 11.0, 11.0, cp.NAN],
                            dtype=edges.color.dtype,
                        ),
                    }
                ),
            )
        ],
    )
    def test_calc_connected_edges(
        self, edge_aggregate_col, edge_render_type, result
    ):
        res = graph_assets.calc_connected_edges(
            self.nodes,
            self.edges,
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
        assert res.to_pandas().equals(result.to_pandas())
