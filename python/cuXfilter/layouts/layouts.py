from panel import GridSpec
from panel import extension
from panel import Column

import panel as pn

from .layout_templates import *

class Layout0:

    def generate_dashboard(self, title, charts):
        """
        layout 0
        [1]
        """

        tmpl = pn.Template(layout_0)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 1600
                chart.height = int(round(90*1.0))*10
                tmpl.add_panel('chart1', chart.view())
            else:
                break

        return tmpl

class Layout1:

    def generate_dashboard(self, title, charts):
        """
        layout 1
        [1]
        [2]
        """

        tmpl = pn.Template(layout_1)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 1600
                chart.height = int(round(90*0.66))*10
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 1600
                chart.height = int(round(90*0.33))*10
                tmpl.add_panel('chart2', chart.view())
            else:
                break
        
        n = 2 - num_of_charts_added

        for i in range(n):
            chart = 2-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl


class Layout2:
    def generate_dashboard(self, title, charts):
        """
        layout 2

        [1 2]
        """

        tmpl = pn.Template(layout_2)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 900
                chart.height = 900
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 900
                chart.height = 900
                tmpl.add_panel('chart2', chart.view())
            else:
                break
        
        n = 2 - num_of_charts_added

        for i in range(n):
            chart = 2-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl

class Layout3:
    def generate_dashboard(self, title, charts):
        """
        layout 3
        [1   2]
        [1   3]
        """

        tmpl = pn.Template(layout_3)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 900
                chart.height = 900
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 900
                chart.height = 450
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 900
                chart.height = 450
                tmpl.add_panel('chart3', chart.view())
            else:
                break
        
        n = 3 - num_of_charts_added

        for i in range(n):
            chart = 3-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl


class Layout4:
    def generate_dashboard(self, title, charts):
        """
        layout 4
        [1 2 3]
        """

        tmpl = pn.Template(layout_4)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600*0.33)
                chart.height = int(1600*0.33)
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600*0.33)
                chart.height = int(1600*0.33)
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600*0.33)
                chart.height = int(1600*0.33)
                tmpl.add_panel('chart3', chart.view())
            else:
                break
        
        n = 3 - num_of_charts_added

        for i in range(n):
            chart = 3-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl

class Layout5:
    def generate_dashboard(self, title, charts):
        """
        layout 5
        [  1  ]
        [2   3]
        """

        tmpl = pn.Template(layout_5)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 1600
                chart.height = 600
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 800
                chart.height = 300
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 800
                chart.height = 300
                tmpl.add_panel('chart3', chart.view())
            else:
                break
        
        n = 3 - num_of_charts_added

        for i in range(n):
            chart = 3-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl


class Layout6:
    def generate_dashboard(self, title, charts):
        """
        layout 6

        [1  2]
        [3  4]
        """

        tmpl = pn.Template(layout_6)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 800
                chart.height = 450
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 800
                chart.height = 450
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 800
                chart.height = 450
                tmpl.add_panel('chart3', chart.view())
            elif num_of_charts_added == 4:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 800
                chart.height = 450
                tmpl.add_panel('chart4', chart.view())
            else:
                break
        
        n = 4 - num_of_charts_added

        for i in range(n):
            chart = 4-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl


class Layout7:
    def generate_dashboard(self, title, charts):
        """
        layout 7

        [   1   ]
        [2  3  4]
        """

        tmpl = pn.Template(layout_7)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 1600
                chart.height = 600
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart3', chart.view())
            elif num_of_charts_added == 4:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart4', chart.view())
            else:
                break
        
        n = 4 - num_of_charts_added

        for i in range(n):
            chart = 4-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl


class Layout8:
    def generate_dashboard(self, title, charts):
        """
        layout 8

        [     1     ]
        [2  3   4  5]
        """

        tmpl = pn.Template(layout_8)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 1600
                chart.height = 600
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart3', chart.view())
            elif num_of_charts_added == 4:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart4', chart.view())
            elif num_of_charts_added == 5:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart5', chart.view())
            else:
                break
        
        n = 5 - num_of_charts_added

        for i in range(n):
            chart = 5-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl


class Layout9:
    def generate_dashboard(self, title, charts):
        """
        layout 9

        [1  1  2]
        [1  1  3]
        [4  5  6]
        """

        tmpl = pn.Template(layout_9)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = 1200
                chart.height = 600
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart3', chart.view())
            elif num_of_charts_added == 4:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart4', chart.view())
            elif num_of_charts_added == 5:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart5', chart.view())
            elif num_of_charts_added == 6:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart6', chart.view())
            else:
                break
        
        n = 6 - num_of_charts_added

        for i in range(n):
            chart = 6-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl

class Layout10:
    def generate_dashboard(self, title, charts):
        """
        layout 10

        [1  2  3]
        [4  5  6]
        """

        tmpl = pn.Template(layout_10)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 450
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 450
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 450
                tmpl.add_panel('chart3', chart.view())
            elif num_of_charts_added == 4:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 450
                tmpl.add_panel('chart4', chart.view())
            elif num_of_charts_added == 5:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 450
                tmpl.add_panel('chart5', chart.view())
            elif num_of_charts_added == 6:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 450
                tmpl.add_panel('chart6', chart.view())
            else:
                break
        
        n = 6 - num_of_charts_added

        for i in range(n):
            chart = 6-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl


class Layout11:
    def generate_dashboard(self, title, charts):
        """
        layout 11

        [  1      2  ]
        [3   4  5   6]
        """

        tmpl = pn.Template(layout_11)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/2)
                chart.height = 600
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/2)
                chart.height = 600
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart3', chart.view())
            elif num_of_charts_added == 4:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart4', chart.view())
            elif num_of_charts_added == 5:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart5', chart.view())
            elif num_of_charts_added == 6:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/4)
                chart.height = 300
                tmpl.add_panel('chart6', chart.view())
            else:
                break
        
        n = 6 - num_of_charts_added

        for i in range(n):
            chart = 6-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl

class Layout12:
    def generate_dashboard(self, title, charts):
        """
        layout 12

        [1  2  3]
        [4  5  6]
        [7  8  9]
        """

        tmpl = pn.Template(layout_12)
        
        tmpl.add_panel('title', '<div class="nav-title"> '+str(title)+'</div>')

        num_of_charts_added = 0

        for chart in charts.values():
            if 'widget' in chart.chart_type or chart.chart_type == 'datasize_indicator':
                continue
            num_of_charts_added +=1
            if num_of_charts_added == 1:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart1', chart.view())
            elif num_of_charts_added == 2:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart2', chart.view())
            elif num_of_charts_added == 3:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart3', chart.view())
            elif num_of_charts_added == 4:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart4', chart.view())
            elif num_of_charts_added == 5:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart5', chart.view())
            elif num_of_charts_added == 6:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart6', chart.view())
            elif num_of_charts_added == 7:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart7', chart.view())
            elif num_of_charts_added == 8:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart8', chart.view())
            elif num_of_charts_added == 9:
                chart.chart.sizing_mode = 'scale_both'
                chart.width = int(1600/3)
                chart.height = 300
                tmpl.add_panel('chart9', chart.view())
            else:
                break
        
        n = 9 - num_of_charts_added

        for i in range(n):
            chart = 9-i
            tmpl.add_panel('chart'+str(chart),'')

        return tmpl