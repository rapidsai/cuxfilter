import panel as pn
import ipywidgets as widgets

out = widgets.Output(layout={"border": "1px solid black"})


def load_notebook_assets():
    with out:
        print("loading cuxfilter notebook assets ... ")
    pn.extension()
    out.clear_output()
    with out:
        print("cuxfilter notebook assets successfully loaded.")
