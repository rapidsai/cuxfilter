# Note: curly braces for Jinja must be escaped in format string
_content = """
{{% block contents %}}
{nav}
{layout}
{{% endblock %}}
"""

_nav = """
<nav>
    {{embed(roots.title)}}
    <div class="nav-container"> {{ embed(roots.widgets) }} </div>
</nav>
"""

_layout_0 = """
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1">
            {{ embed(roots.chart1) }}
        </div>
    </div>
</div>
"""
layout_0 = _content.format(nav=_nav, layout=_layout_0)


_layout_1 = """
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
"""
layout_1 = _content.format(nav=_nav, layout=_layout_1)


_layout_2 = """
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-1-2" >
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-1-2" >
            {{ embed(roots.chart2) }}
        </div>
    </div>
</div>
"""
layout_2 = _content.format(nav=_nav, layout=_layout_2)


_layout_3 = """
<div class="container">
    <div class="pure-g">
        <div class="pure-u-1 pure-u-md-3-5">
            {{ embed(roots.chart1) }}
        </div>
        <div class="pure-u-1 pure-u-md-2-5" style="align-self:center">
            <div class="pure-u-1">
                {{ embed(roots.chart2) }}
            </div>
            <div class="pure-u-1">
                {{ embed(roots.chart3) }}
            </div>
        </div>
    </div>
</div>
"""
layout_3 = _content.format(nav=_nav, layout=_layout_3)


_layout_4 = """
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
"""
layout_4 = _content.format(nav=_nav, layout=_layout_4)


_layout_5 = """
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
"""
layout_5 = _content.format(nav=_nav, layout=_layout_5)


_layout_6 = """
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
"""
layout_6 = _content.format(nav=_nav, layout=_layout_6)


_layout_7 = """
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
"""
layout_7 = _content.format(nav=_nav, layout=_layout_7)


_layout_8 = """
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
"""
layout_8 = _content.format(nav=_nav, layout=_layout_8)


_layout_9 = """
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
"""
layout_9 = _content.format(nav=_nav, layout=_layout_9)


_layout_10 = """
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
"""
layout_10 = _content.format(nav=_nav, layout=_layout_10)


_layout_11 = """
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
"""
layout_11 = _content.format(nav=_nav, layout=_layout_11)


_layout_12 = """
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
"""
layout_12 = _content.format(nav=_nav, layout=_layout_12)
