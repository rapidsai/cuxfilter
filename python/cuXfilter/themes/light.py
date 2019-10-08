# Layout Head Section style CSS
# NOTE may move to remote CSS file later
from bokeh import palettes

class Theme:
    layout_head = '''
    {% extends base %}

    {% block head %}
    <head>
        {% block inner_head %}
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{% block title %}{{ title | e if title else "Panel App" }}{% endblock %}</title>
        {% block preamble %}{% endblock %}
        {% block resources %}
            {% block css_resources %}
            {{ bokeh_css | indent(8) if bokeh_css }}
            
            <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.1/build/pure-min.css" integrity="sha384-oAOxQR6DkCoMliIh8yFnu25d7Eq/PHS21PClpwjOTeU2jRSq11vu66rf90/cZr47" crossorigin="anonymous">
            <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.1/build/grids-responsive-min.css">        
            
            {% endblock %}
            {% block js_resources %}
            {{ bokeh_js | indent(8) if bokeh_js }}
            {% endblock %}
        {% endblock %}
        {% block postamble %}
            <style>
            
                body {
                    margin:0;
                    padding:0;
                }
                
                nav {
                    display: inline-block;
                    vertical-align: top;
                    width: 18em;
                    height: calc(100vh - 2em);
                    padding: 1em;
                    background-color: #fcfcfc;
                    color: #a0a0a0;
                    border-right: 2px solid #fafafa;
                }

                .nav-title {
                    font-size: 1.5em;
                }

                .nav-container {
                    margin-top: 1em;
                    font-size: 1.04em;
                }
     
                .container {
                    display: inline-block;
                    width: calc(100vw - 23em);
                    padding-left: 0.5em;
                    height: 100vh;
                    color: #a0a0a0;
                    background-color: white;
                }
                
                @media screen and (max-width: 48em) {
                    nav {
                        display: block;
                        width: calc(100vw - 2em);
                        height: auto;
                        border-right: none;
                    }
                    
                    .container {
                        display: block;
                        position: relative;
                        width: calc(100vw - 2em);
                        height: auto;
                        padding-left: 0;
                        margin: 0 auto;
                    }
                }
            </style>   
        {% endblock %}
        {% endblock %}
    </head>
    {% endblock %}
    '''


    
    chart_properties = {
        "data_size_indicator_color": '#4292c6',
        "agg_charts_grids":{
            "xgrid": None,
            "ygrid": "#efefef",
        },
        "geo_charts_grids":{
            "xgrid": None,
            "ygrid": None,
        },

        "chart_color":{
            'color': '#4292c6',
            'color_palette': palettes.Blues[9]
        },
        
        #title
        "title": {
            "text_color": "#a0a0a0",
            "text_font": "helvetica",
            "text_font_style": "bold",
            "text_font_size": "18px"
        },
        #background
        "background_fill_color": "white",
        "border_fill_color": "white",
        "min_border": 40,
        "outline_line_width": 0,
        "outline_line_alpha" : 1,
        "outline_line_color" : "#efefef",

        # x axis title
        "xaxis": {
            "axis_label" : "X Axis",
            "axis_label_text_font_style" : "bold",
            "axis_label_text_color" : "#a0a0a0",
            "axis_label_standoff" : 15,
            "major_label_text_color" : "#262626",
            "axis_line_width" : 1,
            "axis_line_color" : "#000000"
        },

        # y axis title
        "yaxis": {
            "axis_label" : "Y Axis",
            "axis_label_text_font_style" : "bold",
            "axis_label_text_color" : "#a0a0a0",
            "axis_label_standoff" : 15,
            "major_label_text_color" : "#262626",
            "axis_line_width" : 0,
            "axis_line_color" : "#000000"
        },

        # axis ticks
        "axis": {
            "major_tick_line_color" : "#262626",
            "minor_tick_line_color" : "#a0a0a0",
            "minor_tick_out" : 2,
            "major_tick_out" : 5,
            "major_tick_in" : 0
        },

        #legend
        "legend":{
            "background_color" :'white',
            "text_color" : '#181818',
        },

        "widgets":{
            "background_color" : '#fcfcfc',
            "datatile_active_color": '#4292c6'
        }
    }
