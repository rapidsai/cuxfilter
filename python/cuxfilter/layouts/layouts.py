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

        widgets = pn.Column()

        self._apply_themes(charts, theme)
        self._process_widgets(charts, widgets)

        num_charts_added = self._process_charts(charts, tmpl)

        self._pad_missing_charts(num_charts_added, tmpl)

        tmpl.add_panel("widgets", widgets)
        return tmpl

    @property
    def total_charts(self):
        return len(self._num_charts_pat.findall(self.layout))

    def _apply_themes(self, charts, theme):
        for chart in charts.values():
            if hasattr(chart, "apply_theme"):
                chart.apply_theme(theme.chart_properties)

    def _process_widgets(self, charts, widgets):
        for chart in (x for x in charts.values() if is_widget(x)):
            chart.chart.width = 280
            widgets.append(chart.view())

    def _pad_missing_charts(self, num_charts_added, tmpl):
        N = self.total_charts - num_charts_added

        for i in range(N, num_charts_added, -1):
            tmpl.add_panel(f"chart{i}", "")

    def _process_charts(self, charts, tmpl):
        raise NotImplementedError()


class Layout0(_LayoutBase):
    _layout = layout_0

    def _process_charts(self, charts, tmpl):
        """
        layout 0
        [1]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = 1600
                chart.height = int(round(90 * 1.0)) * 10
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout1(_LayoutBase):
    _layout = layout_1

    def _process_charts(self, charts, tmpl):
        """
        layout 1
        [1]
        [2]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = 1600
                chart.height = int(round(90 * 0.66)) * 10
            elif i == 2:
                chart.width = 1600
                chart.height = int(round(90 * 0.33)) * 10
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout2(_LayoutBase):
    _layout = layout_2

    def _process_charts(self, charts, tmpl):
        """
        layout 2

        [1 2]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = 900
                chart.height = 900
            elif i == 2:
                chart.width = 900
                chart.height = 900
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout3(_LayoutBase):
    _layout = layout_3

    def _process_charts(self, charts, tmpl):
        """
        layout 3
        [1   2]
        [1   3]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = 900
                chart.height = 900
            elif i == 2:
                chart.width = 800
                chart.height = 450
            elif i == 3:
                chart.width = 800
                chart.height = 450
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout4(_LayoutBase):
    _layout = layout_4

    def _process_charts(self, charts, tmpl):
        """
        layout 4
        [1 2 3]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = int(1600 * 0.33)
                chart.height = int(1600 * 0.33)
            elif i == 2:
                chart.width = int(1600 * 0.33)
                chart.height = int(1600 * 0.33)
            elif i == 3:
                chart.width = int(1600 * 0.33)
                chart.height = int(1600 * 0.33)
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout5(_LayoutBase):
    _layout = layout_5

    def _process_charts(self, charts, tmpl):
        """
        layout 5
        [  1  ]
        [2   3]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = 1600
                chart.height = 600
            elif i == 2:
                chart.width = 800
                chart.height = 300
            elif i == 3:
                chart.width = 800
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout6(_LayoutBase):
    _layout = layout_6

    def _process_charts(self, charts, tmpl):
        """
        layout 6

        [1  2]
        [3  4]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = 800
                chart.height = 450
            elif i == 2:
                chart.width = 800
                chart.height = 450
            elif i == 3:
                chart.width = 800
                chart.height = 450
            elif i == 4:
                chart.width = 800
                chart.height = 450
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout7(_LayoutBase):
    _layout = layout_7

    def _process_charts(self, charts, tmpl):
        """
        layout 7

        [   1   ]
        [2  3  4]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = 1600
                chart.height = 600
            elif i == 2:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 3:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 4:
                chart.width = int(1600 / 3)
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout8(_LayoutBase):
    _layout = layout_8

    def _process_charts(self, charts, tmpl):
        """
        layout 8

        [     1     ]
        [2  3   4  5]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = 1600
                chart.height = 600
            elif i == 2:
                chart.width = int(1600 / 4)
                chart.height = 300
            elif i == 3:
                chart.width = int(1600 / 4)
                chart.height = 300
            elif i == 4:
                chart.width = int(1600 / 4)
                chart.height = 300
            elif i == 5:
                chart.width = int(1600 / 4)
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout9(_LayoutBase):
    _layout = layout_9

    def _process_charts(self, charts, tmpl):
        """
        layout 9

        [1  1  2]
        [1  1  3]
        [4  5  6]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = 1200
                chart.height = 600
            elif i == 2:
                chart.width = int(1600 / 4)
                chart.height = 300
            elif i == 3:
                chart.width = int(1600 / 4)
                chart.height = 300
            elif i == 4:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 5:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 6:
                chart.width = int(1600 / 3)
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout10(_LayoutBase):
    _layout = layout_10

    def _process_charts(self, charts, tmpl):
        """
        layout 10

        [1  2  3]
        [4  5  6]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = int(1600 / 3)
                chart.height = 450
            elif i == 2:
                chart.width = int(1600 / 3)
                chart.height = 450
            elif i == 3:
                chart.width = int(1600 / 3)
                chart.height = 450
            elif i == 4:
                chart.width = int(1600 / 3)
                chart.height = 450
            elif i == 5:
                chart.width = int(1600 / 3)
                chart.height = 450
            elif i == 6:
                chart.width = int(1600 / 3)
                chart.height = 450
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout11(_LayoutBase):
    _layout = layout_11

    def _process_charts(self, charts, tmpl):
        """
        layout 11

        [  1      2  ]
        [3   4  5   6]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = int(1600 / 2)
                chart.height = 600
            elif i == 2:
                chart.width = int(1600 / 2)
                chart.height = 600
            elif i == 3:
                chart.width = int(1600 / 4)
                chart.height = 300
            elif i == 4:
                chart.width = int(1600 / 4)
                chart.height = 300
            elif i == 5:
                chart.width = int(1600 / 4)
                chart.height = 300
            elif i == 6:
                chart.width = int(1600 / 4)
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)


class Layout12(_LayoutBase):
    _layout = layout_12

    def _process_charts(self, charts, tmpl):
        """
        layout 12

        [1  2  3]
        [4  5  6]
        [7  8  9]
        """

        charts = [x for x in charts.values() if not is_widget(x)]

        for i, chart in enumerate(charts, 1):
            if i == 1:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 2:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 3:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 4:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 5:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 6:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 7:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 8:
                chart.width = int(1600 / 3)
                chart.height = 300
            elif i == 9:
                chart.width = int(1600 / 3)
                chart.height = 300
            chart.chart.sizing_mode = "scale_both"
            tmpl.add_panel("chart{i}", chart.view())

        return len(charts)
