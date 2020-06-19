import re

import pytest

# module under test
import cuxfilter.layouts.layout_templates as m

_roots = {
    "layout_0": 1,
    "layout_1": 2,
    "layout_2": 2,
    "layout_3": 3,
    "layout_4": 3,
    "layout_5": 3,
    "layout_6": 4,
    "layout_7": 4,
    "layout_8": 5,
    "layout_9": 6,
    "layout_10": 6,
    "layout_11": 6,
    "layout_12": 9,
}


@pytest.mark.parametrize("layout_name", list(_roots.keys()))
def test_template_embeds_expected_roots(layout_name):
    N = _roots[layout_name]
    embed_pat = re.compile(r"embed\(roots.chart\d?\)")
    layout = getattr(m, layout_name)

    # assert correct total number of root embeds
    assert len(embed_pat.findall(layout)) == N

    # assert every individual embed happens (once)
    for i in range(1, N):
        assert f"embed(roots.chart{i})" in layout


@pytest.mark.parametrize("layout_name", list(_roots.keys()))
def test_template_embeds_widgets(layout_name):
    embed_pat = re.compile(r"embed\(roots.widgets\)")
    layout = getattr(m, layout_name)

    # assert widgets embedded once
    assert len(embed_pat.findall(layout)) == 1


@pytest.mark.parametrize("layout_name", list(_roots.keys()))
def test_template_embeds_title(layout_name):
    embed_pat = re.compile(r"embed\(roots.title\)")
    layout = getattr(m, layout_name)

    # assert one title
    assert len(embed_pat.findall(layout)) == 1
