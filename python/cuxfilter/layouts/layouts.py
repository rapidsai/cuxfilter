import re
import numpy as np
import panel as pn

from panel.template import ReactTemplate, FastGridTemplate
from cuxfilter.themes import dark

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
        width=1200,
        height=800,
    ):
        self._layout_array = layout_array
        self._render_location = render_location
        self.sidebar_width = sidebar_width
        self.width = width
        self.height = height
        widgets = [x for x in sidebar.values() if x.is_widget]
        plots = [x for x in charts.values()]
        self.cols, self.rows = 12, 5

        for chart in charts.values():
            chart.renderer_mode = render_location

        if self._render_location == "notebook":
            tmpl = pn.GridSpec(width=self.width, height=self.height)
            self._apply_themes(charts, theme)
            self._apply_themes(sidebar, theme)
            self._process_plots(plots, tmpl)
            tmpl = self._process_widgets_notebook(widgets, tmpl)
        else:
            tmpl = FastGridTemplate(
                title=title,
                sidebar_width=self.sidebar_width,
                row_height=int(self.height / self.rows),
            )
            self._apply_themes(charts, theme)
            self._apply_themes(sidebar, theme)
            self._process_widgets(widgets, tmpl)
            self._process_plots(plots, tmpl)

        return tmpl

    def _apply_themes(self, charts, theme):
        for chart in charts.values():
            if hasattr(chart, "apply_theme"):
                chart.apply_theme(theme)

    def _process_widgets(self, widgets_list, tmpl):
        widget_box = pn.WidgetBox(
            sizing_mode="scale_width",
            css_classes=["panel-widget-box", "custom-widget-box"],
        )
        for obj in widgets_list:
            obj.chart.width = self.sidebar_width
            obj.chart.sizing_mode = "scale_width"
            if obj.chart_type == "datasize_indicator":
                tmpl.sidebar.append(obj.get_dashboard_view())
            else:
                widget_box.append(obj.get_dashboard_view())
        tmpl.sidebar.append(pn.VSpacer())
        tmpl.sidebar.append(widget_box)

    def _process_widgets_notebook(self, widgets_list, tmpl):
        tmpl_with_widgets = pn.GridSpec()
        tmpl_with_widgets[:, 2 : self.cols] = tmpl
        widget_box = pn.WidgetBox(
            sizing_mode="stretch_width",
        )

        for obj in widgets_list:
            if obj.chart_type == "datasize_indicator":
                tmpl_with_widgets[0:1, 0:2] = obj.get_dashboard_view()
            else:
                obj.chart.sizing_mode = "scale_width"
                widget_box.append(obj.get_dashboard_view())

        tmpl_with_widgets[1:, 0:2] = widget_box
        return tmpl_with_widgets

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
                    plots[i].get_dashboard_view(),
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
