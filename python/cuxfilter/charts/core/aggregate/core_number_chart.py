import numpy as np

from ..core_chart import BaseChart
from ....layouts import chart_view
from ....assets import cudf_utils


class BaseNumberChart(BaseChart):
    stride = 1
    # widget is a chart type that can be rendered in a sidebar or main layout
    is_widget = True

    @property
    def use_data_tiles(self):
        return self.expression is None

    @property
    def is_datasize_indicator(self):
        return not (self.x or self.expression)

    @property
    def name(self):
        value = (self.x or self.expression) or ""
        return f"{value}_{self.chart_type}_{self.title}"

    def __init__(
        self,
        x=None,
        expression=None,
        aggregate_fn="count",
        title="",
        widget=True,
        format="{value}",
        colors=[],
        font_size="18pt",
        **library_specific_params,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            **library_specific_params
        -------------------------------------------

        Ouput:

        """
        self.x = x
        self.expression = expression
        self.title = title if title else (x or expression)
        self.aggregate_fn = aggregate_fn
        self.format = format
        self.colors = colors
        self.font_size = font_size
        self.library_specific_params = library_specific_params
        self.chart_type = (
            "number_chart" if not widget else "number_chart_widget"
        )

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        """
        if self.is_datasize_indicator:
            # datasize indicator
            self.min_value = 0
            self.max_value = len(dashboard_cls._cuxfilter_df.data)
        elif self.x:
            self.expression = f"data.{self.x}"
        elif self.expression:
            for i in dashboard_cls._cuxfilter_df.data.columns:
                self.expression = self.expression.replace(i, f"data.{i}")

        self.calculate_source(dashboard_cls._cuxfilter_df.data)
        self.generate_chart()

    def view(self):
        return chart_view(self.chart, title=self.title)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        pass

    def reload_chart(self, data, patch_update=True):
        """
        reload chart
        """
        self.calculate_source(data, patch_update=patch_update)

    def _compute_source(self, query, local_dict, indices):
        """
        Compute source dataframe based on the values query and indices.
        If both are not provided, return the original dataframe.
        """
        return cudf_utils.query_df(self.source, query, local_dict, indices)

    def query_chart_by_range(
        self,
        active_chart,
        query_tuple,
        datatile,
        query="",
        local_dict={},
        indices=None,
    ):
        """
        Description:
        Reload the current chart by querying its source with current state
        & new queried_tuple for the active chart
        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: datatile of active chart for current
                        chart[type:pandas df]
            4. query: query string representing the current filtered state of
                    the dashboard
            5. local_dict: dictionary containing the variable:value mapping
                    local to the query_string.
                    Passed as a parameter to cudf.query() api
            6. indices: cudf.Series representing the current filtered state
                    of the dashboard, apart from the query_string,
                    since the lasso_select callback results in a boolean mask
        -------------------------------------------

        Ouput:
        """
        if self.use_data_tiles:
            # datatile based computation
            min_val, max_val = query_tuple
            datatile_index_min = int(
                round((min_val - active_chart.min_value) / active_chart.stride)
            )
            datatile_index_max = int(
                round((max_val - active_chart.min_value) / active_chart.stride)
            )

            if datatile_index_min == 0:
                if self.aggregate_fn in ["count", "sum"]:
                    datatile_result = datatile.loc[datatile_index_max].values
                else:
                    datatile_result = getattr(
                        datatile.loc[:datatile_index_max],
                        self.aggregate_fn,
                    )(axis=0, skipna=True)[0]
            else:
                if self.aggregate_fn in ["count", "sum"]:
                    datatile_index_min -= 1
                    datatile_max_values = datatile.loc[
                        datatile_index_max
                    ].values
                    datatile_min_values = datatile.loc[
                        datatile_index_min
                    ].values
                    datatile_result = datatile_max_values - datatile_min_values
                else:
                    datatile_result = getattr(
                        datatile.loc[datatile_index_min:datatile_index_max],
                        self.aggregate_fn,
                    )(axis=0, skipna=True)[0]

            self.reset_chart(datatile_result)
        else:
            # cudf.query based computation
            min_val, max_val = query_tuple
            final_query = "@min_val<=" + active_chart.x + "<=@max_val"
            local_dict.update({"min_val": min_val, "max_val": max_val})
            if len(query) > 0:
                final_query += " and " + query
            self.reload_chart(
                self._compute_source(final_query, local_dict, indices), True
            )

    def query_chart_by_indices_for_count(
        self,
        active_chart,
        old_indices,
        new_indices,
        datatile,
        calc_new,
        remove_old,
    ):
        """
        Description: query_chart by indices when
        self.aggregate_fn is "count" or "sum"

        -------------------------------------------
        Input:
        -------------------------------------------

        Ouput:
        """
        if len(new_indices) == 0 or new_indices == [""]:
            datatile_result = datatile.cumsum().values[-1]
            return datatile_result

        if len(old_indices) == 0 or old_indices == [""]:
            datatile_result = 0
        else:
            datatile_result = self.get_source_y_axis()

        for index in calc_new:
            index = int(
                round((index - active_chart.min_value) / active_chart.stride)
            )
            datatile_result += datatile.loc[int(index)][0]

        for index in remove_old:
            index = int(
                round((index - active_chart.min_value) / active_chart.stride)
            )
            datatile_result -= datatile.loc[int(index)][0]

        return datatile_result

    def query_chart_by_indices_for_agg(
        self,
        active_chart,
        new_indices,
        datatile,
    ):
        """
        Description: query_chart by indices when
        self.aggregate_fn is in ["mean", "min", "max", "std"]

        -------------------------------------------
        Input:
        -------------------------------------------

        Ouput:
        """
        if len(new_indices) == 0 or new_indices == [""]:
            # get min or max from datatile df, skipping column 0(always 0)
            datatile_result = getattr(datatile, self.aggregate_fn)(
                axis=0, skipna=True
            )[0]
        else:
            new_indices = np.array(new_indices)
            new_indices = np.round(
                (new_indices - active_chart.min_value) / active_chart.stride
            ).astype(int)
            datatile_result = getattr(
                datatile.loc[new_indices], self.aggregate_fn
            )(axis=0, skipna=True)[0]

        return datatile_result

    def query_chart_by_indices(
        self,
        active_chart: BaseChart,
        old_indices,
        new_indices,
        datatile=None,
        query="",
        local_dict={},
        indices=None,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. old_indices: list of indices selected in previous callback
            3. new_indices: list of indices selected in currently
            4. datatile: datatile of active chart for current chart
            5. query: query string representing the current filtered state of
                    the dashboard
            6. local_dict: dictionary containing the variable:value mapping
                    local to the query_string.
                    Passed as a parameter to cudf.query() api
            7. indices: cudf.Series representing the current filtered state
                    of the dashboard, apart from the query_string,
                    since the lasso_select callback results in a boolean mask
        -------------------------------------------

        Ouput:
        """
        if self.use_data_tiles:
            # datatile based computation
            calc_new = list(set(new_indices) - set(old_indices))
            remove_old = list(set(old_indices) - set(new_indices))

            if "" in calc_new:
                calc_new.remove("")
            if "" in remove_old:
                remove_old.remove("")

            if self.aggregate_fn in ["count", "sum"]:
                datatile_result = self.query_chart_by_indices_for_count(
                    active_chart,
                    old_indices,
                    new_indices,
                    datatile,
                    calc_new,
                    remove_old,
                )
            else:
                datatile_result = self.query_chart_by_indices_for_agg(
                    active_chart,
                    new_indices,
                    datatile,
                    calc_new,
                    remove_old,
                )
            self.reset_chart(datatile_result)
        else:
            # cudf.query based computation
            if "" in new_indices:
                new_indices.remove("")
            if len(new_indices) == 0:
                # case: all selected indices were reset
                # reset the chart
                final_query = query
            elif len(new_indices) == 1:
                final_query = f"{active_chart.x}=={str(float(new_indices[0]))}"
                if len(query) > 0:
                    final_query += f" and {query}"
            else:
                new_indices_str = ",".join(map(str, new_indices))
                final_query = f"{active_chart.x} in ({new_indices_str})"
                if len(query) > 0:
                    final_query += f" and {query}"

            self.reload_chart(
                self._compute_source(final_query, local_dict, indices),
                True,
            )
