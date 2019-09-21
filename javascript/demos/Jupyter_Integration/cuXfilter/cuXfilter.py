from pkg_resources import resource_string
import json
from IPython.display import display,Javascript, HTML
from html import escape
import time

class dimension():
    def __init__(self, dataset, chart_data, dimension_name,server_ip, cuXfilter_port, width):
        self.name = dimension_name
        self.display = display
        self.js = Javascript
        self.width = width
        self.chart_list = chart_data
        self.dataset = dataset
        self.server_ip = server_ip
        self.cuXfilter_port = cuXfilter_port

    def get_html(self):
       """Render cuXfilter dimension in an iframe"""
       cuXfilter_html = resource_string(__name__, './cuXfilter.html').decode('utf-8')

       return HTML("""
           <iframe name="{}" class="{}" width="{}" srcdoc="{}"
           frameborder="0"></iframe>
       """.format(self.name,self.name, self.width, escape(cuXfilter_html, quote=True)))

    def update(self, command_type):
        """Send data and config to iframe"""
        cuXfilter_data = json.dumps({"type":command_type, "dataset":self.dataset, "chart_list": self.chart_list, "server_ip": self.server_ip, "cuXfilter_port": self.cuXfilter_port})
        cmd = """window.frames["{}"].postMessage({}, "*");""".format(self.name, cuXfilter_data)
        self.display(self.js(cmd))


    def render(self):
        self.update('init')
        time.sleep(0.5)
        cmd = """$('.{}').height( $('.{}').contents().outerHeight()*1.05);""".format(self.name,self.name)
        self.display(self.js(cmd))


    def _end_connection(self):
        self.update('end_connection')

    def add_chart(self,data):
        self.chart_list = data
        self.update('add_dimension')

    def remove_chart(self,data):
        self.chart_list = data
        self.update('remove_dimension')


class cuXfilter():
    def __init__(self, dataset, server_ip, cuXfilter_port='', width='100%', name='cuXfilter1'):
        self.name = name
        self.dataset = dataset
        self.dimensions = {}
        self.width = width
        self.server_ip = server_ip
        self.cuXfilter_port = cuXfilter_port

    def dimension(self, data, name="unnamed"):
        if name is not "unnamed":
            dimension_name = name
        else:
            dimension_name = list(data.keys())[0]
        self.dimensions[dimension_name] = dimension(self.dataset, data, dimension_name, self.server_ip, self.cuXfilter_port, width= self.width)
        return self.dimensions[dimension_name].get_html()#.render()


    def end_connection(self):
        self.dimensions[list(self.dimensions.keys())[0]]._end_connection()

    def render(self):
        for i in self.dimensions:
            self.dimensions[i].render()
