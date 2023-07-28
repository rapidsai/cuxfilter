import panel as pn

css = """
.bk-input-group {
  padding: 10px;
}
"""


def load_notebook_assets():
    pn.extension("deckgl", design="bootstrap")
    pn.config.raw_css += [css]
