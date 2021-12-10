import re
import numpy as np
import panel as pn
from panel.layout.gridstack import GridStack

from .custom_react_template import ReactTemplate

css = """
.center-header {
    text-align: center
}
"""

pn.config.raw_css += [css]


def compute_position(arr, i, pos, offset, cols=12, rows=6):
    x, y = (
        np.array(
            [
                np.where(arr == i + 1)[0][pos] + offset,
                np.where(arr == i + 1)[1][pos] + offset,
            ]
        )
        / np.array(arr.shape)
        * (rows, cols)
    )
    return int(x), int(y)


class _LayoutBase:
    _layout: str
    _layout_array: list
    _num_charts_pat = re.compile("roots.chart")

    def generate_dashboard(
        self,
        title,
        charts,
        sidebar,
        theme,
        layout_array=None,
        render_location="notebook",  # ["notebook", "web-app"]
        sidebar_width=280,
    ):
        pn.config.sizing_mode = "stretch_both"
        self._layout_array = layout_array
        self._render_location = render_location
        self.sidebar_width = sidebar_width
        widgets = [x for x in sidebar.values() if x.is_widget]
        plots = [x for x in charts.values()]

        if self._render_location == "notebook":
            self.cols, self.rows = 11, 6
            tmpl = GridStack(
                allow_drag=False,
                allow_resize=False,
                sizing_mode="stretch_both",
            )
            self._apply_themes(charts, theme)
            self._process_plots(plots, tmpl)
            tmpl = self._process_widgets_notebook(widgets, tmpl)
        else:
            self.cols, self.rows = 12, 6
            tmpl = ReactTemplate(title=title, theme=theme, compact="both")
            self._apply_themes(charts, theme)
            self._process_widgets(widgets, tmpl)
            self._process_plots(plots, tmpl)

        return tmpl

    def _apply_themes(self, charts, theme):
        for chart in charts.values():
            if hasattr(chart, "apply_theme"):
                chart.apply_theme(theme)

    def _process_widgets(self, widgets_list, tmpl):
        for obj in widgets_list:
            obj.chart.width = self.sidebar_width
            obj.chart.sizing_mode = "scale_width"
            tmpl.sidebar.append(obj.view())

    def _process_widgets_notebook(self, widgets_list, tmpl):
        x = pn.Column(width=self.sidebar_width)
        for obj in widgets_list:
            obj.chart.sizing_mode = "stretch_both"
            temp_chart = obj.view()
            temp_chart.collapsible = False
            temp_chart.header_css_classes.append("center-header")
            x.append(temp_chart)
        return pn.Row(x, tmpl)

    def _assign_template_main(self, tmpl, x, y, plot):
        if self._render_location == "notebook":
            tmpl[x[0] : y[0], x[1] : y[1]] = plot
        else:
            tmpl.main[x[0] : y[0], x[1] : y[1]] = plot

    def _process_grid_matrix(self, plots, tmpl):
        arr = np.array(self._layout_array)
        if len(arr.shape) == 1:
            arr = np.array([arr])
        for i in range(arr.max()):
            if i < len(plots):
                self._assign_template_main(
                    tmpl,
                    compute_position(arr, i, 0, 0, self.cols, self.rows),
                    compute_position(arr, i, -1, 1, self.cols, self.rows),
                    plots[i].view(),
                )

    def _process_plots(self, plots, tmpl):
        raise NotImplementedError()


class Layout0(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 0
        [1]
        """
        if not self._layout_array:
            self._layout_array = [1]
        self._process_grid_matrix(plots, tmpl)


class Layout1(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 1

        [1]
        [1]
        [2]
        """
        if not self._layout_array:
            self._layout_array = [[1], [1], [2]]
        self._process_grid_matrix(plots, tmpl)


class Layout2(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 2

        [1 2]
        """
        if not self._layout_array:
            self._layout_array = [1, 2]
        self._process_grid_matrix(plots, tmpl)


class Layout3(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 3

        [1   2]
        [1   3]
        """
        if not self._layout_array:
            self._layout_array = [[1, 2], [1, 3]]
        self._process_grid_matrix(plots, tmpl)


class Layout4(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 4

        [1 2 3]
        """
        if not self._layout_array:
            self._layout_array = [1, 2, 3]
        self._process_grid_matrix(plots, tmpl)


class Layout5(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 5

        [1   1]
        [2   3]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1], [2, 3]]
        self._process_grid_matrix(plots, tmpl)


class Layout6(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 6

        [1  2]
        [3  4]
        """
        if not self._layout_array:
            self._layout_array = [[1, 2], [3, 4]]
        self._process_grid_matrix(plots, tmpl)


class Layout7(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 7

        [1  1  1]
        [2  3  4]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1, 1], [2, 3, 4]]
        self._process_grid_matrix(plots, tmpl)


class Layout8(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 8

        [     1     ]
        [2  3   4  5]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1, 1, 1], [2, 3, 4, 5]]
        self._process_grid_matrix(plots, tmpl)


class Layout9(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 9

        [1  1  2]
        [1  1  3]
        [4  5  6]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1, 2], [1, 1, 3], [4, 5, 6]]
        self._process_grid_matrix(plots, tmpl)


class Layout10(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 10

        [1  2  3]
        [4  5  6]
        """
        if not self._layout_array:
            self._layout_array = [[1, 2, 3], [4, 5, 6]]
        self._process_grid_matrix(plots, tmpl)


class Layout11(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 11

        [1   1   2   2]
        [3   4   5   6]
        """
        if not self._layout_array:
            self._layout_array = [[1, 1, 2, 2], [3, 4, 5, 6]]
        self._process_grid_matrix(plots, tmpl)


class Layout12(_LayoutBase):
    def _process_plots(self, plots, tmpl):
        """
        layout 12

        [1  2  3]
        [4  5  6]
        [7  8  9]
        """
        if not self._layout_array:
            self._layout_array = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self._process_grid_matrix(plots, tmpl)
