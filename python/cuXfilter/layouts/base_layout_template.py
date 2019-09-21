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
                width: 12em;
                height: calc(100vh - 2em);
                padding: 1em;
                background-color: #8735fb;
                color: white;
                border-right: 2px solid #724aa9;
            }

            .nav-title {
                font-size: 1.5em;
            }

            .nav-container {
                margin-top: 1em;
            }
            
            .container {
                display: inline-block;
                width: calc(100vw - 17em);
                padding-left: 1em;
                height: 100vh;
            }

            .vertical-3-center {
                margin-top: 184px; //900px height (1600/3 = 533 chart height)
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
