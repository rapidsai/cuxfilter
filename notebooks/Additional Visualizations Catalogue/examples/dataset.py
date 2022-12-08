import cudf
import cupy as cp


# Function to generate random data - Pandas or cuDF dataframe
def generate_random_points(
    nodes=100, clusters=10, cluster_spreadout_factor=20, dtype="cudf"
):
    processed_nodes = round(nodes / clusters)

    radius = cp.sqrt(
        cp.random.uniform(0, 2**cluster_spreadout_factor, clusters)
    )
    centers = cp.random.uniform(0, 2 * cp.pi, clusters)
    centers_x = radius * cp.cos(centers) + 0
    centers_y = radius * cp.sin(centers) + 0

    dfs = []
    for cluster in range(clusters):
        n = min(nodes, processed_nodes)
        circle_radius = min(n, cluster_spreadout_factor - 4)
        radius = cp.sqrt(cp.random.uniform(0, 2**circle_radius, n))
        points = cp.random.uniform(0, 2 * cp.pi, n)

        dfs.append(
            cudf.DataFrame(
                {
                    "x": cudf.Series(
                        radius * cp.cos(points) + centers_x[cluster]
                    ),
                    "y": cudf.Series(
                        radius * cp.sin(points) + centers_y[cluster]
                    ),
                    "cluster": cluster,
                }
            )
        )
        nodes -= processed_nodes
    return (
        (
            cudf.concat(dfs)
            .reset_index(drop=True)
            .reset_index()
            .rename(columns={"index": "vertex"})
        )
        if dtype == "cudf"
        else (
            cudf.concat(dfs)
            .reset_index(drop=True)
            .reset_index()
            .rename(columns={"index": "vertex"})
            .to_pandas(nullable=False)
        )
    )
