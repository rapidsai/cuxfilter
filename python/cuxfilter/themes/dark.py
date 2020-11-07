from bokeh import palettes


class Theme:
    layout_head = """
`    {% extends base %}

    {% block head %}
    <head>
        {% block inner_head %}
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{% block title %}
            {{ title | e if title else "Panel App" }}{% endblock %}
        </title>
        {% block preamble %}{% endblock %}
        {% block resources %}
            {% block css_resources %}
            {{ bokeh_css | indent(8) if bokeh_css }}

            <link rel="stylesheet"
                href="https://unpkg.com/purecss@1.0.1/build/pure-min.css"
                integrity="sha384-oAOxQR6DkCoMliIh8yFnu25d7Eq/PHS21PClpwjOTeU2jRSq11vu66rf90/cZr47"
                crossorigin="anonymous">
            <link rel="stylesheet"
            href="https://unpkg.com/purecss@1.0.1/build/grids-responsive-min.css">

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
                    background-color: #181818;
                }

                nav {
                    display: inline-block;
                    vertical-align: top;
                    width: 18em;
                    height: calc(100vh - 2em);
                    padding: 1em;
                    background-color: #2c2b2b;
                    color: white;
                    border-right: 2px solid #353535;
                }

                .nav-title {
                    font-size: 1.5em;
                }

                .nav-container {
                    margin-top: 1em;
                    font-size: 1.04em !important;
                }

                .container {
                    display: inline-block;
                    width: calc(100vw - 23em);
                    padding-left: 0.5em;
                    height: 100vh;
                    color: #white;
                    background-color: #181818;
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
    """

    chart_properties = {
        "data_size_indicator_color": "#8735fb",
        "agg_charts_grids": {"xgrid": None, "ygrid": "#505050"},
        "geo_charts_grids": {"xgrid": None, "ygrid": None},
        "chart_color": {
            "color": "#8735fb",
            "color_palette": list(palettes.Purples[9]),
        },
        # title
        "title": {
            "text_color": "#a0a0a0",
            "text_font": "helvetica",
            "text_font_style": "bold",
            "text_font_size": "18px",
        },
        # background
        "background_fill_color": "#181818",
        "border_fill_color": "#181818",
        "min_border": 40,
        "outline_line_width": 0,
        "outline_line_alpha": 1,
        "outline_line_color": "#181818",
        # x axis title
        "xaxis": {
            "axis_label": "X Axis",
            "axis_label_text_font_style": "bold",
            "axis_label_text_color": "#a0a0a0",
            "axis_label_standoff": 15,
            "major_label_text_color": "#E2E2E2",
            "axis_line_width": 1,
            "axis_line_color": "#E2E2E2",
        },
        # y axis title
        "yaxis": {
            "axis_label": "Y Axis",
            "axis_label_text_font_style": "bold",
            "axis_label_text_color": "#a0a0a0",
            "axis_label_standoff": 15,
            "major_label_text_color": "#E2E2E2",
            "axis_line_width": 0,
            "axis_line_color": "#181818",
        },
        # axis ticks
        "axis": {
            "major_tick_line_color": "#E2E2E2",
            "minor_tick_line_color": "#A2A2A2",
            "minor_tick_out": 2,
            "major_tick_out": 5,
            "major_tick_in": 0,
        },
        # legend
        "legend": {"background_color": "#181818", "text_color": "#a0a0a0"},
        "widgets": {
            "background_color": "#2c2b2b",
            "datatile_active_color": "#8735fb",
        },
        "map_style": "dark",
    }
