import re

import panel as pn

from .layout_templates import (
    layout_0,
    layout_1,
    layout_2,
    layout_3,
    layout_4,
    layout_5,
    layout_6,
    layout_7,
    layout_8,
    layout_9,
    layout_10,
    layout_11,
    layout_12,
)


def is_widget(obj):
    return "widget" in obj.chart_type or obj.chart_type == "datasize_indicator"


class _LayoutBase:
    _layout: str

    _num_charts_pat = re.compile("roots.chart")

    def generate_dashboard(self, title, charts, theme):
        tmpl = pn.Template(theme.layout_head + self._layout)
        tmpl.add_panel(
            "title", '<div class="nav-title"> ' + str(title) + "</div>"
        )

        widgets = [x for x in charts.values() if is_widget(x)]
        plots = [x for x in charts.values() if not is_widget(x)]
        self._apply_themes(charts, theme)
        widgetbox = self._process_widgets(widgets)
        self._process_plots(plots, tmpl)
        self._pad_missing_plots(len(plots), tmpl)
        tmpl.add_panel("widgets", widgetbox)
        return tmpl

    @property
    def total_charts(self):
        # Would be nice if the templates and this value could be derived from
        # some common declarative source description
        return len(self._num_charts_pat.findall(self._layout))

    def _apply_themes(self, charts, theme):
        for chart in charts.values():
            if hasattr(chart, "apply_theme"):
                chart.apply_theme(theme.chart_properties)

    def _process_widgets(self, widgets_list):
        widgets_ = pn.Column()
        for obj in widgets_list:
            obj.chart.width = 280
            obj.chart.sizing_mode = "scale_both"
            widgets_.append(obj.view())
        return widgets_

    def _pad_missing_plots(self, num_charts_added, tmpl):
        N = self.total_charts - num_charts_added

        for i in range(N):
            tmpl.add_panel(f"chart{self.total_charts - i}", "")

    def _process_plots(self, plots, tmpl):
        raise NotImplementedError()


class Layout0(_LayoutBase):
    _layout = layout_0

    def _process_plots(self, plots, tmpl):
        """
        layout 0
        [1]
        """

        for i, chart in enumerate(plots, 1):
            chart.width = 1600
            chart.height = 900
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout1(_LayoutBase):
    _layout = layout_1

    def _process_plots(self, plots, tmpl):
        """
        layout 1
        [1]
        [2]
        """

        for i, chart in enumerate(plots, 1):
            if i == 1:
                chart.width = 1600
                chart.height = 600
            elif i == 2:
                chart.width = 1600
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout2(_LayoutBase):
    _layout = layout_2

    def _process_plots(self, plots, tmpl):
        """
        layout 2

        [1 2]
        """

        for i, chart in enumerate(plots, 1):
            chart.width = 900
            chart.height = 900
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout3(_LayoutBase):
    _layout = layout_3

    def _process_plots(self, plots, tmpl):
        """
        layout 3
        [1   2]
        [1   3]
        """

        for i, chart in enumerate(plots, 1):
            if i == 1:
                chart.width = 900
                chart.height = 900
            elif i in [2, 3]:
                chart.width = 800
                chart.height = 450
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout4(_LayoutBase):
    _layout = layout_4

    def _process_plots(self, plots, tmpl):
        """
        layout 4
        [1 2 3]
        """

        for i, chart in enumerate(plots, 1):
            chart.width = int(1600 / 3)
            chart.height = int(1600 / 3)
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout5(_LayoutBase):
    _layout = layout_5

    def _process_plots(self, plots, tmpl):
        """
        layout 5
        [  1  ]
        [2   3]
        """

        for i, chart in enumerate(plots, 1):
            if i == 1:
                chart.width = 1600
                chart.height = 600
            elif i in [2, 3]:
                chart.width = 800
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout6(_LayoutBase):
    _layout = layout_6

    def _process_plots(self, plots, tmpl):
        """
        layout 6

        [1  2]
        [3  4]
        """

        for i, chart in enumerate(plots, 1):
            chart.width = 800
            chart.height = 450
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout7(_LayoutBase):
    _layout = layout_7

    def _process_plots(self, plots, tmpl):
        """
        layout 7

        [   1   ]
        [2  3  4]
        """

        for i, chart in enumerate(plots, 1):
            if i == 1:
                chart.width = 1600
                chart.height = 600
            elif i in [2, 3, 4]:
                chart.width = int(1600 / 3)
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout8(_LayoutBase):
    _layout = layout_8

    def _process_plots(self, plots, tmpl):
        """
        layout 8

        [     1     ]
        [2  3   4  5]
        """

        for i, chart in enumerate(plots, 1):
            if i == 1:
                chart.width = 1600
                chart.height = 600
            elif i in [2, 3, 4, 5]:
                chart.width = int(1600 / 4)
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout9(_LayoutBase):
    _layout = layout_9

    def _process_plots(self, plots, tmpl):
        """
        layout 9

        [1  1  2]
        [1  1  3]
        [4  5  6]
        """

        for i, chart in enumerate(plots, 1):
            if i == 1:
                chart.width = 1200
                chart.height = 600
            elif i in [2, 3]:
                chart.width = int(1600 / 4)
                chart.height = 300
            elif i in [4, 5, 6]:
                chart.width = int(1600 / 3)
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout10(_LayoutBase):
    _layout = layout_10

    def _process_plots(self, plots, tmpl):
        """
        layout 10

        [1  2  3]
        [4  5  6]
        """

        for i, chart in enumerate(plots, 1):
            chart.width = int(1600 / 3)
            chart.height = 450
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout11(_LayoutBase):
    _layout = layout_11

    def _process_plots(self, plots, tmpl):
        """
        layout 11

        [  1      2  ]
        [3   4  5   6]
        """

        for i, chart in enumerate(plots, 1):
            if i in [1, 2]:
                chart.width = int(1600 / 2)
                chart.height = 600
            elif i in [3, 4, 5, 6]:
                chart.width = int(1600 / 4)
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())


class Layout12(_LayoutBase):
    _layout = layout_12

    def _process_plots(self, plots, tmpl):
        """
        layout 12

        [1  2  3]
        [4  5  6]
        [7  8  9]
        """

        for i, chart in enumerate(plots, 1):
            chart.width = int(1600 / 3)
            chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel(f"chart{i}", chart.view())
