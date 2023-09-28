from .core_chart import BaseChart
from .core_widget import BaseWidget
from .core_view_dataframe import ViewDataFrame


def view_dataframe(
    columns=None,
    drop_duplicates=False,
    force_computation=False,
):
    """

    Parameters
    ----------

    columns: list, default None
        display subset of columns, and all columns if None

    drop_duplicates: bool, default False
        display only unique rows if True

    force_computation: bool, default False
        - force_computation=False returns df.head(1000)
        - force_computation=True returns entire df, but it can be
        computationally intensive

    Returns
    -------
    A view dataframe object.
    Type cuxfilter.charts.core_view_dataframe.ViewDataFrame
    """
    plot = ViewDataFrame(columns, drop_duplicates, force_computation)
    plot.chart_type = "view_dataframe"
    return plot
