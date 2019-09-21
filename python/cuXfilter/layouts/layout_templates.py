from .base_layout_template import layout_head

layout_0 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1">
            {{ embed(roots.chart1) }}
        </div>
    </div>
</div>
{% endblock %}
'''

layout_1 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1">
            {{ embed(roots.chart1) }}
        </div>
    </div>
    <div class="pure-g">
        <div class="pure-u-1">
            {{ embed(roots.chart2) }}
        </div>
    </div>
</div>
{% endblock %}
'''

layout_2 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart2) }}
        </div>
    </div>
</div>
{% endblock %}
'''

layout_3 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
    
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-2">
            <div class="pure-u-1">
                {{ embed(roots.chart2) }}
            </div>
            <div class="pure-u-1">
                {{ embed(roots.chart3) }}
            </div>
        </div>
    </div>

</div>
{% endblock %}
'''

layout_4 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
</nav>
<div class="container">
    <div class="pure-g vertical-3-center" >
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart2) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart3) }}
        </div>
    </div>
</div>
{% endblock %}
'''


layout_5 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
    
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1">
            {{ embed(roots.chart1) }}
        </div>
    </div>
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart2) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart3) }}
        </div>
    </div>
</div>
{% endblock %}
'''



layout_6 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
    
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart2) }}
        </div>
    </div>
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart3) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart4) }}
        </div>
    </div>
</div>
{% endblock %}
'''


layout_7 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
    
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1">
            {{ embed(roots.chart1) }}
        </div>
    </div>
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart2) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart3) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart4) }}
        </div>
    </div>
</div>
{% endblock %}
'''


layout_8 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
    
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1">
            {{ embed(roots.chart1) }}
        </div>
    </div>
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-4">
            {{ embed(roots.chart2) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-4">
            {{ embed(roots.chart3) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-4">
            {{ embed(roots.chart4) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-4">
            {{ embed(roots.chart5) }}
        </div>
    </div>
</div>
{% endblock %}
'''


layout_9 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
    
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-3-4">
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-4">
            <div class="pure-u-1">
                {{ embed(roots.chart2) }}
            </div>
            <div class="pure-u-1">
                {{ embed(roots.chart3) }}
            </div>
        </div>
    </div>
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart4) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart5) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart6) }}
        </div>
    </div>
</div>
{% endblock %}
'''


layout_10 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
    
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart2) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart3) }}
        </div>
    </div>
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart4) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart5) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart6) }}
        </div>
    </div>
</div>
{% endblock %}
'''


layout_11 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
    
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-2">
            {{ embed(roots.chart2) }}
        </div>
        
    </div>
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-4">
            {{ embed(roots.chart3) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-4">
            {{ embed(roots.chart4) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-4">
            {{ embed(roots.chart5) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-4">
            {{ embed(roots.chart6) }}
        </div>
    </div>
</div>
{% endblock %}
'''


layout_12 = layout_head + '''
<!-- goes in body -->
{% block contents %}
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> Widgets </div>
    
</nav>
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart2) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart3) }}
        </div>
    </div>
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart4) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart5) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart6) }}
        </div>
    </div>
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart7) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart8) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-3">
            {{ embed(roots.chart9) }}
        </div>
    </div>
</div>
{% endblock %}
'''